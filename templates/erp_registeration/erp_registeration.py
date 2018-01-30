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

    def register(self, node_id, zerotier_address):
        import erppeek

        conn = HTTPSConnection('api.telegram.org')

        botid = self.data['botid']
        chatid = self.data['chatid']
        url = self.data['url']
        db = self.data['db']
        username = self.data['username']
        password = self.data['password']
        productid = self.data['productid']
        message = "Node with id {} and zerotier address {} is successfully registered in Odoo.".format(
            node_id, zerotier_address)
        # do registration
        try:
            client = erppeek.Client(url, db, username, password)
            lot = client.model('stock.production.lot')
            # check if not yet registered
            if lot.count([['name', '=', node_id]]) == 0:
                lot.create({'name': node_id, 'product_id': productid})
                self.logger.info("Odoo registration succeeded")
            else:
                self.logger.info("Odoo registration: node already registered")

        except Exception as err:
            message = "Node with id {} and zerotier address {} has failed the Odoo registration: {}".format(
                node_id, zerotier_address, str(err))
            raise j.exceptions.RuntimeError(message)
        finally:
            url = "/bot{}/sendMessage?chat_id={}&text={}".format(
                botid, chatid, message)
            conn.request("GET", url)
