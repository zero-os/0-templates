from js9 import j
from zerorobot.template.base import TemplateBase


class Vm(TemplateBase):

    version = '0.0.1'
    template_name = "vm"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self.hv_name = "hv_%s" % self.guid
        self._node = None
        self._hypervisor = None
        self._validate_input()

    def _validate_input(self):
        if not self.data.get('node'):
            raise ValueError("invalid input, node can't be None")

        vdisks = self.data.get('vdisks')
        flist = self.data.get('flist')
        if not vdisks and not flist:
            raise ValueError("invalid input. Vm requires or a vdisk or flist to be specifed.")

    @property
    def node(self):
        """
        connection to the zos node
        """
        if self._node is None:
            self._node = j.clients.zero_os.sal.node_get(self.data['node'])
        return self._node

    @property
    def hypervisor(self):
        if self._hypervisor is None:
            if self.hv_name in self.api.services.names:
                self._hypervisor = self.api.services.names[self.hv_name]
        return self._hypervisor

    def install(self):
        HV_TEMPLATE = 'github.com/zero-os/0-templates/hypervisor/0.0.1'
        data = {
            'node': self.node.name,
            'vm': self.name,
        }

        self._hypervisor = self.api.services.create(template_uid=HV_TEMPLATE, service_name=self.hv_name, data=data)

        port = {int(k): int(v) for k, v in self.data.get('port', {}).items()}
        args = {
            # 'media': self.data['vdisks'],
            'flist': self.data['flist'],
            'cpu': self.data['cpu'],
            'memory': self.data['memory'],
            'nics': self.data['nics'],
            'port': port,
            # 'mount': self.data['mount'],
            # 'tags': self.data['tags']
        }

        t = self._hypervisor.schedule_action('create', args)
        t.wait()
        if t.state != 'ok':
            # cleanup if hypervisor failed to start
            if self._hypervisor.guid in self.api.services.guids:
                self.api.services.guids[self._hypervisor.guid].delete()
                self._hypervisor = None
            raise RuntimeError("error during creation of the hypervisor: %s", t.eco.errormessage)

    def uninstall(self):
        if not self.hypervisor:
            return

        # TODO: deal with vdisks
        self.hypervisor.schedule_action('destroy')
        self.hypervisor.delete()
        self._hypervisor = None

    def shutdown(self):
        if not self.hypervisor:
            return
        self.hypervisor.schedule_action('shutdown')

    def pause(self):
        if not self.hypervisor:
            return
        self.hypervisor.schedule_action('pause')

    def resume(self):
        if not self.hypervisor:
            return
        self.hypervisor.schedule_action('resume')

    def reboot(self):
        if not self.hypervisor:
            return
        self.hypervisor.schedule_action('reboot')

    def reset(self):
        if not self.hypervisor:
            return
        self.hypervisor.schedule_action('reset')

    def _get_vnc_port(self):
        # Fix me: client.kvm should provide a way to get
        # the info without listing all vms
        if not self.hypervisor:
            return None

        for vm in self.node.client.kvm.list():
            if vm['name'] == self.hv_name:
                return vm['vnc']

    def enable_vnc(self):
        port = self._get_vnc_port()
        if port:
            self.node.client.nft.open_port(port)

    def disable_vnc(self):
        port = self._get_vnc_port()
        if port:
            self.node.client.nft.drop_port(port)
