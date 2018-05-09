## template: github.com/zero-os/0-templates/zeroboot_client/0.0.1

### Description:

This template is responsible for configuring the zeroboot client on jumpscale. Initializing a service from this templates creates a client with the provided configuration.

If the client with instance name already already exists, that instance will be used.

### Schema:

- `networkId`: Zerotier network ID
- `sshClient`: ssh jumpscale client instance name
- `zerotierClient`: zerotier jumpscale client instance name

### Actions:

- `delete`: delete the client from jumpscale and the service
