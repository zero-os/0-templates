# template: github.com/zero-os/0-templates/erp_registeration/0.0.1

## Description:
This template is responsible for registering a node in odoo if it wasn't already registered.

## Schema:
- url: url of the odoo server
- db: name of the database
- username: username to use to connect to odoo
- password: password to use to connect to odoo
- bot_token: token of the telegram bot to be use to send the telegram message
- chat_id: id of the telegram groupchat to send the message to


## Actions:

### Register
Register a node in model `stock.production.lot`.

Arguments:
- node_id: the name of the node service.
- zerotier_address: zerotier address of the node

```python
args = {
    'url': 'odoo_url',
    'db': 'test',
    'username': 'user',
    'password': 'password',
    'bot_token': 'XomAJANa',
    'chat_id': '1823737123',
}
erp = self.api.services.create('github.com/zero-os/0-templates/erp_registeration/0.0.1', 'erp', args)
erp.schedule_action('register', args={'node_id':'node1', 'zerotier_address': 'xAJKAHam'})
```