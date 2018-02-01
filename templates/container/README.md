# template: github.com/zero-os/0-templates/container/0.0.1

## Description:
This template is responsible for creating a container on zero-os nodes

## Schema:

- node: name of the parent node
- hostname: container hostname
- flist: url of the root filesystem flist
- initProcesses: a list of type Processes. These are the processes to be started once the container starts.
- nics: a list of type Nics. It specifies the configuration of the attached nics to the container.
- hostNetworking: a boolean if set to true will make the node networking available to the container.
- ports: a list of node-to-container ports mappings. e.g: 8080:80
- storage: ??
- mounts: a list of type Mount mapping mount points fron the node to the container.
- zerotiernodeid: The node's zerotier network id.
- privileged: a boolean indicating whether this will be a privileged container or not.
- identity: ??


### Install
Installs a container on the node, starts it and runs all the processes in initProcesses.

### Start
Starts a container

### Uninstall
Stops the container

