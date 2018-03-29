from js9 import j

from zerorobot.template.base import TemplateBase


class ZeroosClient(TemplateBase):

    version = '0.0.1'
    template_name = "zeroos_client"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

        # client instance already exists
        if self.name in j.clients.zero_os.list():
            return

        # create the client instance
        if not self.data.get('host'):
            raise ValueError('no host specified in service data')

        print(self.data)
        client_data = {
            'host': self.data['host'],
            'port': self.data['port'],
            'password_': self.data['password'],
            'ssl': self.data['ssl'],
            'db': self.data['db'],
            'timeout': self.data['timeout'],
        }
        # this will create a configuration for this instance
        _ = j.clients.zero_os.get(self.name, data=client_data)

    def delete(self):
        """
        delete the client configuration
        """
        j.clients.zero_os.delete(self.name)
        # call the delete of the base class
        super().delete()
