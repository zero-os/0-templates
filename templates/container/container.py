from zerorobot.template.base import TemplateBase
from js9 import j


NODE_TEMPLATE_UID = 'github.com/zero-os/0-templates/node/0.0.1'


class Container(TemplateBase):

    version = '0.0.1'
    template_name = "container"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._validate_input()
        self._node = None

    def _validate_input(self):
        for param in ['node', 'flist']:
            if not self.data[param]:
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))

    @property
    def node_sal(self):
        if self._node is None:
            self._node = j.clients.zero_os.sal.node_get(self.data['node'])
        return self._node

    @property
    def container_sal(self):
        try:
            return self.node_sal.containers.get(self.name)
        except LookupError:
            return self.install()

    def install(self):
        node_name = self.data['node']
        nodes = self.api.services.find(name=node_name, template_uid=NODE_TEMPLATE_UID)
        if not nodes:
            raise RuntimeError("service for node {} does'nt exist".format(node_name))

        self.api.services.names[node_name].state.check('actions', 'install', 'ok')

        if self.node_sal is None:
            raise RuntimeError("no connection to the zero-os node")

        container_sal = self.node_sal.containers.create(self.name, self.data['flist'], hostname=None,
                                                        mounts=None, nics=None, host_network=False,
                                                        ports=None, storage=None, init_processes=None,
                                                        privileged=False, env=None)
        self.state.set('actions', 'install', 'ok')
        return container_sal

    def start(self, node_name=None):
        if node_name and self.data['node'] != node_name:
            return

        self.state.check('actions', 'install', 'ok')
        print('starting %s' % self.name)
        self.container_sal.start()
        self.state.set('actions', 'start', 'ok')

    def stop(self, node_name=None):
        if node_name and self.data['node'] != node_name:
            return

        self.state.check('actions', 'start', 'ok')
        print('stopping %s' % self.name)
        self.container_sal.stop()
        self.state.delete('actions', 'start')
