## ZeroMD
### Description

This template is responsible for deploying a 0-metadatastor (see: [0-metadata](https://github.com/zero-os/0-metadata))

### Schema:
 - **node**: node to install the 0-metadata on 
 - **port**: port for 0-metadata to run on
 - **ardb.cluster**: service guid of ARDB cluster

### Actions:
 - **install**: installs 0-metadata on configured node
 - **configure**: configures 0-metadata to connect to ARDB cluster
 - **start**: starts 0-metadata on configured port
 - **stop**: stops 0-metadata 

### Blueprint example:
```yaml
services:
    - github.com/jumpscale/0-robot/node/0.0.1__node:
        id: '00:00:00:00' # mac address of the mngt network card
        hostname: 'hostnode'
        redis.addr: 'localhost' # redis addr for client
        redis.port: 6379 # redis port for client
        redis.password: '' # redis password for client

    - github.com/zero-os/0-templates/zeromd/0.0.1__zeromd:
        node: node
        port: 666
        ardb.cluster: 'ardbcluster'


actions:
    template: github.com/jumpscale/0-robot/zeromd/0.0.1
    actions: ['install', 'start']
```
