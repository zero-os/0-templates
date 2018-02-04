from js9 import j

from zerorobot.template.base import TemplateBase

from http.client import HTTPSConnection


class ErpRegisteration(TemplateBase):

    version = '0.0.1'
    template_name = 'hardware_check'

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._validate_input()
        j.tools.prefab.local.bash.executor.execute('pip install erppeek')

    def _validate_input(self):
        for param in ['url', 'db', 'username', 'password', 'productid', 'botid', 'chatid']:
            if not self.data[param]:
                raise ValueError("parameter '%s' not valid: %s",
                                 str(self.data[param]))

    def _get_erp_client(self):
        data = {
            'url': self.data['url'],
            'db': self.data['db'],
            'password_': self.data['password'],
            'username': self.data['username'],
        }
        # make sure the config exists
        cl = j.clients.erppeek.get(
            instance=self.guid,
            data=data,
            create=True,
            die=True)

        # update the config with correct value
        cl.config.data.update(data)
        cl.config.save()

        return cl

    def _get_bot_client(self):
        data = {
            'bot_token_': self.data['botid'],
        }
        # make sure the config exists
        cl = j.clients.telegram_bot.get(
            instance=self.guid,
            data=data,
            create=True,
            die=True)

        # update the config with correct value
        cl.config.data.update(data)
        cl.config.save()

        return cl

    def register(self, node_id, zerotier_address):
        productid = self.data['productid']
        message = "Node with id {} and zerotier address {} is successfully registered in Odoo.".format(
            node_id, zerotier_address)
        # do registration
        try:
            cl = self._get_erp_client()

            # check if not yet registered
            model_name = 'stock.production.lot'
            if cl.count_records(model_name, [['name', '=', node_id]]) == 0:
                cl.create_record(model_name, {'name': node_id, 'product_id': productid})
                self.logger.info("Odoo registration succeeded")
            else:
                self.logger.info("Odoo registration: node already registered")

        except Exception as err:
            message = "Node with id {} and zerotier address {} has failed the Odoo registration: {}".format(
                node_id, zerotier_address, str(err))
            raise j.exceptions.RuntimeError(message)
        finally:
            bot_cl = self._get_bot_client()
            bot_cl.send_message(self.data['chatid'], message)
