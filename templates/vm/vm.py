from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError

NODE_CLIENT = 'local'


class Vm(TemplateBase):

    version = '0.0.1'
    template_name = "vm"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

        self.recurring_action('_monitor', 30)  # every 30 seconds

    def validate(self):
        if not (self.data['flist'] or self.data['ipxeUrl']):
            raise ValueError("invalid input. Vm requires flist or ipxeUrl to be specifed.")

    @property
    def _vm_sal(self):
        data = self.data.copy()
        data['name'] = self.name
        return self._node_sal.primitives.from_dict('vm', data)

    @property
    def _node_sal(self):
        """
        connection to the zos node
        """
        return j.clients.zos.sal.get_node(NODE_CLIENT)

    def _monitor(self):
        self.logger.info('Monitor vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')

        if self._vm_sal.is_running():
            self.state.set('status', 'running', 'ok')
            try:
                self.state.check('status', 'rebooting', 'ok')
                self.state.delete('status', 'rebooting')
            except StateCheckError:
                pass

            try:
                self.state.check('status', 'shutdown', 'ok')
                self.state.delete('status', 'shutdown')
            except StateCheckError:
                pass
        else:
            self.state.delete('status', 'running')

    def install(self):
        self.logger.info('Installing vm %s' % self.name)
        vm_sal = self._vm_sal
        vm_sal.deploy()
        self.data['uuid'] = vm_sal.uuid
        self.state.set('actions', 'install', 'ok')
        self.state.set('status', 'running', 'ok')

    def uninstall(self):
        self.logger.info('Uninstalling vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._vm_sal.destroy()
        self.state.delete('actions', 'install')
        self.state.delete('status', 'running')

    def shutdown(self):
        self.logger.info('Shuting down vm %s' % self.name)
        self.state.check('status', 'running', 'ok')
        self._vm_sal.shutdown()
        self.state.delete('status', 'running')
        self.state.set('status', 'shutdown', 'ok')

    def pause(self):
        self.logger.info('Pausing vm %s' % self.name)
        self.state.check('status', 'running', 'ok')
        self._vm_sal.pause()
        self.state.delete('status', 'running')
        self.state.set('actions', 'pause', 'ok')

    def resume(self):
        self.logger.info('Resuming vm %s' % self.name)
        self.state.check('actions', 'pause', 'ok')
        self._vm_sal.resume()
        self.state.delete('actions', 'pause')
        self.state.set('status', 'running', 'ok')

    def reboot(self):
        self.logger.info('Rebooting vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._vm_sal.reboot()
        self.state.set('status', 'rebooting', 'ok')

    def reset(self):
        self.logger.info('Resetting vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._vm_sal.reset()

    def enable_vnc(self):
        self.logger.info('Enable vnc for vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._vm_sal.enable_vnc()

    def disable_vnc(self):
        self.logger.info('Disable vnc for vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.state.check('vnc', self._vm_sal.info['vnc'], 'ok')
        self._vm_sal.disable_vnc()
