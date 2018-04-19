from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError
from zerorobot.service_collection import ServiceNotFoundError

CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
NODE_TEMPLATE_UID = 'github.com/zero-os/0-templates/node/0.0.1'
ZERODB_FLIST = 'https://hub.gig.tech/gig-autobuilder/zero-os-0-db-master.flist'
NODE_CLIENT = 'local'


class Zerodb(TemplateBase):

    version = '0.0.1'
    template_name = "zerodb"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    @property
    def _node_sal(self):
        # hardcoded local instance, this service is only intended to be install by the node robot
        return j.clients.zero_os.sal.get_node(NODE_CLIENT)

    @property
    def _container_sal(self):
        return self._node_sal.containers.get(self._container_name)

    @property
    def _zerodb_sal(self):
        kwargs = {
            'name': self.name,
            'container': self._container_sal,
            'port': 9900,
            'data_dir': '/zerodb/data',
            'index_dir': '/zerodb/index',
            'mode': self.data['mode'],
            'sync': self.data['sync'],
            'admin': self.data['admin'],
        }
        return j.clients.zero_os.sal.get_zerodb(**kwargs)

    @property
    def _container_data(self):
        ports = self._node_sal.freeports(9900, 1)
        if len(ports) <= 0:
            raise RuntimeError("can't install 0-db, no free port available on the node")

        self.data['nodePort'] = ports[0]
        mounts = {
            'source': self.data['disk'],
            'target': '/zerodb',
        }

        return {
            'flist': ZERODB_FLIST,
            'mounts': [mounts],
            'ports': ['%s:%s' % (self.data['nodePort'], 9900)],
            'nics': [{'type': 'default'}],
        }

    @property
    def _container_name(self):
        return 'container_zdb_%s' % self.guid

    def install(self):
        self.logger.info('Installing zerodb %s' % self.name)

        # generate admin password
        if not self.data['admin']:
            self.data['admin'] = j.data.idgenerator.generateXCharID(25)

        container = self.api.services.find_or_create(CONTAINER_TEMPLATE_UID, self._container_name, data=self._container_data)
        container.schedule_action('install').wait(die=True)
        self.state.set('actions', 'install', 'ok')

    def start(self):
        """
        start zerodb server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Starting zerodb %s' % self.name)
        container = self.api.services.find_or_create(CONTAINER_TEMPLATE_UID, self._container_name, data=self._container_data)

        try:
            container.state.check('actions', 'install', 'ok')
        except StateCheckError:
            container.schedule_action('install').wait(die=True)
        container.schedule_action('start').wait(die=True)

        self._zerodb_sal.start()
        self._node_sal.client.nft.open_port(self.data['nodePort'])
        self.state.set('actions', 'start', 'ok')

    def stop(self):
        """
        stop zerodb server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Stopping zerodb %s' % self.name)

        self._zerodb_sal.stop()

        self._node_sal.client.nft.drop_port(self.data['nodePort'])

        try:
            container = self.api.services.get(self._container_name)
            container.schedule_action('stop').wait(die=True)
            container.delete()
        except ServiceNotFoundError:
            # container is already done, nothing else to do
            pass

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
        return self._zerodb_sal.list_namespaces()

    def namespace_info(self, name):
        """
        Get info of namespace
        :param name: namespace name
        :return: dict
        """
        self.state.check('actions', 'start', 'ok')
        return self._zerodb_sal.get_namespace_info(name)

    def namespace_create(self, name, size=None, secret=None):
        """
        Create a namespace and set the size and secret
        :param name: namespace name
        :param size: namespace size
        :param secret: namespace secret
        """
        self.state.check('actions', 'start', 'ok')
        self._zerodb_sal.create_namespace(name)
        if size:
            self._zerodb_sal.set_namespace_property(name, 'maxsize', size)
        if secret:
            self._zerodb_sal.set_namespace_property(name, 'password', secret)

    def namespace_set(self, name, prop, value):
        """
        Set a property of a namespace
        :param name: namespace name
        :param prop: property name
        :param value: property value
        """
        self.state.check('actions', 'start', 'ok')
        self._zerodb_sal.set_namespace_property(name, prop, value)

    def namespace_delete(self, name):
        """
        Delete a namespace
        """
        self.state.check('actions', 'install', 'ok')
        return self._zerodb_sal.delete_namespace(name)
