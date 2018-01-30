from js9 import j
from zerorobot.template.base import TemplateBase


class Hypervisor(TemplateBase):

    version = '0.0.1'
    template_name = "hypervisor"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._node = None
        self._validate_input()

    def _validate_input(self):
        if not self.data.get('node'):
            raise ValueError("invalid input, node can't be None")

    @property
    def node(self):
        """
        connection to the zos node
        """
        if self._node is None:
            self._node = j.clients.zero_os.sal.node_get(self.data['node'])
            self._node.client.timeout = 60
        return self._node

    def create(self, media=None, flist=None, cpu=2, memory=512, nics=None, port=None, mount=None, tags=None):
        resp = self.node.client.kvm.create(name=self.name,
                                           media=media,
                                           flist=flist,
                                           cpu=cpu,
                                           memory=memory,
                                           nics=nics,
                                           port=port,
                                           mount=mount,
                                           tags=tags)
        self.data['uid'] = resp.data[1:-1]

    def destroy(self):
        if 'uid' not in self.data:
            return
        self.node.client.kvm.destroy(self.data['uid'])
        del self.data['uid']

    def shutdown(self):
        if 'uid' not in self.data:
            return
        self.node.client.kvm.shutdown(self.data['uid'])

    def pause(self):
        if 'uid' not in self.data:
            return
        self.node.client.kvm.pause(self.data['uid'])

    def resume(self):
        if 'uid' not in self.data:
            return
        self.node.client.kvm.resume(self.data['uid'])

    def reboot(self):
        if 'uid' not in self.data:
            return
        self.node.client.kvm.reboot(self.data['uid'])

    def reset(self):
        if 'uid' not in self.data:
            return
        self.node.client.kvm.reset(self.data['uid'])
