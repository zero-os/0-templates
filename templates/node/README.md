## template: github.com/zero-os/0-templates/node/0.0.1

### Description:
This template is responsible for managing a zero-os node.

### Schema:

- `hostname`: the name of the host. It will be automatically filled when the node is created by the `zero_os_bootstrap` service. **optional**
- `version`: the version of the zero-os. It set by the template.
- `uptime`: node uptime in seconds
- `deployZdb`: a boolean indicating whether 0-db should be installed on each disk or not upon the node install. 


### Actions
- `install`: installs a node and makes it manageable by zero-robot.
- `reboot`: stops all containers and vms and reboots the node.
- `info`: returns node os info.
- `stats`: returns the node aggregated statistics.
- `processes`: returns the list of processes running on the node.
- `os_version`: returns the node version


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
  actions: ['reboot']
```
