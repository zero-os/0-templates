## template: github.com/zero-os/0-templates/hypervisor/0.0.1

### Description:
This template is responsible for managing a zero-os kvm hypervisor.

### Schema:

- `node`: the name of the node the hypervisor is on
- `vm`: the name of the vm


### Actions

- `create`: creates a hypervisor on a zeroos node

    Arguments:
    - `media`:
    - `flist`:
    - `cpu`:
    - `memory`:
    - `nics`:
    - `port`: 
    - `mount`:
    - `tags`

- `destroy`: destroys the hypervisor  
- `shutdown`': shuts down the hypervisor
- `pause`: pause the hypervisor 
- `resume`: resume the hypervisor
- `reboot`: reboot the hypervisor
- `reset`: reset the hypervisor
