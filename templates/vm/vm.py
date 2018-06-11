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
        self.state.check('actions', 'start', 'ok')

        if not self._vm_sal.is_running():
            self._vm_sal.deploy()
            if self._vm_sal.is_running():
                self.state.set('status', 'running', 'ok')

                # handle reboot
                try:
                    self.state.check('status', 'rebooting', 'ok')
                    self.state.delete('status', 'rebooting')
                except StateCheckError:
                    pass

            else:
                self.state.delete('status', 'running')

    def install(self):
        self.logger.info('Installing vm %s' % self.name)
        vm_sal = self._vm_sal
        vm_sal.deploy()
        self.data['uuid'] = vm_sal.uuid
        self.data['ztIdentity'] = vm_sal.zt_identity
        self.state.set('actions', 'install', 'ok')
        self.state.set('actions', 'start', 'ok')
        self.state.set('status', 'running', 'ok')

    def uninstall(self):
        self.logger.info('Uninstalling vm %s' % self.name)
        self._vm_sal.destroy()
        self.state.delete('actions', 'install')
        self.state.delete('actions', 'start')
        self.state.delete('status', 'running')

    def shutdown(self, force=False):
        self.logger.info('Shuting down vm %s' % self.name)
        self.state.check('status', 'running', 'ok')
        if force is False:
            self._vm_sal.shutdown()
        else:
            self._vm_sal.destroy()
        self.state.delete('status', 'running')
        self.state.delete('actions', 'start')

    def pause(self):
        self.logger.info('Pausing vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.state.check('status', 'running', 'ok')
        self._vm_sal.pause()
        self.state.delete('status', 'running')
        self.state.delete('actions', 'start')
        self.state.set('actions', 'pause', 'ok')

    def start(self):
        self.logger.info('Starting vm {}'.format(self.name))
        self.state.check('actions', 'install', 'ok')
        self._vm_sal.deploy()
        self.state.set('status', 'running', 'ok')
        self.state.set('actions', 'start', 'ok')

    def resume(self):
        self.logger.info('Resuming vm %s' % self.name)
        self.state.check('actions', 'pause', 'ok')
        self._vm_sal.resume()
        self.state.delete('actions', 'pause')
        self.state.set('status', 'running', 'ok')
        self.state.set('actions', 'start', 'ok')

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

    def info(self):
        info = self._vm_sal.info or {}
        return {
            'vnc': info.get('vnc'),
            'status': info.get('state', 'halted'),
            'disks': self.data['disks'],
            'nics': self.data['nics'],
            'ztIdentity': self.data.get('ztIdentity')
        }
