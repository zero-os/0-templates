# template: github.com/zero-os/0-templates/zerotier_client/0.0.1

## Description:
This template is responsible for configuring the zerotier client on jumpscale. Initializing a service from this templates creates a client with the correct configuration.

## Schema:

- token: the token for the zerotier api


### Delete
Deletes the client from jumpscale.


### Example for creating a zerotier client using the api

```python
args = {
    'token': 'Ximdhaua',
}
zt = self.api.services.create('github.com/zero-os/0-templates/zerotier_client/0.0.1', 'client', args)
```