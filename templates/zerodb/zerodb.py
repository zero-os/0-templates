from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError
from zerorobot.service_collection import ServiceNotFoundError


NODE_TEMPLATE_UID = 'github.com/zero-os/0-templates/node/0.0.1'
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
    def _zerodb_sal(self):
        data = self.data.copy()
        data['name'] = self.name
        return self._node_sal.primitives.from_dict('zerodb', data)

    def _deploy(self):
        zerodb_sal = self._zerodb_sal
        zerodb_sal.deploy()
        self.data['nodePort'] = zerodb_sal.node_port
        self.data['ztIdentity'] = zerodb_sal.zt_identity

    def install(self):
        self.logger.info('Installing zerodb %s' % self.name)

        # generate admin password
        if not self.data['admin']:
            self.data['admin'] = j.data.idgenerator.generateXCharID(25)

        self._deploy()
        self.state.set('actions', 'install', 'ok')
        self.state.set('actions', 'start', 'ok')

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
        self.state.check('actions', 'start', 'ok')
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
        if not self._namespace_exists_update_delete(name):
            raise ValueError('Namespace {} doesn\'t exist'.format(name))
        return self._zerodb_sal.namespaces[name].info().to_dict()

    def namespace_create(self, name, size=None, password=None, public=True):
        """
        Create a namespace and set the size and secret
        :param name: namespace name
        :param size: namespace size
        :param password: namespace password
        :param public: namespace public status
        """
        self.state.check('actions', 'start', 'ok')
        if self._namespace_exists_update_delete(name):
                raise ValueError('Namespace {} already exists'.format(name))
        self.data['namespaces'].append({'name': name, 'size': size, 'password': password, 'public': public})
        self._zerodb_sal.deploy()

    def namespace_set(self, name, prop, value):
        """
        Set a property of a namespace
        :param name: namespace name
        :param prop: property name
        :param value: property value
        """
        self.state.check('actions', 'start', 'ok')

        if not self._namespace_exists_update_delete(name, prop, value):
            raise ValueError('Namespace {} doesn\'t exist'.format(name))
        self._zerodb_sal.deploy()

    def namespace_delete(self, name):
        """
        Delete a namespace
        """
        self.state.check('actions', 'start', 'ok')
        if not self._namespace_exists_update_delete(name, delete=True):
            raise ValueError('Namespace {} doesn\'t exist'.format(name))

        self._zerodb_sal.deploy()

    def connection_info(self):
        return {
            'ip': self._node_sal.public_addr,
            'port': self.data['nodePort']
        }

    def _namespace_exists_update_delete(self, name, prop=None, value=None, delete=False):
        if prop and delete:
            raise RuntimeError('Can\'t set property and delete at the same time')
        if prop and prop not in ['size', 'password', 'public']:
            raise ValueError('Property must be size, password, or public')

        for namespace in self.data['namespaces']:
            if namespace['name'] == name:
                if prop and delete:
                    raise RuntimeError('Can\'t set property and delete at the same time')
                if prop:
                    if prop not in ['size', 'password', 'public']:
                        raise ValueError('Property must be size, password, or public')
                    namespace[prop] = value
                if delete:
                    self.data['namespaces'].remove(namespace)
                return True
        return False
