from js9 import j
import copy
import netaddr
from zerorobot.template.base import TemplateBase

NODE_CLIENT = 'local'
GATEWAY_TEMPLATE_UID = 'github.com/zero-os/0-templates/gateway/0.0.1'


class PublicGateway(TemplateBase):
    version = '0.0.1'
    template_name = "public_gateway"

    def validate(self):
        services = self.api.services.find(template_uid=GATEWAY_TEMPLATE_UID, name='publicgw')
        if len(services) != 1:
            raise RuntimeError('This service requires there to be exactly one gateway deployed with name `publicgw`')
        for forward in self.data.get('portforwards', []):
            if not forward.get('name'):
                raise ValueError('Name is a required attribute for portforward')
            if not isinstance(forward.get('srcport'), int):
                raise ValueError('srcport should be an int')
            if not isinstance(forward.get('dstport'), int):
                raise ValueError('dstport should be an int')
            for protocol in forward.get('protocols', []):
                if protocol not in ['tcp', 'udp']:
                    raise ValueError('Invalid protocol {}'.format(protocol))
            netaddr.IPAddress(forward.get('dstip'))
        for proxy in self.data.get('httpproxies', []):
            if not proxy.get('name'):
                raise ValueError('Name is a required attribute for http proxy')
            if not proxy.get('host'):
                raise ValueError('Host is a required attribute for http proxy')
            if not proxy.get('destinations'):
                raise ValueError('Destinations is a required attribute for http proxy')

    @property
    def _node_sal(self):
        return j.clients.zos.sal.get_node(NODE_CLIENT)

    @property
    def _gateway_service(self):
        return self.api.services.get(template_uid=GATEWAY_TEMPLATE_UID, name='publicgw')

    def install(self):
        self.logger.info('Install public gateway {}'.format(self.name))
        gw_service = self._gateway_service
        portforwards = self.data.get('portforwards')
        for portforward in portforwards:
            fwd = copy.deepcopy(portforward)
            fwd['srcnetwork'] = 'public'
            fwd['name'] = self._prefix_name(portforward['name'])
            gw_service.schedule_action('add_portforward', args={'forward': fwd}).wait(die=True)

        proxies = self.data.get('httpproxies')
        for proxy in proxies:
            p = copy.deepcopy(proxy)
            p['name'] = self._prefix_name(proxy['name'])
            gw_service.schedule_action('add_http_proxy', args={'proxy': p}).wait(die=True)

    def add_portforward(self, forward):
        self.logger.info('Add portforward {}'.format(forward['name']))
        gw_service = self._gateway_service
        fwd = copy.deepcopy(forward)
        fwd['srcnetwork'] = 'public'
        fwd['name'] = self._prefix_name(forward['name'])
        gw_service.schedule_action('add_portforward', args={'forward': fwd}).wait(die=True)
        self.data['portforwards'].append(forward)

    def _prefix_name(self, name):
        return '{}_{}'.format(self.guid, name)

    def remove_portforward(self, forward_name):
        self.logger.info('Remove portforward {}'.format(forward_name))
        name = self._prefix_name(forward_name)
        self._gateway_service.schedule_action('remove_portforward', args={'forward_name': name}).wait(die=True)
        for forward in self.data['portforwards']:
            if forward['name'] == forward_name:
                self.data['portforwards'].remove(forward)
                return

    def add_http_proxy(self, proxy):
        self.logger.info('Add http proxy {}'.format(proxy['name']))
        gwproxy = copy.deepcopy(proxy)
        gwproxy['name'] = self._prefix_name(proxy['name'])
        self._gateway_service.schedule_action('add_http_proxy', args={'proxy': gwproxy}).wait(die=True)
        self.data['httpproxies'].append(proxy)

    def remove_http_proxy(self, proxy_name):
        self.logger.info('Remove http proxy {}'.format(proxy_name))
        name = self._prefix_name(proxy_name)
        self._gateway_service.schedule_action('remove_http_proxy', args={'proxy_name': name}).wait(die=True)
        for proxy in self.data['httpproxies']:
            if proxy['name'] == proxy_name:
                self.data['httpproxies'].remove(proxy)
                return

    def info(self):
        gwinfo = self._gateway_service.schedule_action('info').wait(die=True).result
        publicip = ''
        zerotierId = ''
        for network in gwinfo['networks']:
            if network['name'] == 'public':
                publicip = network['config']['cidr']
                continue
            elif network['type'] == 'zerotier':
                zerotierId = network['id']
        data = {
            'portforwards': self.data['portforwards'],
            'httpproxies': self.data['httpproxies'],
            'publicip': publicip,
            'zerotierId': zerotierId
        }
        return data

    def uninstall(self):
        gw_service = self._gateway_service
        self.logger.info('Uninstall publicservice {}'.format(self.name))
        for portforward in self.data['portforwards']:
            name = self._prefix_name(portforward['name'])
            gw_service.schedule_action('remove_portforward', args={'forward_name': name}).wait(die=True)

        proxies = self.data.get('httpproxies')
        for proxy in proxies:
            name = self._prefix_name(proxy['name'])
            gw_service.schedule_action('remove_http_proxy', args={'proxy_name': name}).wait(die=True)

