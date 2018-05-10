## template: github.com/zero-os/0-templates/namespace/0.0.1

### Description:
This template is responsible for managing a 0-db namespace

### Schema:

- `zerodb`: the zerodb to create the namespace on
- `size`: the namespace size
- `password`: The namespace password **optional**

### Actions
- `install`: creates the namespace.
- `info`: returns info about the namespace. 
- `url`: return the public url of the namespace
- `private_url`: return the private url of the namespace

### Usage example via the 0-robot DSL

```python
from zerorobot.dsl import ZeroRobotAPI

robot = j.clients.zrobot.robots['main']

args = {
    'zerodb': 'zerodb_one',
    'size': 10,
    'password': 'password',
}
namespace = robot.services.create('github.com/zero-os/0-templates/namespace/0.0.1', 'namespace_one', data=args)
namespace.schedule_action('install')
namespace.schedule_action('info')
```


### Usage example via the 0-robot CLI

To create namespace `namespace_one`:

```yaml
services:
    - github.com/zero-os/0-templates/namespace/0.0.1__namespace_one:
          zerodb: 'zerodb_one'
          size: 10
          password: 'password'
          
actions:
    - template: 'github.com/zero-os/0-templates/namespace/0.0.1'
      service: 'namespace_one'
      actions: ['install']

```


To get info for namespace `namespace_one`:

```yaml
actions:
    - template: 'github.com/zero-os/0-templates/namespace/0.0.1'
      service: 'namespace_one'
      actions: ['info']

```