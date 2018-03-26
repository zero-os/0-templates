from js9 import j
from zerorobot.template.base import TemplateBase
from JumpScale9Lib.clients.zero_os.sal.gateway import Gateway as GatewaySal
import copy

CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
NODE_TEMPLATE_UID = 'github.com/zero-os/0-templates/node/0.0.1'
FLIST = 'https://hub.gig.tech/gig-official-apps/zero-os-gw-master.flist'


class Gateway(TemplateBase):
    version = '0.0.1'
    template_name = "container"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    def validate(self):
        GatewaySal.validate_input(self.data)

    @property
    def node_sal(self):
        return j.clients.zero_os.sal.get_node(self.data['node'])

    def _get_gateway(self):
        container = self.node_sal.containers.get(self.name)
        return self.node_sal.gateways.get(container, self.data)

    def install(self):
        contnics = copy.deepcopy(self.data['nics'])
        for nic in contnics:
            nic.pop('dhcpserver', None)
            zerotierbridge = nic.pop('zerotierbridge', None)
            if zerotierbridge:
                contnics.append(
                    {
                        'id': zerotierbridge['id'], 'type': 'zerotier',
                        'name': 'z-{}'.format(nic['name']), 'token': zerotierbridge.get('token', '')
                    })
        containerdata = {
            'node': self.data['node'],
            'flist': FLIST,
            'nics': contnics,
            'hostname': self.data['hostname'],
            'hostNetworking': False,
            'privileged': True
        }
        contservice = self.api.services.find_or_create(CONTAINER_TEMPLATE_UID, self.name, containerdata)
        contservice.schedule_action('install').wait(die=True)
        gw = self._get_gateway()
        gw.install()
        self.state.set('actions', 'install', 'ok')

    def add_portforward(self, forward):
        for fw in self.data['portforwards']:
            if self._compare_objects(fw, forward, 'srcip', 'srcport'):
                if set(fw['protocols']).intersection(set(forward['protocols'])):
                    raise ValueError("Forward conflicts with existing forward")
        self.data['portforwards'].append(forward)
        self._get_gateway().configure_fw()

    def remove_portforward(self, forward):
        for fw in self.data['portforwards']:
            if self._compare_objects(fw, forward, 'srcip', 'srcport'):
                if set(fw['protocols']).intersection(set(forward['protocols'])):
                    self.data['portforwards'].remove(fw)
                    break
        else:
            return
        self._get_gateway().configure_fw()

    def add_http_proxy(self, proxy):
        for existing_proxy in self.data['httpproxies']:
            if self._compare_objects(existing_proxy, proxy, 'host'):
                raise ValueError("Proxy with host {} already exists".format(proxy['host']))
        self.data['httpproxies'].append(proxy)
        self._get_gateway().configure_http()

    def remove_http_proxy(self, proxy):
        for existing_proxy in self.data['httpproxies']:
            if self._compare_objects(existing_proxy, proxy, 'host'):
                self.data['httpproxies'].remove(existing_proxy)
                break
        else:
            return
        self._get_gateway().configure_http()

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
        gw = self._get_gateway()
        gw.configure_dhcp()
        gw.configure_cloudinit()

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
        self._get_gateway().configure_dhcp()

    def _compare_objects(self, obj1, obj2, *keys):
        for key in keys:
            if obj1[key] != obj2[key]:
                return False
        return True

    def add_nic(self, nic):
        for existing_nic in self.data['nics']:
            if self._compare_objects(existing_nic, nic, 'type', 'id'):
                raise ValueError('Nic with same type/id combination already exists')
        containernic = copy.deepcopy(nic)
        dhcpserver = containernic.pop('dhcpserver', None)
        zerotierbridge = containernic.pop('zerotierbridge', None)
        containernic.pop('token', None)
        contservice = self.api.services.find(CONTAINER_TEMPLATE_UID, self.name)
        contservice.schedule_action('add_nic', nic=containernic).wait(die=True)
        self.data['nics'].append(nic)
        gw = self._get_gateway()
        if zerotierbridge:
            gw.setup_zerotierbridges()
        if dhcpserver:
            gw.configure_dhcp()

    def remove_nic(self, nicname):
        for nic in self.data['nics']:
            if nic['name'] == nicname:
                break
        else:
            return
        gw = self._get_gateway()
        dhcpserver = nic.pop('dhcpserver', None)
        if nic.get('zerotierbridge'):
            gw.cleanup_zerotierbridge(nic)

        contservice = self.api.services.find(CONTAINER_TEMPLATE_UID, self.name)
        contservice.schedule_action('remove_nic', nicname=nicname).wait(die=True)
        self.data['nics'].append(nic)
        if dhcpserver:
            gw.configure_dhcp()

    def update_data(self, data):
        raise NotImplementedError('Not supported use actions instead')

    def uninstall(self):
        contservice = self.api.services.find(CONTAINER_TEMPLATE_UID, self.name)
        contservice.schedule_action('uninstall').wait(die=True)
        self.state.delete('actions', 'install')

    def stop(self):
        contservice = self.api.services.find(CONTAINER_TEMPLATE_UID, self.name)
        contservice.schedule_action('stop').wait(die=True)

    def start(self):
        self.install()

