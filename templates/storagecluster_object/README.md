## template: github.com/zero-os/0-templates/storagecluster_object/0.0.1

### Description:
This template is responsible for managing a storage cluster

### Schema:

- `label`: storage cluster label
- `status`: a value from status enum denoting the cluster status.
- `nrServer`: number of zerodb servers needed.

Status enum:
- `empty`
- `deploying`
- `ready`
- `error`
- `halting`


### Actions
- `install`: install creates a storage cluster and all the zerodb services.
- `start`: starts the storage cluster and all the zerodb services.
- `stop`: stops the cluster and all the zerodb services.
