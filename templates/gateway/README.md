## template: github.com/zero-os/0-templates/gateway/0.0.1

### Description:
This template is responsible for creating a gateway on zero-os nodes
It configures caddy, dnsmasq, nftables and cloud-init to work together to provide gateway services

### Schema:

- `hostname`: container hostname.
- `domain`: Domain for the private networks
- `nics`: a list of type Nics. It specifies the configuration of the attached nics to the container.
- `portforwards`: tcp/udp forwards from public network to private network
- `httpproxies`: Reverse http/https proxy to allow one public ip to host multiple http services

Portforwards:
- `protocols`: tcp or udp
- `srcport`: Port to forward from
- `srcip`: IPAddress to forward from
- `dstip`: IPAddress to forward to
- `dstport`: Port to forward to

Nic:
- `type`: value from enum NicType indicating the nic type. 
- `id`: vxlan or vlan id.
- `config`: a dict of NicConfig.
- `name`: nic's name.
- `token`: zerotier token for Nic of type zerotier.
- `hwaddr`: hardware address.
- `dhcpsever`: Config for dhcp entries to be services for this nic.

NicConfig:
- `dhcp`: boolean indicating to use dhcp or not.
- `cidr`: cidr for this nic.
- `gateway`: gateway address
- `dns`: list of dns

NicType enum:
- `default`
- `zerotier`
- `vlan`
- `vxlan`
- `bridge`

DHCPServer:
- `nameservers`: IPAddresses of upstream dns servers
- `hosts`: Host entries to provided leases for

Host:
- `hostname`: Hostname to pass to lease info
- `macaddress`: MACAddress used to identify lease info
- `ipaddress`: IPAddress service for this host
- `ip6address`: IP6Address service for this host
- `cloudinit`: Cloud-init data for this host

CloudInit:
- `userdata`: Userdata as string (yaml string)
- `metadata`: Metadata as string (yaml string)

### Actions:
- `install`: creates a gatewa on a node, starts it and configures all services
- `start`: start a gateway
- `stop`: stops a gateway
- `add_portforward`: Adds a portforward to the firewall
- `remove_portforward`: Removes a portforward from the firewall
- `add_http_porxy`: Adds a httpproxy to the http server
- `remove_http_porxy`: Removes a httpproxy from the http server
- `add_dhcp_host`: Adds a host to a dhcp server
- `remove_dhcp_host`: Remove a host from a dhcp server
- `add_nic`: Adds a nic to the gateway
- `remove_nic`: Remove a nic from the gateway
