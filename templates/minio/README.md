## template: github.com/zero-os/0-templates/minio/0.0.1

### Description:
This template is responsible for managing [minio](https://minio.io/) server instance.

### Schema:

- `node`: name of the node service to where minio will be deployed
- `zdbs`: list of zerodbs endpoints used as backend for minio ex: ['192.168.122.87:9600']
- `namespace`: namespace name to use on the 0-db
- `nsSecret`: secret to use to have access to the namespace on the 0-db servers
- `login`: minio login. End user need to know this login to have access to minio
- `password`: minio password. End user need to know this login to have access to minio
- `container`: reference to the container on which minio will be running. This is set by the template
- `listenPort`: the port minio will bind to
- `resticRepo`: restic repo to create the bucket on and use for metadata backup
- `resticUsername`: restic username
- `resticPassword`: restic password
- `privateKey`: encryption private key


### Actions
- `install`: install the minio server. It will create a container on the node and run minio inside the container
- `start`: starts the container and the minio process. 
- `stop`: stops minio process.
- `uninstall`: stop the minio server and remove the container from the node. Executing this action will make you loose all data stored on minio