from js9 import j
from zerorobot.template.base import TemplateBase

NODE_TEMPLATE_UID = "github.com/zero-os/0-templates/node/0.0.1"
HV_TEMPLATE = 'github.com/zero-os/0-templates/hypervisor/0.0.1'
NODE_CLIENT = 'local'


class Vm(TemplateBase):

    version = '0.0.1'
    template_name = "vm"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    def validate(self):
        if not self.data.get('flist'):
            raise ValueError("invalid input. Vm requires flist to be specifed.")

    @property
    def node_sal(self):
        """
        connection to the zos node
        """
        return j.clients.zero_os.sal.get_node(NODE_CLIENT)

    def install(self):
        self.logger.info('Installing vm %s' % self.name)
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
        }
        self.data['uuid'] = self.node_sal.hypervisor.create(**args).uuid
        self.state.set('actions', 'install', 'ok')

    def uninstall(self):
        self.logger.info('Uninstalling vm %s' % self.name)
        if self.data.get('uuid'):
            self.node_sal.hypervisor.get(self.data['uuid']).destroy()

    def shutdown(self):
        self.logger.info('Shuting down vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.node_sal.hypervisor.get(self.data['uuid']).shutdown()

    def pause(self):
        self.logger.info('Pausing vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.node_sal.hypervisor.get(self.data['uuid']).pause()

    def resume(self):
        self.logger.info('Resuming vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.node_sal.hypervisor.get(self.data['uuid']).resume()

    def reboot(self):
        self.logger.info('Rebooting vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.node_sal.hypervisor.get(self.data['uuid']).reboot()

    def reset(self):
        self.logger.info('Resetting vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.node_sal.hypervisor.get(self.data['uuid']).reset()

    def enable_vnc(self):
        self.logger.info('Enable vnc for vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.node_sal.hypervisor.get(self.data['uuid']).enable_vnc()

    def disable_vnc(self):
        self.logger.info('Disable vnc for vm %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.node_sal.hypervisor.get(self.data['uuid']).disable_vnc()
