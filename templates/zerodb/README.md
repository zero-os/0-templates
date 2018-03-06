## template: github.com/zero-os/0-templates/zerodb/0.0.1

### Description:
This template is responsible for managing 0-db.

### Schema:

- `listenAddr`: listen address (default 0.0.0.0)
- `listenPort`: listen port (default 9900)
- `dataDir`: data file directory (default /zerodb/data)
- `indexDir`: index file directory (default /zerodb/index)
- `mode`: a value from enum Mode representing the 0-db mode.
- `sync`: boolean deciding whether all write should be sync'd or not.
- `container`: reference to the container running the zerodb.
- `nodeMountPoint`: the node mountpoint that will be mounted at containerMountPoint.
- `containerMountPoint`: the container destination where hostMountPoint will be mounted.


Mode enum:
- `user`: the default user key-value mode.
- `seq`: sequential keys generated.
- `direct`: direct position by key.


### Actions
- `start`: starts the container and the 0-db process. 
- `stop`: stops the container and the 0-db process.
- `namespace_create`: create a new namespace. Only admin can do this.
- `namespace_info`: returns basic information about a namespace
- `namespace_list`: returns an array of all available namespaces.
- `namespace_set`: change a namespace setting/property. Only admin can do this.
