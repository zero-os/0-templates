## template: github.com/zero-os/0-templates/zerodb/0.0.1

### Description:
This template is responsible for managing 0-db.

### Schema:

- `mode`: a value from enum Mode representing the 0-db mode.
- `sync`: boolean indicating whether all write should be sync'd or not.
- `disk`: path of the disk to use
- `nodePort`: the node port used in port forwarding
- `admin`: admin password. Set by the template if not supplied.

Mode enum:
- `user`: the default user key-value mode.
- `seq`: sequential keys generated.
- `direct`: direct position by key.


### Actions
- `start`: starts the container and the 0-db process. 
- `stop`: stops the 0-db process.
- `namespace_create`: create a new namespace. Only admin can do this.
- `namespace_info`: returns basic information about a namespace
- `namespace_list`: returns an array of all available namespaces.
- `namespace_set`: change a namespace setting/property. Only admin can do this.
- `free_space`: return the amount of storage space still available for reservation