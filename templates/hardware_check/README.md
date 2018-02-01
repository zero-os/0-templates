# template: github.com/zero-os/0-templates/hardware_check/0.0.1

## Description:
This template is responsible for checking if the hardware specs of a node matches the expected specs and sending a message to a telegram chat with the result of the check.

## Schema:
- numhdd: expected number of hdds
- numssd: expected number of ssds
- ram: expected amount of ram (in mibi bytes - MiB)
- cpu: model name of expected cpu
- bot_token: token of the telegram bot to be use to send the telegram message
- chat_id: id of the telegram groupchat to send the message to


### Check
Checks the hardware specs of a specific node and the message accordingly.

Arguments:
- node_name: the name of the node service.

## Example to check hardware specs of node node1

```python
args = {
    'numhdd': 2,
    'numssd': 2,
    'ram': 7150,
    'cpu': 'intel',
    'bot_token': 'thisisabottoken',
    'chat_id': '1823737123',
}
hw_check= self.api.services.create('github.com/zero-os/0-templates/hardware_check/0.0.1', 'hw_check', args)
hw_check.schedule_action('check', args={'node_name':'node1'})
```