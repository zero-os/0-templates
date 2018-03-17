from js9 import j

from zerorobot.template.base import TemplateBase
import netaddr


CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
OVS_FLIST = 'https://hub.gig.tech/gig-official-apps/ovs.flist'


class Network(TemplateBase):

    version = '0.0.1'
    template_name = "network"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    def validate(self):
        for x in ['cidr', 'vlanTag']:
            if not self.data.get(x):
                raise ValueError("%s need to be specified in the data")
        if 'bonded' not in self.data:
            self.data['bonded'] = False

    def _ensure_ovs_container(self, node_name):
        container_data = {
            'node': node_name,
            'hostname': 'ovs',
            'flist': OVS_FLIST,
            'hostNetworking': True,
            'privileged': True,
        }
        container_name = 'container_%s_ovs' % node_name
        container = self.api.services.find_or_create(CONTAINER_TEMPLATE_UID, container_name, data=container_data)
        container.schedule_action('install').wait(die=True)
        return container_name

    def configure(self, node_name):
        node_sal = j.clients.zero_os.sal.node_get(node_name)

        self.logger.info("install OpenVSwitch container")
        container_name = self._ensure_ovs_container(node_name)

        if self.data.get('driver'):
            self.logger.info("reload driver %s" % self.data['driver'])
            node_sal.network.reload_driver(self.data['driver'])

        self.logger.info("configure network: cidr: {cidr} - vlang tag: {vlanTag} - bonded:{bonded}".format(**self.data))
        node_sal.network.configure(
            cidr=self.data['cidr'],
            vlan_tag=self.data['vlanTag'],
            ovs_container_name=container_name,
            bonded=self.data.get('bonded', False),
        )
