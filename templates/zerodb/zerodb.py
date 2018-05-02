from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError
from zerorobot.service_collection import ServiceNotFoundError

CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
NODE_TEMPLATE_UID = 'github.com/zero-os/0-templates/node/0.0.1'
# user this for development
ZERODB_FLIST = 'https://hub.gig.tech/gig-autobuilder/rivine-0-db-master.flist'
#ZERODB_FLIST = 'https://hub.gig.tech/gig-autobuilder/rivine-0-db-release-master.flist'
NODE_CLIENT = 'local'


class Zerodb(TemplateBase):

    version = '0.0.1'
    template_name = "zerodb"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._zdb_sal = None

    @property
    def _node_sal(self):
        # hardcoded local instance, this service is only intended to be install by the node robot
        return j.clients.zero_os.sal.get_node(NODE_CLIENT)

    @property
    def _zerodb_sal(self):
        if not self._zdb_sal:
            self._zdb_sal = self._node_sal.primitives.create_zerodb(self.name)
        self._zdb_sal.from_dict(self.data)
        return self._zdb_sal

    def _deploy(self):
        self._zerodb_sal.deploy()
        self.data['nodePort'] = self._zerodb_sal.node_port

    def install(self):
        self.logger.info('Installing zerodb %s' % self.name)

        # generate admin password
        if not self.data['admin']:
            self.data['admin'] = j.data.idgenerator.generateXCharID(25)

        self._deploy()
        self.state.set('actions', 'install', 'ok')

    def start(self):
        """
        start zerodb server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Starting zerodb %s' % self.name)
        self._deploy()
        self.state.set('actions', 'start', 'ok')

    def stop(self):
        """
        stop zerodb server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Stopping zerodb %s' % self.name)

        self._zerodb_sal.stop()
        self.state.delete('actions', 'start')

    def upgrade(self):
        """
        upgrade 0-db
        """
        self.stop()
        self.start()

    def namespace_list(self):
        """
        List namespace
        :return: list of namespaces ex: ['namespace1', 'namespace2']
        """
        self.state.check('actions', 'start', 'ok')
        return self.data['namespaces']

    def namespace_info(self, name):
        """
        Get info of namespace
        :param name: namespace name
        :return: dict
        """
        self.state.check('actions', 'start', 'ok')
        return self._zerodb_sal.namespaces[name].info().to_dict()

    def namespace_create(self, name, size=None, secret=None, public=True):
        """
        Create a namespace and set the size and secret
        :param name: namespace name
        :param size: namespace size
        :param secret: namespace secret
        :param public: namespace public status
        """
        self.state.check('actions', 'start', 'ok')
        namespace = self._zerodb_sal.namespaces.add(name, size, secret, public)
        namespace.deploy()

    def namespace_set(self, name, prop, value):
        """
        Set a property of a namespace
        :param name: namespace name
        :param prop: property name
        :param value: property value
        """
        self.state.check('actions', 'start', 'ok')
        self._zerodb_sal.namespaces[name].set_property(prop, value)
        self.data['namespaces'] = self._zerodb_sal.to_dict()['namespaces']

    def namespace_delete(self, name):
        """
        Delete a namespace
        """
        self.state.check('actions', 'install', 'ok')
        self._zerodb_sal.namespaces.remove(name)
        self._deploy()
        self.data['namespaces'] = self._zerodb_sal.to_dict()['namespaces']

    def connection_info(self):
        return {
            'ip': self._node_sal.public_addr,
            'port': self.data['nodePort']
        }