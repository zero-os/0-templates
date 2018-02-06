## template: github.com/zero-os/0-templates/hypervisor/0.0.1

### Description:
This template is responsible for managing a zero-os kvm hypervisor.

### Schema:

- `node`: the name of the node the hypervisor is on.
- `vm`: the name of the vm.


### Actions

- `create`: creates a hypervisor on a zeroos node.

    Arguments:
    - `media`: array of media objects to attach to the machine, where the first object is the boot device.

         Each media object is a dict of {url, type} where type can be one of `disk`, or `cdrom`, or empty (default to disk) example:

       ```python
       [{'url': 'nbd+unix:///test?socket=/tmp/ndb.socket'}, {'type': 'cdrom': '/somefile.iso'}]
       ```

    - `flist`: VM flist. A special bootable flist witch has a correct boot.yaml file
    - `cpu`: number of vcpu cores.
    - `memory`: memory in MiB.
    - `nics`: Configure the attached nics to the container. Each nic object is a dict of the format:

        ```python
        {
         'type': nic_type # default, bridge, vlan, or vxlan (note, vlan and vxlan only supported by ovs)
         'id': id # depends on the type, bridge name (bridge type) zerotier network id (zertier type), the vlan tag or the vxlan id
        }
        ```

    - `port`: a dict of host port:hypervisor port pairs.
    - `mount`:  A list of host shared folders in the following format:

        ```python
        {'source': '/host/path', 'target': '/guest/path', 'readonly': True|False}
        ```
    - `tags`: tags for the hypervisor.

- `destroy`: destroys the hypervisor.
- `shutdown`': shuts down the hypervisor.
- `pause`: pause the hypervisor.
- `resume`: resume the hypervisor.
- `reboot`: reboot the hypervisor.
- `reset`: reset the hypervisor.
