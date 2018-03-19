from zerorobot.template.base import TemplateBase
from js9 import j


NODE_TEMPLATE_UID = 'github.com/zero-os/0-templates/node/0.0.1'


class Container(TemplateBase):

    version = '0.0.1'
    template_name = "container"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._validate_input()

    def _validate_input(self):
        for param in ['node', 'flist']:
            if not self.data[param]:
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))

    @property
    def node_sal(self):
        return j.clients.zero_os.sal.node_get(self.data['node'])

    @property
    def container_sal(self):
        try:
            return self.node_sal.containers.get(self.name)
        except LookupError:
            self.install()
            return self.node_sal.containers.get(self.name)

    def install(self):
        node_name = self.data['node']
        node = self.api.services.get(name=node_name, template_uid=NODE_TEMPLATE_UID)
        node.state.check('status', 'running', 'ok')

        if self.node_sal is None:
            raise RuntimeError("no connection to the zero-os node")

        # convert "src:dst" to {src:dst}
        ports = j.clients.zero_os.sal.format_ports(self.data['ports'])

        mounts = {}
        for mount in self.data['mounts']:
            mounts[mount['source']] = mount['target']

        envs = {}
        for env in self.data['env']:
            envs[env['name']] = env['value']

        self.node_sal.containers.create(self.name, self.data['flist'], hostname=self.data['hostname'],
                                        mounts=mounts, nics=self.data['nics'],
                                        host_network=self.data['hostNetworking'],
                                        ports=ports, storage=self.data['storage'],
                                        init_processes=self.data['initProcesses'],
                                        privileged=self.data['privileged'], env=envs)
        self.state.set('actions', 'install', 'ok')
        self.state.set('actions', 'start', 'ok')

    def start(self, node_name=None):
        if node_name and self.data['node'] != node_name:
            return

        self.state.check('actions', 'install', 'ok')
        self.logger.info('Starting container %s' % self.name)
        self.container_sal.start()
        self.state.set('actions', 'start', 'ok')

    def stop(self, node_name=None):
        if node_name and self.data['node'] != node_name:
            return

        self.state.check('actions', 'install', 'ok')
        self.logger.info('Stopping container %s' % self.name)
        self.container_sal.stop()
        self.state.delete('actions', 'start')

    def uninstall(self):
        self.logger.info('Uninstalling container %s' % self.name)
        self.stop()
        self.state.delete('actions', 'install')


