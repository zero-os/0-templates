## template: github.com/zero-os/0-templates/zeroboot_reservation/0.0.1

### Description:

This template is responsible for marking a zeroboot host (zeroboot_ipmi_host or zeroboot_racktivity_host) as reserved.  
It also acts as a proxy for the zeroboot host.

### Schema:

- zerobootPool: zeroboot pool where it can look for available hosts
- ipxeUrl: URL to ipxe boot script

### Actions:

- install: Fetches an available host from the pool and marks it as reserved. Also tries to power on the host
- uninstall: powers off the host and marks the host as available again.
- host: returns the hostname of the reservation
- power_on: proxy to the zeroboot host to power on the host
- power_off: proxy to the zeroboot host to power off the host
- power_cycle: proxy to the zeroboot host to power cycle the host
- power_status: proxy to the zeroboot host to return the power status of the host (True if on, False if off)
- monitor: proxy to the zeroboot host to check if the power status on the host matches the last set by the host template
- configure_ipxe_boot: proxy to the zeroboot host to set the ipxe boot url
