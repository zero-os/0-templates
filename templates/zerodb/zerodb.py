from js9 import j

from zerorobot.template.base import TemplateBase


CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
ZERODB_FLIST = 'https://hub.gig.tech/gig-autobuilder/zero-os-0-db-master.flist'


class Zerodb(TemplateBase):

    version = '0.0.1'
    template_name = "zerodb"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        for param in ['node']:
            if not self.data.get(param):
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))
        if bool(self.data.get('nodeMountPoint')) != bool(self.data['containerMountPoint']):
            raise ValueError('nodeMountPoint and containerMountPoint must either both be defined or both be none.')

    @property
    def node_sal(self):
        return j.clients.zero_os.sal.node_get(self.data['node'])

    @property
    def container_sal(self):
        return self.node_sal.containers.get(self.data['container'])

    @property
    def zerodb_sal(self):
        kwargs = {
            'name': self.name,
            'container': self.container_sal,
            'addr': self.data['listenAddr'],
            'port': self.data['listenPort'],
            'data_dir': self.data['dataDir'],
            'index_dir': self.data['indexDir'],
            'mode': self.data['mode'],
            'sync': self.data['sync'],
            'admin': self.data['admin'],
        }
        return j.clients.zero_os.sal.get_zerodb(**kwargs)

    def get_data(self):
        return self.data

    def install(self):
        mounts = {}
        if self.data['nodeMountPoint'] and self.data['containerMountPoint']:
            mounts = {'source': self.data['nodeMountPoint'], 'target': self.data['containerMountPoint']}

        container_data = {
            'flist': ZERODB_FLIST,
            'mounts': [mounts],
            'node': self.data['node'],
            'hostNetworking': True,
            'storage': 'ardb://hub.gig.tech:16379',
        }
        self.data['container'] = 'container_%s' % self.name
        container = self.api.services.create(CONTAINER_TEMPLATE_UID, self.data['container'], data=container_data)
        container.schedule_action('install').wait()
        self.state.set('actions', 'install', 'ok')

    def start(self):
        """
        start zerodb server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Starting zerodb {}'.format(self.name))
        container = self.api.services.get(template_uid=CONTAINER_TEMPLATE_UID, name=self.data['container'])
        container.schedule_action('start').wait()
        self.zerodb_sal.start()
        self.state.set('actions', 'start', 'ok')

    def stop(self):
        """
        stop zerodb server
        """
        self.state.check('actions', 'start', 'ok')
        self.logger.info('Stopping zerodb {}'.format(self.name))
        self.zerodb_sal.stop()
        self.state.delete('actions', 'start')

    def namespace_list(self):
        self.state.check('actions', 'start', 'ok')
        return self.zerodb_sal.list_namespaces()

    def namespace_info(self, name):
        self.state.check('actions', 'start', 'ok')
        return self.zerodb_sal.get_namespace_info(name)

    def namespace_create(self, name, size=None, secret=None):
        self.state.check('actions', 'start', 'ok')
        self.zerodb_sal.create_namespace(name)
        if size:
            self.zerodb_sal.set_namespace_property(name, 'maxsize', size)
        if secret:
            self.zerodb_sal.set_namespace_property(name, 'password', secret)

    def namespace_set(self, name, prop, value):
        self.state.check('actions', 'start', 'ok')
        self.zerodb_sal.set_namespace_property(name, prop, value)
