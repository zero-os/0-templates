from zerorobot.template.base import TemplateBase
from js9 import j


class Container(TemplateBase):

    version = '0.0.1'
    template_name = "container"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._node = None

    @property
    def node(self):
        if self._node is None:
            self._node = j.clients.zero_os.sal.node_get(self.parent.name)
        return self._node

    @property
    def container_client(self):
        try:
            return self.node.containers.get(self.name)
        except LookupError:
            return self.install()

    def install(self):
        if self.node is None:
            raise RuntimeError("no connextion to the zero-os node")

        container = self.node.containers.create(self.name, self.data['flist'], hostname=None, mounts=None, nics=None,
                                                host_network=False, ports=None, storage=None, init_processes=None,
                                                privileged=False, env=None)
        self.state.set('actions', 'installed', 'ok')
        return container

    def start(self):
        print('starting %s' % self.name)
        self.container_client.start()
        self.state.set('actions', 'started', 'ok')

    def stop(self):
        print('stopping %s' % self.name)
        self.container_client.stop()
        self.state.delete('actions', 'started')
