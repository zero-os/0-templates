## template: github.com/zero-os/0-templates/zeroboot_pool/0.0.1

### Description:

This template is responsible for keeping track of a pool of zeroboot hosts (zeroboot_ipmi_host or zeroboot_racktivity_host).

### Schema:

- zerobootHosts: A list of zeroboot instance names

### Actions:

- add: Add a zeroboot host to the pool
- remove: Remove a zeroboot host from the pool
- unreserved_host: Returns a zeroboot host instance that has not been reserved yet.  
It does this by checking which hosts in the pool do not have an installed reservation service (template: `github.com/zero-os/0-templates/zeroboot_reservation`)
