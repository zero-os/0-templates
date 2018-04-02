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

Following yaml file is to install the node service:

```yaml
services:
- github.com/zero-os/0-templates/node/0.0.1__525400123456:
    redisAddr: 172.17.0.1
    redisPort: 6379
    hostname: "myzeros"
    alerta: ['reporter']

actions:
    - actions: ['install']
```

To deploy 0-robot on the node:

```yaml
services:
- github.com/zero-os/0-templates/zrobot/0.0.1__robot2:
    node: "525400123456"
    templates: ["https://github.com/zero-os/0-templates.git"]

actions:
    - actions: ['install']

```