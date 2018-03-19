from js9 import j
from zerorobot.template.base import TemplateBase

NODE_TEMPLATE_UID = "github.com/zero-os/0-templates/node/0.0.1"
HV_TEMPLATE = 'github.com/zero-os/0-templates/hypervisor/0.0.1'


class Vm(TemplateBase):

    version = '0.0.1'
    template_name = "vm"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self.hv_name = "hv_%s" % self.guid
        self._hypervisor = None
        self._validate_input()

    def _validate_input(self):
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

    @property
    def hypervisor(self):
        if self._hypervisor is None:
            self._hypervisor = self.api.services.get(name=self.hv_name, template_uid=HV_TEMPLATE)
        return self._hypervisor

    def install(self):
        self.logger.info('Installing vm %s' % self.name)
        node_name = self.data['node']
        node = self.api.services.get(name=node_name, template_uid=NODE_TEMPLATE_UID)
        node.state.check('actions', 'install', 'ok')

        data = {
            'node': self.node_sal.name,
            'vm': self.name,
        }

        self._hypervisor = self.api.services.create(template_uid=HV_TEMPLATE, service_name=self.hv_name, data=data)
        args = {
            'media': self.data['media'],
            'flist': self.data['flist'],
            'cpu': self.data['cpu'],
            'memory': self.data['memory'],
            'nics': self.data['nics'],
            'port': j.clients.zero_os.sal.format_ports(self.data['ports']),
            # 'tags': self.data['tags']
        }

        t = self._hypervisor.schedule_action('create', args)
        t.wait(die=True)
        if t.state != 'ok':
            # cleanup if hypervisor failed to start
            if self._hypervisor.guid in self.api.services.guids:
                self.api.services.guids[self._hypervisor.guid].delete()
                self._hypervisor = None
            raise RuntimeError("error during creation of the hypervisor: %s", t.eco.errormessage)

    def uninstall(self):
        self.logger.info('Uninstalling vm %s' % self.name)
        # TODO: deal with vdisks
        self.hypervisor.schedule_action('destroy').wait(die=True)
        self.hypervisor.delete()
        self._hypervisor = None

    def shutdown(self):
        self.logger.info('Shuting down vm %s' % self.name)
        self.hypervisor.schedule_action('shutdown')

    def pause(self):
        self.logger.info('Pausing vm %s' % self.name)
        self.hypervisor.schedule_action('pause')

    def resume(self):
        self.logger.info('Resuming vm %s' % self.name)
        self.hypervisor.schedule_action('resume')

    def reboot(self):
        self.logger.info('Rebooting vm %s' % self.name)
        self.hypervisor.schedule_action('reboot')

    def reset(self):
        self.logger.info('Resetting vm %s' % self.name)
        self.hypervisor.schedule_action('reset')

    def _get_vnc_port(self):
        # Fix me: client.kvm should provide a way to get
        # the info without listing all vms
        for vm in self.node_sal.client.kvm.list():
            if vm['name'] == self.hv_name:
                return vm['vnc']

    def enable_vnc(self):
        self.logger.info('Enable vnc for vm %s' % self.name)
        port = self._get_vnc_port()
        if port:
            self.node_sal.client.nft.open_port(port)

    def disable_vnc(self):
        self.logger.info('Disable vnc for vm %s' % self.name)
        port = self._get_vnc_port()
        if port:
            self.node_sal.client.nft.drop_port(port)
