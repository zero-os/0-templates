# template: github.com/zero-os/0-templates/hypervisor/0.0.1

## Description:
This template is responsible for managing a zero-os kvm hypervisor.

## Schema:

- node: the name of the node the hypervisor is on
- vm: the name of the vm


## Actions

#### Create
Creates a hypervisor on a zeroos node

Arguments:
- media:
- flist:
- cpu:
- memory:
- nics:
- port: 
- mount:
- tags

#### Destroy
destroys the hypervisor 

#### Shutdown
Shuts down the hypervisor

#### Pause
Pause the hypervisor

#### Resume
Resume the hypervisor

#### Reboot
Reboot the hypervisor

#### Reset
Reset the hypervisor


## Example for installing a node
```yaml
github.com/zero-os/0-templates/node/0.0.1__525400123456:
  redisAddr: 172.17.0.1
  redisPort: 6379
  hostname: "myzeros"

actions:
  action: ['install']
```

## Example for uninstalling a node

```yaml
actions:
  template: github.com/zero-os/0-templates/node/0.0.1
  name: 525400123456
  actions: ['uninstall']
```

## Example for rebooting a node

```yaml
actions:
  template: github.com/zero-os/0-templates/node/0.0.1
  name: 525400123456
  actions: ['reboot']
```
