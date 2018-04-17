## template: github.com/zero-os/0-templates/node/0.0.1

### Description:
This template is responsible for managing a zero-os node.

### Schema:

- `hostname`: the name of the host. It will be automatically filled when the node is created by the `zero_os_bootstrap` service. **optional**
- `version`: the version of the zero-os. It set by the template.
- `uptime`: node uptime in seconds


### Actions
- `install`: installs a node and makes it managable by zero-robot. As part of the installation, it creates a partition and mounts it to be used as cache for g8ufs, the label of the partition is `fs_cache`.
- `reboot`: stops all containers and vms and reboots the node. 
It waits for 60 seconds for the node to reboot then it starts the containers and vms again.
- `uninstall`: stops all vms and containers and deletes the service.


```yaml
github.com/zero-os/0-templates/node/0.0.1__525400123456:
  hostname: "myzeros"

actions:
  action: ['install']
```


```yaml
actions:
  template: github.com/zero-os/0-templates/node/0.0.1
  name: 525400123456
  actions: ['uninstall']
```

```yaml
actions:
  template: github.com/zero-os/0-templates/node/0.0.1
  name: 525400123456
  actions: ['reboot']
```
