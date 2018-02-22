## template: github.com/zero-os/0-templates/zerodb/0.0.1

### Description:
This template is responsible for managing 0-db.

### Schema:

- `listenAddr`: listen address (default 0.0.0.0)
- `listenPort`: listen port (default 9900)
- `dataDir`: data file directory (default ./data)
- `indexDir`: index file directory (default ./index)
- `mode`: a value from enum Mode representing the 0-db mode.
- `sync`: boolean deciding whether all write should be sync'd or not.
- `container`: reference to the container running the zerodb.


Mode enum:
- `user`: the default user key-value mode.
- `seq`: sequential keys generated.
- `direct`: direct position by key.


### Actions
- `install`: install creates a container with the 0-db flist.
- `start`: starts the container and the 0-db process. 
- `stop`: stops the container and the 0-db process.
