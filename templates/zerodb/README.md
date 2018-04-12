## template: github.com/zero-os/0-templates/zerodb/0.0.1

### Description:
This template is responsible for managing 0-db.

### Schema:

- `listenPort`: listen port (default 9900)
- `dataDir`: data file directory (default /zerodb/)
- `indexDir`: index file directory (default /zerodb/)
- `mode`: a value from enum Mode representing the 0-db mode.
- `sync`: boolean indicating whether all write should be sync'd or not.
- `container`: reference to the container running the zerodb. This is set by the template.
- `node`: reference to the node running the zerdb container
- `nodeMountPoint`: the node mountpoint that will be mounted at containerMountPoint.
- `containerMountPoint`: the container destination where hostMountPoint will be mounted.
- `admin`: admin password


Mode enum:
- `user`: the default user key-value mode.
- `seq`: sequential keys generated.
- `direct`: direct position by key.


### Actions
- `install`: create and start a container with 0-db.
- `start`: starts the container and the 0-db process. 
- `stop`: stops the 0-db process.
- `namespace_create`: create a new namespace. Only admin can do this.
- `namespace_info`: returns basic information about a namespace
- `namespace_list`: returns an array of all available namespaces.
- `namespace_set`: change a namespace setting/property. Only admin can do this.



### Usage example via the 0-robot DSL

```python
from zerorobot.dsl import ZeroRobotAPI
api = ZeroRobotAPI.ZeroRobotAPI()
robot = api.robots['main']

args = {
    'sync': True,
    'mode': 'user',
    'admin': 'password',
    'nodeMountPoint': '/mnt/zdb/zdb1',
    'containerMountPoint': '/zdb',
}
zdb = robot.services.create('github.com/zero-os/0-templates/zerodb/0.0.1', 'zerodb1', data=args)
zdb.schedule_action('install')

zdb.schedule_action('start')

zdb.schedule_action('namespace_list')
zdb.schedule_action('namespace_info', args={'name':'namespace'})
zdb.schedule_action('namespace_create', args={'name':'namespace'})
zdb.schedule_action('namespace_set', args={'name':'namespace', 'password': 'password'})

zdb.schedule_action('stop')
```


### Usage example via the 0-robot CLI

To install zerodb `zerodb1` on node `525400123456`:

```yaml
services:
    - github.com/zero-os/0-templates/zerodb/0.0.1__zerodb1:
          sync: True
          mode: 'user'
          admin: 'password'
          nodeMountPoint: '/mnt/zdb/zdb1'
          containerMountPoint: '/zdb'
          
actions:
    - template: 'github.com/zero-os/0-templates/zerodb/0.0.1'
      service: 'zerodb1'
      actions: ['install']

```


To start  zerodb `zerodb1`:

```yaml
actions:
    - template: 'github.com/zero-os/0-templates/zerodb/0.0.1'
      service: 'zerodb1'
      actions: ['start']

```


To stop  zerodb `zerodb1`:

```yaml
actions:
    - template: 'github.com/zero-os/0-templates/zerodb/0.0.1'
      service: 'zerodb1'
      actions: ['stop']

```

