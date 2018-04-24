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
        if not self.data.get('flist'):
            raise ValueError("invalid input. Vm requires flist to be specifed.")

    @property
    def _hypervisor_sal(self):
        return self._node_sal.hypervisor.get(self.data['uuid'])

    @property
    def _node_sal(self):
        """
        connection to the zos node
        """
        return j.clients.zero_os.sal.get_node(NODE_CLIENT)

    def _monitor(self):
        self.logger.info('Monitor vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')

        if self._hypervisor_sal.is_running():
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
        configs = {}
        for config in self.data['configs']:
            configs[config['path']] = config['content']

        args = {
            'name': self.name,
            'media': self.data['media'],
            'flist': self.data['flist'],
            'cpu': self.data['cpu'],
            'memory': self.data['memory'],
            'nics': self.data['nics'],
            'ports': self.data['ports'],
            'mounts': self.data.get('mount'),
            'tags': self.data.get('tags'),
            'config': configs,
        }
        self.data['uuid'] = self._node_sal.hypervisor.create(**args).uuid
        self.state.set('actions', 'install', 'ok')
        self.state.set('status', 'running', 'ok')

    def uninstall(self):
        self.logger.info('Uninstalling vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._hypervisor_sal.destroy(self.data['ports'])
        self.state.delete('actions', 'install')

    def shutdown(self):
        self.logger.info('Shuting down vm %s' % self.name)
        self.state.check('status', 'running', 'ok')
        self._hypervisor_sal.shutdown(self.data['ports'])
        self.state.delete('status', 'running')
        self.state.set('status', 'shutdown', 'ok')

    def pause(self):
        self.logger.info('Pausing vm %s' % self.name)
        self.state.check('status', 'running', 'ok')
        self._hypervisor_sal.pause()
        self.state.delete('status', 'running')
        self.state.set('actions', 'pause', 'ok')

    def resume(self):
        self.logger.info('Resuming vm %s' % self.name)
        self.state.check('actions', 'pause', 'ok')
        self._hypervisor_sal.resume()
        self.state.delete('actions', 'pause')
        self.state.set('status', 'running', 'ok')

    def reboot(self):
        self.logger.info('Rebooting vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._hypervisor_sal.reboot()
        self.state.set('status', 'rebooting', 'ok')

    def reset(self):
        self.logger.info('Resetting vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._hypervisor_sal.reset()

    def enable_vnc(self):
        self.logger.info('Enable vnc for vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self._hypervisor_sal.enable_vnc()
        self.state.set('vnc', self._hypervisor_sal.info['vnc'], 'ok')

    def disable_vnc(self):
        self.logger.info('Disable vnc for vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.state.check('vnc', self._hypervisor_sal.info['vnc'], 'ok')
        self._hypervisor_sal.disable_vnc()
        self.state.delete('vnc', self._hypervisor_sal.info['vnc'])
