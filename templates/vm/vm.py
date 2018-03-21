from js9 import j
from zerorobot.template.base import TemplateBase

NODE_TEMPLATE_UID = "github.com/zero-os/0-templates/node/0.0.1"
HV_TEMPLATE = 'github.com/zero-os/0-templates/hypervisor/0.0.1'


class Vm(TemplateBase):

    version = '0.0.1'
    template_name = "vm"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    def validate(self):
        if not self.data.get('node'):
            raise ValueError("invalid input, node can't be None")

        vdisks = self.data.get('vdisks')
        flist = self.data.get('flist')
        if not vdisks and not flist:
            raise ValueError("invalid input. Vm requires a vdisk or flist to be specifed.")

    @property
    def node_sal(self):
        """
        connection to the zos node
        """
        return j.clients.zero_os.sal.node_get(self.data['node'])

    def install(self):
        self.logger.info('Installing vm %s' % self.name)
        node_name = self.data['node']
        node = self.api.services.get(name=node_name, template_uid=NODE_TEMPLATE_UID)
        node.state.check('actions', 'install', 'ok')
        node.state.check('status', 'running', 'ok')
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
        # TODO: deal with vdisks
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
