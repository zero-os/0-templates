
from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.decorator import retry, timeout
from zerorobot.template.state import StateCheckError
import netaddr

NODE_CLIENT = 'local'

class CapacityBeat(TemplateBase):

    version = '0.0.1'
    template_name = 'capacity_beat'

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self.schedule_action("install")
        self.recurring_action('_register', 5)  # every 30 seconds .. update to 2 mins.

    def install(self):
        self.state.set('actions', 'install', 'ok')

    @property
    def node_sal(self):
        """
        connection to the node
        """
        return j.clients.zos.sal.get_node(NODE_CLIENT)

    @retry(RuntimeError, tries=5, delay=5, backoff=2)
    def _register(self):
        """
        register the capacity
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info("register node capacity")
        # TODO:
        # implement TTL for the data registered, so if the node is not online anymore
        # the capacity will not be visible anymore until the node is up again
        self.node_sal.capacity.register()