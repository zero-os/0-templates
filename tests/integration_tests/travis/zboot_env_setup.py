from js9 import j
import argparse, os, time, random

def authorize_zt_member(zerotier_instance, networkId):
    members = zerotier_instance.network.listMembers(networkId).json()
    for member in members:
        if not member['config']['authorized']:
            address = member['config']['address']
            data = {"config": {"authorized": True}}
            zerotier_instance.network.updateMember(id=networkId, address=address, data=data)
            return member['config']['id']
        
def main(options):
    import ipdb ; ipdb.set_trace()
    """[summary]
    Arguments:
        router_address {str} -- address of the router in the zerotier network.
        router_username {str} -- username on the router.
        router_password {str} -- password of router username.
        zerotier_network {str} -- router's zerotier network.
        zerotier_token {str} -- router's zerotier token.
        rack_hostname {str} -- address of the racktivity device in the internal router network.
        rack_username {str} -- user login for the racktivity device.
        rack_password {str} -- password for user login.
        rack_module_id {str} -- rack module id.
        cpu {str} -- cpu's hostname.
        cpu_port {int} -- cpu's rack port.
        core_0_branch {str} -- 0core branch.
    """

    instance_name = 'test-{}'.format(random.randint(1, 1000))

    # configure ssh client
    data = {
        'addr':options.router_address, 
        'login':options.router_username, 
        'passwd_':options.router_password
    }
    sshclient = j.clients.ssh.get(instance_name, data=data, interactive=False)

    # configure ssh client
    data = {'token_':options.zerotier_token}
    zerotier = j.clients.zerotier.get(instance_name, data=data, interactive=False)

    # configure racktivity client
    data = {
        'hostname':options.rack_hostname, 
        'username':options.rack_username, 
        'password_':options.rack_password
    }
    rack = j.clients.racktivity.get(instance_name, data=data, interactive=False)

    # configure zeroboot client
    data = {
        'network_id':options.zerotier_network, 
        'sshclient_instance':instance_name, 
        'zerotier_instance':instance_name
    }
    zboot = j.clients.zboot.get(instance_name, data=data, interactive=False)

    try:
        network = zboot.networks.get()
        node = network.hosts.get(options.cpu_hostname)

        print('[*] Create testing zerotier network')
        testing_zt_network = zerotier.network_create(public=False, subnet='10.147.17.0/24')

        print('[*] Configure node ipxe boot url')
        ipxe_url = 'http://unsecure.bootstrap.gig.tech/ipxe/{branch}/{zerotier_network}/development'.format(
            branch=options.core_0_branch,
            zerotier_network=testing_zt_network.id
        )
        node.configure_ipxe_boot(ipxe_url)

        print('[*] Reboot node: {}'.format(options.cpu_hostname))
        zboot.port_power_cycle([options.cpu_rack_port], rack, options.rack_module_id)

        time.sleep(120)

        print('[*] Authorize node on zerotier network')
        cpu_zt_ip = authorize_zt_member(zerotier, testing_zt_network.id)

        print('[*] Done ==============================================')
        print('[*] Zerotier network: {}'.format(testing_zt_network.id))
        print('[*] Node zerotier ip address: {}'.format(cpu_zt_ip))

        os.system('printf "{}" > /tmp/testing_zt_network.txt'.format(testing_zt_network.id))
        os.system('printf "{}" > /tmp/cpu_zt_ip.txt'.format(cpu_zt_ip))
    
    finally:
        j.clients.zerotier.delete(instance_name)
        j.clients.ssh.delete(instance_name)
        j.clients.zboot.delete(instance_name)        
        j.clients.racktivity.delete(instance_name)

if __name__ == "__main__":    
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--router_address", type=str, required=True)
    parser.add_argument("-u", "--router_username", type=str, required=True)
    parser.add_argument("-k", "--router_password", type=str, required=True)
    parser.add_argument("-n", "--zerotier_network", type=str, required=True)
    parser.add_argument("-t", "--zerotier_token", type=str, required=True)
    parser.add_argument("-l", "--rack_hostname", type=str, required=True)
    parser.add_argument("-l", "--rack_username", type=str, required=True)
    parser.add_argument("-s", "--rack_password", type=str, required=True)
    parser.add_argument("-m", "--rack_module_id", type=str, required=True)
    parser.add_argument("-c", "--cpu_hostname", type=str, required=True)
    parser.add_argument("-p", "--cpu_rack_port", type=int, required=True)
    parser.add_argument("-b", "--core_0_branch", type=str, default='development')
    options = parser.parse_args()

    main(options)