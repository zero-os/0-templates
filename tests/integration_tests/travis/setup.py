from js9 import j
from termcolor import colored
import argparse, time, uuid


def get_available_facility(client, plan):
    facilities = client.client.list_facilities()
    for facility in facilities:
        try:
            if client.client.validate_capacity([(facility.code, plan, 1)]):
                return facility.code
        except:
            pass
    else:
        return None


def create_device(packet_client, zos_version, zt_token):
    print(colored(' [*] Create zerotier network.', 'white'))
    zt_config_instance_name = str(uuid.uuid4()).replace('-', '')[:10]
    zt_name = str(uuid.uuid4()).replace('-', '')[:10]
    zt_client = j.clients.zerotier.get(instance=zt_config_instance_name, data={'token_': zt_token})
    zt_network = zt_client.network_create(public=True, name=zt_name, auto_assign=True,
                                          subnet='10.147.19.0/24')
    with open('/tmp/testing_zt_network.txt', 'w') as file:
        file.write(zt_network.id)
    print(colored(' [*] ZT ID: {} '.format(zt_network.id), 'green'))

    ipxe = 'http://unsecure.bootstrap.gig.tech/ipxe/{}/{}/console=ttyS1,115200%20development'.format(zos_version,
                                                                                                     zt_network.id)
    print(colored(' [*] ipxe : {}'.format(ipxe), 'yellow'))
    print(colored(' [*] Install ZOS packet machine', 'white'))
    packet_machine_name = '0-core-TEST'
    plan = "baremetal_0"
    project_id = packet_client.client.list_projects()[0].id
    facility = get_available_facility(client=packet_client, plan=plan)
    device_data = packet_client.client.create_device(project_id=project_id, hostname=packet_machine_name, plan=plan,
                                                     facility=facility, operating_system="custom_ipxe",
                                                     ipxe_script_url=ipxe, termination_time=10800)
    print(colored(' [*] wait .. booting .. ', 'yellow'))
    for _ in range(300):
        try:
            device = packet_client.client.get_device(device_data.id)
        except:
            time.sleep(10)
    with open('/tmp/device_id.txt', 'w') as file:
        file.write(device_data.id)

    print(colored(' [*] packet machine IP : {} '.format(device.ip_addresses[0]['address']), 'green'))

    print(colored(' [*] Authorize it', 'white'))
    for _ in range(300):
        try:
            zos_zt_member = zt_network.member_get(public_ip=device.ip_addresses[0]['address'])
        except:
            time.sleep(10)
        else:
            zos_zt_member = zt_network.member_get(public_ip=device.ip_addresses[0]['address'])

    zos_zt_member.authorize()
    packet_machine_zt_ip = zos_zt_member.private_ip
    with open('/tmp/ip.txt', 'w') as file:
        file.write(packet_machine_zt_ip)
    print(colored(' [*] packet_machine_zt_ip = {}'.format(packet_machine_zt_ip), 'green'))


def delete_device(packet_client):
    with open('/tmp/device_id.txt', 'r') as file:
        device_id = file.read()
        device = packet_client.client.get_device(device_id)
        device.delete()

if __name__ == "__main__":
    print(colored(' [*] Setup Testing env ... '))
    parser = argparse.ArgumentParser()
    parser.add_argument("--zos-version", dest="zos_version", default='development', help="zos version")
    parser.add_argument("--zt-token", dest="zt_token", help="zerotier token")
    parser.add_argument("--pckt_token", dest="packet_token", help="packet token")
    parser.add_argument("--action", dest="action", help="packet action")
    args = parser.parse_args()
    zos_version = args.zos_version
    zt_token = args.zt_token
    packet_auth_token = args.packet_token
    action = args.action
    packet_client_data = {"auth_token_": packet_auth_token,
                          "project_name": "GIG Engineering"}
    packet_client = j.clients.packetnet.get(data=packet_client_data)
    if action == "create":
        create_device(packet_client, zos_version, zt_token)
    elif action == "delete":
        delete_device(packet_client)

