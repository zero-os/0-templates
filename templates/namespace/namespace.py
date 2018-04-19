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

    def validate(self):
        for param in ['zerodb', 'size']:
            if not self.data.get(param):
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))

    @property
    def _zerodb(self):
        return self.api.services.get(template_uid=ZERODB_TEMPLATE_UID, name=self.data['zerodb'])

    def install(self):
        args = {
            'name': self.name,
            'size': self.data['size'],
            'secret': self.data['secret'],
        }
        self._zerodb.schedule_action('namespace_create', args=args).wait(die=True)
        self.state.set('actions', 'install', 'ok')

    def info(self):
        self.state.check('actions', 'install', 'ok')
        task = self._zerodb.schedule_action('namespace_info', args={'name': self.name})
        task.wait(die=True)

        return task.result

    def uninstall(self):
        self.state.check('actions', 'install', 'ok')
        self._zerodb.schedule_action('namespace_delete', args={'name': self.name}).wait(die=True)

