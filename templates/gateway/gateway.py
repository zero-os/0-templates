from js9 import j
from zerorobot.template.base import TemplateBase

NODE_CLIENT = 'local'


class Gateway(TemplateBase):
    version = '0.0.1'
    template_name = "gateway"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    def validate(self):
        if not self.data['hostname']:
            raise ValueError('Must supply a valid hostname')

    @property
    def _node_sal(self):
        return j.clients.zero_os.sal.get_node(NODE_CLIENT)

    @property
    def _gateway_sal(self):
        return self._node_sal.primitives.from_dict('gateway', self.data)

    def install(self):
        gateway_sal = self._gateway_sal
        gateway_sal.deploy()
        self.data['identity'] = gateway_sal.identity
        self.state.set('actions', 'install', 'ok')
        self.state.set('actions', 'start', 'ok')

    def add_portforward(self, forward):
        self.state.check('actions', 'start', 'ok')

        for fw in self.data['portforwards']:
            if self._compare_objects(fw, forward, 'srcip', 'srcport'):
                if set(fw['protocols']).intersection(set(forward['protocols'])):
                    raise ValueError('Forward conflicts with existing forward')
        self.data['portforwards'].append(forward)
        self._gateway_sal.deploy()

    def remove_portforward(self, forward):
        self.state.check('actions', 'start', 'ok')

        for fw in self.data['portforwards']:
            if self._compare_objects(fw, forward, 'srcip', 'srcport'):
                if set(fw['protocols']).intersection(set(forward['protocols'])):
                    self.data['portforwards'].remove(fw)
                    break
        else:
            return
        self._gateway_sal.configure_fw()

    def add_http_proxy(self, proxy):
        self.state.check('actions', 'start', 'ok')

        for existing_proxy in self.data['httpproxies']:
            if self._compare_objects(existing_proxy, proxy, 'host'):
                raise ValueError("Proxy with host {} already exists".format(proxy['host']))
        self.data['httpproxies'].append(proxy)
        self._gateway_sal.configure_http()

    def remove_http_proxy(self, proxy):
        self.state.check('actions', 'start', 'ok')

        for existing_proxy in self.data['httpproxies']:
            if self._compare_objects(existing_proxy, proxy, 'host'):
                self.data['httpproxies'].remove(existing_proxy)
                break
        else:
            return
        self._gateway_sal.configure_http()

    def add_dhcp_host(self, nicname, host):
        self.state.check('actions', 'start', 'ok')

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
        self.state.check('actions', 'start', 'ok')

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
        self._gateway_sal.configure_cloudinit()

    def _compare_objects(self, obj1, obj2, *keys):
        for key in keys:
            if obj1[key] != obj2[key]:
                return False
        return True

    def add_nic(self, nic):
        self.state.check('actions', 'start', 'ok')

        for existing_nic in self.data['nics']:
            if self._compare_objects(existing_nic, nic, 'type', 'id'):
                raise ValueError('Nic with same type/id combination already exists')
        self._gateway_sal.deploy()

    def remove_nic(self, nicname):
        self.state.check('actions', 'start', 'ok')

        for nic in self.data['nics']:
            if nic['name'] == nicname:
                break
        else:
            return
        self._gateway_sal.deploy()

    def update_data(self, data):
        raise NotImplementedError('Not supported use actions instead')

    def uninstall(self):
        self.state.check('actions', 'install', 'ok')
        self._gateway_sal.stop()
        self.state.delete('actions', 'install')
        self.state.delete('actions', 'start')

    def stop(self):
        self.state.check('actions', 'start', 'ok')
        self._gateway_sal.stop()
        self.state.delete('actions', 'start')

    def start(self):
            self.install()
