## template: github.com/zero-os/0-templates/ssh_client/0.0.1

### Description:

This template is responsible for configuring the ssh client on jumpscale. Initializing a service from this templates creates a client with the provided configuration.

If the client with instance name already already exists, that instance will be used

### Schema:

- `host`: target host address
- `port`: target port
- `login`: ssh username/login
- `password`: ssh password

### Actions:

- `delete`: delete the client from jumpscale and the service
