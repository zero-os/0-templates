from js9 import j
from zerorobot.template.base import TemplateBase
from JumpScale9Lib.clients.zero_os.sal.gateway import Gateway as GatewaySal
import copy

CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
NODE_TEMPLATE_UID = 'github.com/zero-os/0-templates/node/0.0.1'
FLIST = 'https://hub.gig.tech/gig-official-apps/zero-os-gw-master.flist'
NODE_CLIENT = 'local'


class Gateway(TemplateBase):
    version = '0.0.1'
    template_name = "container"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._gw_sal = None

    def validate(self):
        GatewaySal.validate_input(self.data)

    @property
    def _node_sal(self):
        return j.clients.zero_os.sal.get_node(NODE_CLIENT)

    @property
    def _gateway_sal(self):
        if not self._gw_sal:
            self._gw_sal = self._node_sal.primitives.create_gateway(self.name)
        self._gw_sal.from_dict(self.data)
        return self._gw_sal

    def install(self):
        self._gateway_sal.deploy()
        self.data['identity'] = self._gateway_sal.identity
        self.state.set('actions', 'install', 'ok')
        self.state.set('actions', 'start', 'ok')

    def add_portforward(self, forward):
        for fw in self.data['portforwards']:
            if self._compare_objects(fw, forward, 'srcip', 'srcport'):
                if set(fw['protocols']).intersection(set(forward['protocols'])):
                    raise ValueError("Forward conflicts with existing forward")
        self.data['portforwards'].append(forward)
        self._gateway_sal().configure_fw()

    def remove_portforward(self, forward):
        for fw in self.data['portforwards']:
            if self._compare_objects(fw, forward, 'srcip', 'srcport'):
                if set(fw['protocols']).intersection(set(forward['protocols'])):
                    self.data['portforwards'].remove(fw)
                    break
        else:
            return
        self._gateway_sal().configure_fw()

    def add_http_proxy(self, proxy):
        for existing_proxy in self.data['httpproxies']:
            if self._compare_objects(existing_proxy, proxy, 'host'):
                raise ValueError("Proxy with host {} already exists".format(proxy['host']))
        self.data['httpproxies'].append(proxy)
        self._gateway_sal().configure_http()

    def remove_http_proxy(self, proxy):
        for existing_proxy in self.data['httpproxies']:
            if self._compare_objects(existing_proxy, proxy, 'host'):
                self.data['httpproxies'].remove(existing_proxy)
                break
        else:
            return
        self._gateway_sal.configure_http()

    def add_dhcp_host(self, nicname, host):
        for nic in self.data['nics']:
            if nic['name'] == nicname:
                break
        else:
            raise LookupError('Could not find NIC with name {}'.format(nicname))
        dhcpserver = nic['dhcpserver']
        for existing_host in dhcpserver['hosts']:
            if existing_host['macaddress'] == host['macaddress']:
                raise ValueError('Host with macaddress {} already exists'.format(host['macaddress']))
        dhcpserver['hosts'].append(host)
        self._gateway_sal.configure_dhcp()
        self._gateway_sal.configure_cloudinit()

    def remove_dhcp_host(self, nicname, host):
        for nic in self.data['nics']:
            if nic['name'] == nicname:
                break
        else:
            raise LookupError('Could not find NIC with name {}'.format(nicname))
        dhcpserver = nic['dhcpserver']
        for existing_host in dhcpserver['hosts']:
            if existing_host['macaddress'] == host['macaddress']:
                dhcpserver['hosts'].remove(existing_host)
                break
        else:
            return
        self._gateway_sal.configure_dhcp()

    def _compare_objects(self, obj1, obj2, *keys):
        for key in keys:
            if obj1[key] != obj2[key]:
                return False
        return True

    def add_nic(self, nic):
        for existing_nic in self.data['nics']:
            if self._compare_objects(existing_nic, nic, 'type', 'id'):
                raise ValueError('Nic with same type/id combination already exists')
        self._gateway_sal.deploy()

    def remove_nic(self, nicname):
        for nic in self.data['nics']:
            if nic['name'] == nicname:
                break
        else:
            return
        self._gateway_sal.deploy()

    def update_data(self, data):
        raise NotImplementedError('Not supported use actions instead')

    def uninstall(self):
        self._gateway_sal.stop()
        self.state.delete('actions', 'install')

    def stop(self):
        self._gateway_sal.stop()
        self.state.delete('actions', 'start')

    def start(self):
            self.install()
