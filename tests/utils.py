import requests, argparse, sys, packet, random, zerotier, time, uuid, os

class Packet:
    def __init__(self, token):
        self.manager = packet.Manager(auth_token=token)
        self.project = self.manager.list_projects()[0].id

    def get_available_facility(self, plan):
        facilities = self.manager.list_facilities()
        for facility in facilities:
            try:
                if self.manager.validate_capacity([(facility.code, plan, 1)]):
                    return facility.code
            except:
                pass
        else:
            return None

    
    def create_machine(self, hostname, plan='baremetal_0'):
        facility = self.get_available_facility(plan=plan)
        device = self.manager.create_device(
            project_id=self.project,
            hostname=hostname,
            plan=plan,
            operating_system='ubuntu_16_04',
            facility=facility
        )
        return device
                
    def create_node(self, hostname, branch, zerotier_network, plan='baremetal_0'):
        ipxe_script_url = 'http://unsecure.bootstrap.gig.tech/ipxe/%s/%s' % (branch, zerotier_network)
        facility = self.get_available_facility(plan=plan)
        device = self.manager.create_device(
            project_id=self.project,
            hostname=hostname,
            plan=plan,
            operating_system='custom_ipxe',
            ipxe_script_url=ipxe_script_url,
            facility=facility
        )
        return device

    
    def wait_for_ipaddress(self, deviceId, timeout=300):
        for _ in range(timeout):
            device = self.manager.get_device(deviceId)
            if device.state == 'active':
                return device.ip_addresses[0]['address']
            else:
                time.sleep(1)
        else:
            raise RuntimeError('packet machine creation timeout')

    def delete_devices(self, hostname):
        devices = self.manager.list_devices(self.project)
        for device in devices:
            if hostname in device.hostname:
                self.manager.call_api('devices/%s' % device.id, type='DELETE')

    
    def delete_ssh_keys(self, label):
        ssh_keys = self.manager.list_ssh_keys()
        for ssh_key in ssh_keys:
            if label in ssh_key.label:
                self.manager.call_api('ssh-keys/%s' % ssh_key.id, type='DELETE')


def create_zerotier_network(token):
    session = requests.Session()
    session.headers['Authorization'] = 'Bearer {}'.format(token)

    data = {
        'config': {
            'ipAssignmentPools': [
                {'ipRangeEnd': '10.147.17.254', 'ipRangeStart': '10.147.17.1'}
            ],
            'private': 'true',
            'routes': [
                {'target': '10.147.17.0/24', 'via': None}
            ],
            'v4AssignMode': {'zt': 'true'}}
        }

    response = session.post(url='https://my.zerotier.com/api/network', json=data)
    return response.json()['id']
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=str, required=True)
    parser.add_argument("-t", "--packet_token", type=str)
    parser.add_argument("-b", "--zero_os_branch", type=str, default='master')
    parser.add_argument("-k", "--job_key", type=str)
    parser.add_argument("-z", "--zerotier_network", type=str)
    parser.add_argument("-s", "--zerotier_token", type=str)
    parser.add_argument("-n", "--number_of_nodes", type=int, default=1)
  
    options = parser.parse_args()
    
    if options.action == 'create_zerotier_network':
        zerotier_network = create_zerotier_network(options.zerotier_token)
        os.system('printf "{}" > /tmp/zerotier_network.txt'.format(zerotier_network))
        print(zerotier_network)

    elif options.action == 'create_ctrl':
        packet_client = Packet(token=options.packet_token)
        hostname = 'travis-ctrl-{}'.format(options.job_key)

        with open(os.path.join(os.environ['HOME'], '.ssh/id_rsa.pub'), 'r') as f:
            sshkey = f.read().strip()

        ssh_label = 'sshkey-{}'.format(options.job_key)
        packet_client.manager.create_ssh_key(ssh_label, sshkey)
        
        device = packet_client.create_machine(hostname)
        device_ipaddress = packet_client.wait_for_ipaddress(device.id)

        os.system('printf "{}" > /tmp/device_id.txt'.format(device.id))        
        os.system('printf "{}" > /tmp/device_ipaddress.txt'.format(device_ipaddress))

        print(device_ipaddress)

    elif options.action == 'create_nodes':
        packet_client = Packet(token=options.packet_token)
        for i in range(options.number_of_nodes):
            hostname = 'travis-node-{}-{}'.format(str(i), options.job_key) 
            packet_client.create_node(hostname, options.zero_os_branch, options.zerotier_network)

    elif options.action == 'teardown':
        packet_client = Packet(token=options.packet_token)
        packet_client.delete_devices(options.job_key)
        packet_client.delete_ssh_keys(options.job_key)

    elif options.action == 'bootstrap':
        from zerorobot.dsl import ZeroRobotAPI
        from js9 import j
        
        apis = ZeroRobotAPI.ZeroRobotAPI()
        api = apis.robots['main']

        data = {'token_':options.zerotier_token}
        j.dirs.HOMEDIR = '/root'        
        j.clients.zerotier.get(data=data)

        service_name = str(uuid.uuid4()).replace('-', '')[:10]
        template_uid = 'github.com/zero-os/0-templates/zeroos_bootstrap/0.0.1'
        data = {'zerotierClient':'main', 'zerotierNetID':options.zerotier_network}
        nodes = api.services.create(template_uid=template_uid, service_name=service_name, data=data)

        zerotier_client = zerotier.APIClient()
        zerotier_client.set_auth_header('Bearer {}'.format(options.zerotier_token))

        for i in range(30):
            zerotier_members = zerotier_client.network.listMembers(options.zerotier_network).json()
            authorized_nodes = [member for member in zerotier_members if (member['online'] and member['name'] and member['config']['authorized'])]
            
            print("[+] found {} of {} nodes".format(len(authorized_nodes), options.number_of_nodes))

            if len(authorized_nodes) == options.number_of_nodes:
                break
            else:
                time.sleep(60)
        else:
            sys.exit('[-] Cannot install Zero-OS nodes')
