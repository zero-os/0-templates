## template: github.com/zero-os/0-templates/vm/0.0.1

### Description:
This template is responsible for managing a vm on a zero-os node.

### Schema:

- `memory`: amount of memory in MiB. Defaults to 128.
- `cpu`: number of virtual CPUs. Defaults to 1.
- `nics`: list of type NicLink specifying the nics of this vm.
- `media`: list of Media that can be attached to the vm 
- `flist`: if specified the vm will boot from this flist and not the vdisk.
- `vnc`: the vnc port the machine is listening to.
- `ports`: List of node to vm port mappings. e.g: ['8080:80']
- `tags`: List of vm tags. e.g ['tag']
- `configs`: List of type Config.

NicLink:
- `id`: vxlan or vlan id
- `type`: NicType enum specifying the nic type
- `macaddress`: nic's macaddress

NicType enum: 
- `default` 
- `vlan`
- `vxlan`
- `bridge`

Media:
- `mediaType`: mediaType enum specifying media type
- `url`: media location

Config:
- `path`: the file path 
- `content`: the file content

MediaType enum: 
- `disk` 
- `cdrom`

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

### Examples:
#### DSL (api interface):
```python
data = {
    'memory': 256,
    'cpu': 1,
    'nics': [{'type':'default'}],
    'flist': 'https://hub.gig.tech/gig-bootable/ubuntu-xenial-bootable-sshd.flist',
    'ports':["22:22"],
    'configs': [{'path': '/root/.ssh/authorized_keys', 'content': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDC8tBgGU1'}]
}
vm = robot.services.create('github.com/zero-os/0-templates/vm/0.0.1','vm1', data)
vm.schedule_action('install')
```

#### Blueprint (cli interface):
```yaml
services:
    - github.com/zero-os/0-templates/vm/0.0.1__vm1:
        flist: 'https://hub.gig.tech/gig-bootable/ubuntu-xenial-bootable-sshd.flist',
        memory: 256
        cpu: 1
        nics: 
            - type: 'default'
        ports:
            - '22:22'
       configs:
         - path: '/root/.ssh/authorized_keys'
           content: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDC8tBgGU1'



actions:
    - actions: ['install']
      service: vm1
```
