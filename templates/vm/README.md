# template: github.com/zero-os/0-templates/vm/0.0.1

## Description:
This template is responsible for managing a vm on a zero-os node.

## Schema:

- node: the node to deploy the vm on.
- id: ?
- memory: amount of memory in MiB. Defaults to 128.
- cpu: number of virtual CPUs. Defaults to 1.
- nics: list of type NicLink specifying the nics of this vm.
- vdisks: list of type DiskLink 
- flist: if specified the vm will boot from this flist.
- vnc: the vnc port the machine is listening to.



## Actions

#### Install
Creates a a vm and the hypervisor on the node

#### Uninstall
destroys the and deletes the service

#### Shutdown
Shuts down the vm

#### Pause
Pause the vm

#### Resume
Resume the vm

#### Reboot
Reboot the vm

#### Reset
Reset the vm

### enable_vnc
If a vnc port is specified, it opens the port

### disable_vnc
If a vnc port is specified, it drops the port
