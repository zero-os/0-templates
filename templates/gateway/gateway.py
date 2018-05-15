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
        return j.clients.zos.sal.get_node(NODE_CLIENT)

    @property
    def _gateway_sal(self):
        return self._node_sal.primitives.from_dict('gateway', self.data)

    def install(self):
        gateway_sal = self._gateway_sal
        gateway_sal.deploy()
        self.data['ztIdentity'] = gateway_sal.zt_identity
        self.state.set('actions', 'install', 'ok')
        self.state.set('actions', 'start', 'ok')

    def add_portforward(self, forward):
        self.state.check('actions', 'start', 'ok')

        for network in self.data['networks']:
            if network['name'] == forward['srcnetwork']:
                break
        else:
            raise LookupError('Network with name {} doesn\'t exist'.format(forward['srcnetwork']))

        for fw in self.data['portforwards']:
            name, combination = self._compare_objects(fw, forward, 'srcnetwork', 'srcport')
            if name:
                raise ValueError('A forward with the same name exists')
            if combination:
                if set(fw['protocols']).intersection(set(forward['protocols'])):
                    raise ValueError('Forward conflicts with existing forward')
        self.data['portforwards'].append(forward)
        self._gateway_sal.deploy()

    def remove_portforward(self, forward_name):
        self.state.check('actions', 'start', 'ok')

        for fw in self.data['portforwards']:
            if fw['name'] == forward_name:
                self.data['portforwards'].remove(fw)
                break
        else:
            raise LookupError('Forward {} doesn\'t exist'.format(forward_name))
        self._gateway_sal.configure_fw()

    def add_http_proxy(self, proxy):
        self.state.check('actions', 'start', 'ok')

        for existing_proxy in self.data['httpproxies']:
            name, combination = self._compare_objects(existing_proxy, proxy, 'host')
            if name:
                raise ValueError('A proxy with the same name exists')
            if combination:
                raise ValueError("Proxy with host {} already exists".format(proxy['host']))
        self.data['httpproxies'].append(proxy)
        self._gateway_sal.configure_http()

    def remove_http_proxy(self, proxy_name):
        self.state.check('actions', 'start', 'ok')

        for existing_proxy in self.data['httpproxies']:
            if existing_proxy['name'] == proxy_name:
                self.data['httpproxies'].remove(existing_proxy)
                break
        else:
            raise LookupError('Proxy with name {} doesn\'t exist'.format(proxy_name))
        self._gateway_sal.configure_http()

    def add_dhcp_host(self, network_name, host):
        self.state.check('actions', 'start', 'ok')

        for network in self.data['networks']:
            if network['name'] == network_name:
                break
        else:
            raise LookupError('Network with name {} doesn\'t exist'.format(network_name))
        dhcpserver = network['dhcpserver']
        for existing_host in dhcpserver['hosts']:
            if existing_host['macaddress'] == host['macaddress']:
                raise ValueError('Host with macaddress {} already exists'.format(host['macaddress']))
        dhcpserver['hosts'].append(host)
        self._gateway_sal.configure_dhcp()
        self._gateway_sal.configure_cloudinit()

    def remove_dhcp_host(self, networkname, host):
        self.state.check('actions', 'start', 'ok')

        for network in self.data['networks']:
            if network['name'] == networkname:
                break
        else:
            raise LookupError('Network with name {} doesn\'t exist'.format(networkname))
        dhcpserver = network['dhcpserver']
        for existing_host in dhcpserver['hosts']:
            if existing_host['macaddress'] == host['macaddress']:
                dhcpserver['hosts'].remove(existing_host)
                break
        else:
            raise LookupError('Host with macaddress {} doesn\'t exist'.format(host['macaddress']))
        self._gateway_sal.configure_dhcp()
        self._gateway_sal.configure_cloudinit()

    def _compare_objects(self, obj1, obj2, *keys):
        """
        Checks that obj1 and obj2 have different names, and that the combination of values from keys are unique
        :param obj1: first dict to use for comparison
        :param obj2: second dict to use for comparison
        :param keys: keys to use for value comparison
        :return: a tuple of bool, where the first element indicates whether the name matches or not,
        and the second element indicates whether the combination of values matches or not
        """
        name = obj1['name'] == obj2['name']
        for key in keys:
            if obj1[key] != obj2[key]:
                return name, False
        return name, True

    def add_network(self, network):
        self.state.check('actions', 'start', 'ok')

        for existing_network in self.data['networks']:
            name, combination = self._compare_objects(existing_network, network, 'type', 'id')
            if name:
                raise ValueError('Network with name {} already exists'.format(name))
            if combination:
                raise ValueError('network with same type/id combination already exists')
        self.data['networks'].append(network)
        self._gateway_sal.deploy()

    def remove_network(self, network_name):
        self.state.check('actions', 'start', 'ok')

        for network in self.data['networks']:
            if network['name'] == network_name:
                self.data['networks'].remove(network)
                break
        else:
            raise LookupError('Network with name {} doesn\'t exists'.format(network_name))
        self._gateway_sal.deploy()

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
        self.state.check('actions', 'install', 'ok')
        self.install()
