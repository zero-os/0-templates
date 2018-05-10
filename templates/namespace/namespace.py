from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError
from zerorobot.service_collection import ServiceNotFoundError

ZERODB_TEMPLATE_UID = 'github.com/zero-os/0-templates/zerodb/0.0.1'


class Namespace(TemplateBase):

    version = '0.0.1'
    template_name = "namespace"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        if not self.data.get('password'):
            self.data['password'] = j.data.idgenerator.generateXCharID(32)

    def validate(self):
        try:
            # ensure that a node service exists
            node = self.api.services.get(template_account='zero-os', template_name='node')
            node.state.check('actions', 'install', 'ok')
        except:
            raise RuntimeError("not node service found, can't install the namespace")

        for param in ['disktype', 'size', 'mode']:
            if not self.data.get(param):
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))

    @property
    def _zerodb(self):
        return self.api.services.get(template_uid=ZERODB_TEMPLATE_UID, name=self.data['zerodb'])

    def install(self):
        node = self.api.services.get(template_account='zero-os', template_name='node')
        kwargs = {
            'disktype': self.data['disktype'].upper(),
            'mode': self.data['mode'],
            'password': self.data['password'],
            'public': self.data['public'],
            'size': self.data['size'],
        }
        # use the method on the node service to create the zdb and the namespace.
        # this action hold the logic of the capacity planning for the zdb and namespaces
        self.data['zerodb'], self.data['ns_name'] = node.schedule_action('create_zdb_namespace', kwargs).wait(die=True).result
        self.state.set('actions', 'install', 'ok')

    def info(self):
        self.state.check('actions', 'install', 'ok')
        return self._zerodb.schedule_action('namespace_info', args={'name': self.data['ns_name']}).wait(die=True).result

    def url(self):
        self.state.check('actions', 'install', 'ok')
        return self._zerodb.schedule_action('namespace_url', args={'name': self.data['ns_name']}).wait(die=True).result

    def private_url(self):
        self.state.check('actions', 'install', 'ok')
        return self._zerodb.schedule_action('namespace_private_url', args={'name': self.data['ns_name']}).wait(die=True).result

    def uninstall(self):
        self.state.check('actions', 'install', 'ok')
        self._zerodb.schedule_action('namespace_delete', args={'name': self.data['ns_name']}).wait(die=True)
        self.state.delete('actions', 'install')

    def connection_info(self):
        self.state.check('actions', 'install', 'ok')
        return self._zerodb.schedule_action('connection_info').wait(die=True).result
