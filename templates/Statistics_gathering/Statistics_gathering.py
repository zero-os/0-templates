import os
import datetime
import json
from js9 import j
from zerorobot.service_collection import ServiceNotFoundError
from zerorobot.template.base import TemplateBase
from zerorobot.template.decorator import retry
from zerorobot.template.state import StateCheckError
from zerorobot.template.decorator import timeout

class StatisticsGathering(TemplateBase):
    version = '0.0.1'
    template_name = 'Statistics_gathering'

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._url_ = None
        self._node_ = None
        self.recurring_action('_monitor', 300) # every 5 minutes

    @property
    def _node(self):
        if not self._node_:
            try:
                self._node_ = self.api.services.get(template_account='zero-os', template_name='node')
            except ServiceNotFoundError:
                pass
        return self._node_            

    def start(self):
        self.state.set('status', 'running', 'ok')
        db=j.clients.influxdb.get('statistics-gathering', data={'database': 'statistics-gathering'})
        if 'statistics-gathering' not in db.get_list_database():
            db.create_database('statistics-gathering')
            db.switch_database('statistics-gathering')
        dashboard = self.setup_grafana_dashboard()
        self.logger.info("grafana dashboard URL=http://localhost:3000"+dashboard['url']+"\n")
        
    def stop(self):
        self.state.delete('status', 'running')

    @timeout(60, error_message='Monitor function call timed out')
    def _monitor(self):
        try:
            self.state.check('status', 'running', 'ok')
        except StateCheckError:
            return

        if self._node:
            stats_task = self._node.schedule_action('stats')

        if self._node:
            # Gather stats info
            stats_task.wait()
            if stats_task.state == 'ok':       
                db=j.clients.influxdb.get('statistics-gathering')
                for _, stat in stats_task.result.items():
                    points = stat['history']['300']
                    ps=[]
                    for point in points:
                        currentDT = datetime.datetime.now()
                        ps.append({"measurement": "statistics", "tags": point, "fields": {"Time": currentDT.strftime("%I:%M:%S %p")}})
                    db.write_points(ps, database='statistics-gathering')

    def setup_grafana_dashboard(self):
        parentdir = j.sal.fs.getParent(__file__)

        grafana_dashboard_json_file = j.sal.fs.joinPaths(parentdir, "grafana_dashboard.json")
        # dashboard_model_str = open(grafana_dashboard_json_file).read()
        dashboard_model = None
        with open(grafana_dashboard_json_file) as f:
            dashboard_model = json.load(f)

        if dashboard_model is None:
            return False
    
        grafancl = j.clients.grafana.get("statistics", data={"password_":"passwd","url":"http://localhost:3000","username":"admin"})
        

        data = {
            'type': 'influxdb', 
            'access': 'proxy', 
            'database': "statistics-gathering" , 
            'name': '', 
            'url': "http://localhost:3000", 
            'user': 'admin', 
            'password': 'passwd', 
            'default': True, 
        }
        grafancl.addDataSource(data)
        new_dashboard = grafancl.updateDashboard(dashboard_model)
        new_dashboard['panels_count'] = len(dashboard_model['panels'])
        return new_dashboard