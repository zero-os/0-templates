## template: github.com/zero-os/0-templates/container/0.0.1

### Description:
This template is responsible for creating a container on zero-os nodes

### Schema:

- `node`: name of the parent node
- `hostname`: container hostname
- `flist`: url of the root filesystem flist
- `initProcesses`: a list of type Processes. These are the processes to be started once the container starts.
- `nics`: a list of type Nics. It specifies the configuration of the attached nics to the container.
- `hostNetworking`: a boolean if set to true will make the node networking available to the container.
- `ports`: a list of node-to-container ports mappings. e.g: 8080:80
- `storage`: ??
- `mounts`: a list of type Mount mapping mount points from the node to the container.
- `zerotierNetwork`: The node's zerotier network id.
- `privileged`: a boolean indicating whether this will be a privileged container or not.
- `identity`: ??

Mount:
- `filesystem`: instance name of the filesystem service.
- `target`: the mount target of this filesystem in the container.

Process:
- `name`: name of the executable.
- `pwd`: directory in which the process needs to be started.
- `args`: list of the process' command line arguments.
- `environment`: list of environment variables for the process e.g ['PATH=/usr/bin/local'].
- `stdin`: data that needs to be passed into the stdin of the started process.
- `id`: ??

Nic:
- `type`: value from enum NicType indicating the nic type. 
- `id`: vxlan or vlan id
- `config`: a dict of NicConfig
- `name`: nic's name
- `token`: zerotier token for Nic of tyoe zerotier
- `hwaddr`: ??

NicConfig:
- `dhcp`: 
- `cidr`: cidr for this nic
- `gateway`:
- `dns`: list of dns

NicType enum:
- `default`
- `zerotier`
- `vlan`
- `vxlan`
- `bridge`


### Actions:
- `install`: creates a container on a node, starts it and runs all the processes in initProcesses
- `start`: start a container and run all the initProcesses
- `stop`: stops a container
