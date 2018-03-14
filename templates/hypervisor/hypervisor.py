from js9 import j
from zerorobot.template.base import TemplateBase


class Hypervisor(TemplateBase):

    version = '0.0.1'
    template_name = 'hypervisor'

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._validate_input()

    def _validate_input(self):
        if not self.data.get('node'):
            raise ValueError("invalid input, node can't be None")

    @property
    def node_sal(self):
        """
        connection to the zos node
        """
        return j.clients.zero_os.sal.node_get(self.data['node'])

    def create(self, media=None, flist=None, cpu=2, memory=512, nics=None, port=None, mount=None, tags=None):
        self.logger.info('Creating hypervisor %s' % self.name)
        resp = self.node_sal.client.kvm.create(name=self.name,
                                               media=media,
                                               flist=flist,
                                               cpu=cpu,
                                               memory=memory,
                                               nics=nics,
                                               port=port,
                                               mount=mount,
                                               tags=tags)
        self.data['uid'] = resp.data[1:-1]
        self.state.set('actions', 'create', 'ok')

    def destroy(self):
        self.logger.info('Destroying hypervisor %s' % self.name)
        self.state.check('actions', 'create', 'ok')
        self.node_sal.client.kvm.destroy(self.data['uid'])
        del self.data['uid']
        self.state.delete('actions', 'create')

    def shutdown(self):
        self.logger.info('Shuting down hypervisor %s' % self.name)
        self.state.check('actions', 'create', 'ok')
        self.node_sal.client.kvm.shutdown(self.data['uid'])

    def pause(self):
        self.logger.info('Pausing hypervisor %s' % self.name)
        self.state.check('actions', 'create', 'ok')
        self.node_sal.client.kvm.pause(self.data['uid'])

    def resume(self):
        self.logger.info('Resuming hypervisor %s' % self.name)
        self.state.check('actions', 'create', 'ok')
        self.node_sal.client.kvm.resume(self.data['uid'])

    def reboot(self):
        self.logger.info('Rebooting hypervisor %s' % self.name)
        self.state.check('actions', 'create', 'ok')
        self.node_sal.client.kvm.reboot(self.data['uid'])

    def reset(self):
        self.logger.info('Resetting hypervisor %s' % self.name)
        self.state.check('actions', 'create', 'ok')
        self.node_sal.client.kvm.reset(self.data['uid'])
