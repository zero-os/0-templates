## 0-MDStor Spec/Documentation

### Blueprint example:
```yaml
services:
    - github.com/jumpscale/0-robot/node/0.0.1__node:
        id: '00:00:00:00' # mac address of the mngt network card
        hostname: 'hostnode'
        redis.addr: 'localhost' # redis addr for client
        redis.port: 6379 # redis port for client
        redis.password: '' # redis password for client

    - github.com/zero-os/0-templates/0-mdstor/0.0.1__zeromd:
        node: node
        port: 666
        ardb.cluster: 'ardbcluster'


actions:
    template: github.com/jumpscale/0-robot/0-mdstor/0.0.1
    actions: ['install', 'start']
```


### template internals:
- **schema.capnp**
    ```capnp
    @0xc5ba0f64c9013a80;

    struct Schema {
        node @0 :Text;
        port @1 :UInt32;
        ardb.cluster @2 :Text;
    }
    ```
- **zeromd.py**
    ```python
    from zerorobot.template.base import TemplateBase


    class zeromd(TemplateBase):
        # define the verion of this template
        version = '0.0.1'
        template_name = "zeromd"

        def __init__(self, name=None, guid=None, data=None):
            super().__init__(name=name, guid=guid, data=data)


        def _configure(self):
            """
            configures 0-metadata to connect to ardb cluster
            """
            raise NotImplementedError()

        def install(self):
            """
            installs the 0-metadatastor on the node
            """
            self.configure()
            raise NotImplementedError()

        def start(self):
            """
            starts 0-metadata on configured port
            """
            raise NotImplementedError()

        def stop(self):
            """
            stops 0-metadata
            """
            raise NotImplementedError()

    ```
