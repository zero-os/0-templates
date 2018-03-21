import ast
from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError


#Temporary flist needs to be updated to offical 0-robot flist
FLIST_ZROBOT = 'https://hub.gig.tech/fastgeert/jumpscale-0-robot-latest.flist'
NODE_TEMPLATE = 'github.com/zero-os/0-templates/node/0.0.1'
CONTAINER_TEMPLATE = 'github.com/zero-os/0-templates/container/0.0.1'


class Zrobot(TemplateBase):

    version = '0.0.1'
    template_name = "zrobot"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._validate_input()
    
    def _validate_input(self):
        if not self.data['node']:
            raise ValueError("parameter node not valid: %s" % (str(self.data['node'])))

        self.api.services.get(template_uid=NODE_TEMPLATE, name=self.data['node'])

    @property
    def node_sal(self):
        return j.clients.zero_os.sal.node_get(self.data['node'])
    
    def _get_container(self):
        ports = None
        nics = self.data.get('nics')
        if not nics:
            nics = [{'type': 'default'}]
            ports = ['6600:6600']

        data = {
            'node': self.data['node'],
            'flist': FLIST_ZROBOT,
            'nics': nics,
            'hostname': self.name,
            'hostNetworking': False,
            'privileged': True,
            'ports': ports
        }
        return self.api.services.find_or_create(CONTAINER_TEMPLATE, self.name, data)

    def _get_zrobot_client(self, contservice):
        container = self.node_sal.containers.get(contservice.name)
        return j.clients.zero_os.sal.get_zerorobot(container=container)

    def install(self, force=False):
        try:
            self.state.check('actions', 'install', 'ok')
            if not force:
                return
        except StateCheckError:
            pass

        contservice = self._get_container()
        contservice.schedule_action('install').wait(die=True)

        zrobot_sal = self._get_zrobot_client(contservice)
        zrobot_sal.start(port=6600, template_repos=self.data['templates'])
        self.state.set('actions', 'install', 'ok')

    def uninstall(self):
        self.state.check('actions', 'install', 'ok')
        contservice = self._get_container()
        zrobot_sal = self._get_zrobot_client(contservice)
        zrobot_sal.stop()
        self.state.delete('actions', 'install')
        
