## template: github.com/zero-os/0-templates/zrobot/0.0.1

### Description:

This template will start a 0-robot on a node inside a container. 

### schema:

- `node`: name of the node service.

- `templates`: 0-robot repo templates to be loaded on process starts.

- `organization`: optional, if specified enable JWT authentication for this organization

- `nics`: configuration of the attached nics to the container. If left empty will use default nic and create a port forward on the container exposing the 0-robot port.

### Actions

- `install`: will create a container using the 0-robot flist and will run 0-robot inside the container.

- `uninstall`: will stop the running 0-robot process, delete the container and delete the persistent data of the robot.

- `start`: start the 0-robot process

- `stop`: stop the 0-robot process


### Usage example via the 0-robot DSL

```python
from zerorobot.dsl import ZeroRobotAPI
api = ZeroRobotAPI.ZeroRobotAPI()
robot = api.robots['main']

args = {
    'node': '525400123456',
    'templates': ["https://github.com/zero-os/0-templates.git"],
}
zrobot = robot.services.create('github.com/zero-os/0-templates/zrobot/0.0.1', 'zrobot', data=args)
zrobot.schedule_action('install')

zrobot.schedule_action('start')
zrobot.schedule_action('stop')
zrobot.schedule_action('uninstall')
```

### Usage example via the 0-robot CLI

To deploy 0-robot `robot2` on the node `525400123456`:

```yaml
services:
- github.com/zero-os/0-templates/zrobot/0.0.1__robot2:
    node: "525400123456"
    templates: ["https://github.com/zero-os/0-templates.git"]

actions:
    - actions: ['install']

```

To start 0-robot `robot2`:

```yaml
actions:
    - template: 'github.com/zero-os/0-templates/zrobot/0.0.1'
      service: 'robot2'
      actions: ['start']
```

To stop 0-robot `robot2`:

```yaml
actions:
    - template: 'github.com/zero-os/0-templates/zrobot/0.0.1'
      service: 'robot2'
      actions: ['stop']

```

To uninstall 0-robot `robot2`:

```yaml
actions:
    - template: 'github.com/zero-os/0-templates/zrobot/0.0.1'
      service: 'robot2'
      actions: ['uninstall']

```

