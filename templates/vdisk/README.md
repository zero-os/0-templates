## template: github.com/zero-os/0-templates/vdisk/0.0.1

### Description:
This template is responsible for managing a vdisk

### Schema:

- `zerodb`: the zerodb to create the namespace for the vdisk on.
- `size`: the vdisk size
- `diskType`: the type of the disk to use for the namespace
- `mountPoint`: mount point of the disk
- `filesystem`: filesystem to create on the disk
- `nsName`: the name of the namespace created on tzerodb

### Actions
- `install`: creates the vdisk and namespace.
- `info`: returns info about the namespace. 
- `url`: return the public url of the namespace.
- `private_url`: return the private url of the namespace.
- `uninstall`: uninstall the vdisk by deleting the namespace

### Usage example via the 0-robot DSL

```python
from zerorobot.dsl import ZeroRobotAPI

robot = j.clients.zrobot.robots['main']

args = {
    'size': 10,
    'diskType': 'hdd',
}
vdisk = robot.services.create('github.com/zero-os/0-templates/vdisk/0.0.1', 'vdisk_one', data=args)
vdisk.schedule_action('install')
vdisk.schedule_action('info')
```


### Usage example via the 0-robot CLI

To create vdisk `vdisk_one`:

```yaml
services:
    - github.com/zero-os/0-templates/vdisk/0.0.1__vdisk_one:
          size: 10
          diskType: 'hdd'
          
actions:
    - template: 'github.com/zero-os/0-templates/vdisk/0.0.1'
      service: 'vdisk_one'
      actions: ['install']

```


To get info for vdisk `vdisk_one`:

```yaml
actions:
    - template: 'github.com/zero-os/0-templates/vdisk/0.0.1'
      service: 'vdisk_one'
      actions: ['info']

```