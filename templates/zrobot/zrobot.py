import os

from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError
from zerorobot.service_collection import ServiceNotFoundError

FLIST_ZROBOT = 'https://hub.gig.tech/gig-autobuilder/zero-os-0-robot-master-406382eb65.flist'
NODE_TEMPLATE = 'github.com/zero-os/0-templates/node/0.0.1'
CONTAINER_TEMPLATE = 'github.com/zero-os/0-templates/container/0.0.1'


class Zrobot(TemplateBase):

    version = '0.0.1'
    template_name = "zrobot"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self.recurring_action('_monitor', 30)  # every 30 seconds

    def validate(self):
        if not self.data['node']:
            raise ValueError("parameter node not valid: %s" % (str(self.data['node'])))

        # ensure the node service we depend on exists
        self.api.services.get(template_uid=NODE_TEMPLATE, name=self.data['node'])

    @property
    def node_sal(self):
        return j.clients.zero_os.sal.get_node(self.data['node'])

    @property
    def _container_name(self):
        return "container-%s" % self.guid

    def _get_container(self):
        ports = None
        nics = self.data.get('nics')
        if not nics:
            nics = [{'type': 'default'}]

            port = self.data.get('port')
            if not port:
                freeports = self.node_sal.freeports(baseport=6600, nrports=1)
                if not freeports:
                    raise RuntimeError("can't find a free port to expose the robot")
                self.data['port'] = freeports[0]

            ports = ['%s:6600' % self.data['port']]

        data = {
            'node': self.data['node'],
            'flist': FLIST_ZROBOT,
            'nics': nics,
            'hostname': self.name,
            'privileged': False,
            'ports': ports,
            'env': [
                {'name': 'LC_ALL', 'value': 'C.UTF-8'},
                {'name': 'LANG', 'value': 'C.UTF-8'}
            ]
        }

        sp = self.node_sal.storagepools.get('zos-cache')
        try:
            fs = sp.get(self.guid)
        except ValueError:
            fs = sp.create(self.guid)

        # prepare persistant volume to mount into the container
        node_fs = self.node_sal.client.filesystem
        ssh_vol = os.path.join(fs.path, 'ssh')
        data_vol = os.path.join(fs.path, 'zrobot_data')
        config_vol = os.path.join(fs.path, 'config')
        jsconfig_vol = os.path.join(fs.path, 'jsconfig')
        for vol in [ssh_vol, data_vol, config_vol, jsconfig_vol]:
            node_fs.mkdir(vol)

        data['mounts'] = [
            {'source': data_vol,
             'target': '/opt/code/zrobot/zrobot_data'},
            {'source': config_vol,
             'target': '/opt/code/zrobot/config'},
            {'source': ssh_vol,
             'target': '/root/.ssh'},
            {'source': jsconfig_vol,
             'target': '/js9host/cfg'},
            {'source': '/var/run/redis.sock',  # mount zero-os redis socket into container, so the robot can talk to the os directly
             'target': '/tmp/redis.sock'}
        ]

        return self.api.services.find_or_create(CONTAINER_TEMPLATE, self._container_name, data)
    
    @property
    def zrobot_sal(self):
        container_sal = self.node_sal.containers.get(self._container_name)
        return j.clients.zero_os.sal.get_zerorobot(container=container_sal, port=6600, template_repos=self.data['templates'], organization=(self.data.get('organization') or None))

    def install(self, force=False):
        try:
            self.state.check('actions', 'install', 'ok')
            if not force:
                return
        except StateCheckError:
            pass

        container = self._get_container()
        container.schedule_action('install').wait(die=True)

        self.zrobot_sal.start()
        self.state.set('actions', 'install', 'ok')
        self.state.set('actions', 'start', 'ok')
        self.state.set('status', 'running', 'ok')

    def start(self):
        container = self._get_container()
        container.schedule_action('start').wait(die=True)

        self.zrobot_sal.start()
        self.state.set('actions', 'start', 'ok')
        self.state.set('status', 'running', 'ok')

    def stop(self):
        self.state.check('actions', 'start', 'ok')
        try:
            self.zrobot_sal.stop()
        except (ServiceNotFoundError, LookupError):
            pass
        self.state.delete('actions', 'start')
        self.state.delete('status', 'running')

    def uninstall(self):
        self.state.check('actions', 'install', 'ok')
        try:
            container = self.api.services.get(name=self._container_name)
            self.zrobot_sal.stop()
            container.schedule_action('uninstall').wait(die=True)
            container.delete()
        except (ServiceNotFoundError, LookupError):
            pass

        try:
            # cleanup filesystem used by this robot
            storagepool_sal = self.node_sal.storagepools.get('zos-cache')
            fs_sal = storagepool_sal.get(self.guid)
            fs_sal.delete()
        except ValueError:
            # filesystem doesn't exist, nothing else to do
            pass

        self.state.delete('actions', 'install')
        self.state.delete('status', 'running')

    def _monitor(self):
        self.state.check('actions', 'install', 'ok')
        self.state.check('actions', 'start', 'ok')

        try:
            self.api.services.get(name=self._container_name) # check that container service exists
            if self.zrobot_sal and self.zrobot_sal.is_running():
                self.state.set('status', 'running', 'ok')
                return
        except (ServiceNotFoundError, LookupError):
            self.state.delete('status', 'running')

        # try to start
        self.start()
