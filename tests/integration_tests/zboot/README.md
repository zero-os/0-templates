## What this script does ?
Automate zboot environment setup for testing
- Configure Jumpscale clients.
- Create zerotier network for testing.
- Configure target cpu node's ipxe boot url.
- Reboot target node.
- Authorize the cpu node on the zerotier network and get its ip address.

## Usage

```bash 
python3 zboot_env_setup.py [arguments]
```

#### Arguments
```--router_ip```:  address of the router in the zerotier network.

```--router_username```: username on the router.

```--router_password```: password of router username.

```--zerotier_network```: zerotier network of the router.

```--zerotier_token```: zerotier token.

```--rack_ip```:    address of the racktivity device in the internal router network.

```--rack_username```: user login for the racktivity device.

```--rack_password```: password for rack device.

```--rack_model_id```: racktivity device model id.

```--zero_os_branch```: zero-os branch.

```--cpu_hostname```: cpu hostname.

```--cpu_rack_port```: racktivity device port connected to the target node.
