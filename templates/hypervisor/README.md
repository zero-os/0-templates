## template: github.com/zero-os/0-templates/hypervisor/0.0.1

### Description:
This template is responsible for managing a zero-os kvm hypervisor.

### Schema:

- `node`: the name of the node the hypervisor is on.
- `vm`: the name of the vm.


### Actions

- `create`: creates a hypervisor on a zeroos node.

    Arguments:
    - `media`:
    - `flist`:
    - `cpu`:
    - `memory`: 
    - `nics`: Configure the attached nics to the container. Each nic object is a dict of the format:
    
           {
              'type': nic_type # default, bridge, vlan, or vxlan (note, vlan and vxlan only supported by ovs)
              'id': id # depends on the type, bridge name (bridge type) zerotier network id (zertier type), the vlan tag or the vxlan id
           }
    - `port`: a dict of host port:hypervisor port pairs.
    - `mount`:  A list of host shared folders in the format {'source': '/host/path', 'target': '/guest/path', 'readonly': True|False}.
    - `tags`: tags for the hypervisor.

- `destroy`: destroys the hypervisor.
- `shutdown`': shuts down the hypervisor.
- `pause`: pause the hypervisor.
- `resume`: resume the hypervisor.
- `reboot`: reboot the hypervisor.
- `reset`: reset the hypervisor.
