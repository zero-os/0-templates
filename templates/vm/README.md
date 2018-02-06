## template: github.com/zero-os/0-templates/vm/0.0.1

### Description:
This template is responsible for managing a vm on a zero-os node.

### Schema:

- `node`: the node to deploy the vm on.
- `node`: the node to deploy the vm on.
- `memory`: amount of memory in MiB. Defaults to 128.
- `cpu`: number of virtual CPUs. Defaults to 1.
- `nics`: list of type NicLink specifying the nics of this vm.
- `vdisks`: list of type DiskLink 
- `flist`: if specified the vm will boot from this flist and not the vdisk.
- `vnc`: the vnc port the machine is listening to.

NicLink:
- `id`: vxlan or vlan id
- `type`: NicType enum specifying the nic type
- `macaddress`: nic's macaddress

DiskLink:
- `vdiskId`: vdisk identifier.
- `maxIOps`: maximum iops for this disk

NicType enum: 
- `default` 
- `vlan`
- `vxlan`
- `bridge`


### Actions:
- `install`: creates a a vm and the hypervisor on the node.
- `uninstall`: destroys and deletes the service from 0-robot and the node.
- `shutdown`: shuts down the vm.
- `pause`: pause the vm.
- `resume`: resume the vm.
- `reboot`: reboot the vm.
- `reset`: reset the vm.
- `enable_vnc`: if a vnc port is specified, it opens the port.
- `disable_vnc`: if a vnc port is specified, it drops the port.