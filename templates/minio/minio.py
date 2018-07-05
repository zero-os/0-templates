from js9 import j

from zerorobot.template.base import TemplateBase


MINIO_FLIST = 'https://hub.gig.tech/gig-official-apps/minio.flist'
META_DIR = '/bin/zerostor_meta'
NODE_CLIENT = 'local'
NS_TEMPLATE_UID = 'github.com/zero-os/0-templates/namespace/0.0.1'


class Minio(TemplateBase):

    version = '0.0.1'
    template_name = "minio"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

        self.recurring_action('_backup_minio', 30)
        self.recurring_action('_monitor', 30)  # every 30 seconds

    def validate(self):
        self.state.delete('status', 'running')
        for param in ['namespaces', 'namespace', 'login', 'password']:
            if not self.data.get(param):
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))

        if not self.data['resticRepo'].endswith('/'):
            self.data['resticRepo'] += '/'

    def _monitor(self):
        self.logger.info('Monitor minio %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.state.check('actions', 'start', 'ok')

        if not self._minio_sal.is_running():
            self.state.delete('status', 'running')

            for name in self.data['namespaces']:
                namespace = self.api.services.get(template_uid=NS_TEMPLATE_UID, name=name)
                namespace.state.check('status', 'running', 'ok')

            self._update_config()
            self._minio_sal.start()
            self.restic_sal.restore(META_DIR)
            if self._minio_sal.is_running():
                self.state.set('status', 'running', 'ok')
        else:
            self.state.set('status', 'running', 'ok')

    @property
    def node_sal(self):
        return j.clients.zos.sal.get_node(NODE_CLIENT)

    @property
    def _minio_sal(self):

        kwargs = {
            'name': self.name,
            'node': self.node_sal,
            'namespace': self.data['namespace'],
            'namespace_secret': self.data['nsSecret'],
            'zdbs': self.data['zerodbs'],
            'node_port': self.data['listenPort'],
            'private_key': self.data['privateKey'],
            'login': self.data['login'],
            'password': self.data['password'],
            'restic_username': self.data['resticUsername'],
            'restic_password': self.data['resticPassword'],
            'meta_private_key': self.data['metaPrivateKey'],
        }
        return j.clients.zos.sal.get_minio(**kwargs)

    @property
    def restic_sal(self):
        bucket = '{repo}{bucket}'.format(repo=self.data['resticRepo'], bucket=self.guid)
        return j.clients.zos.sal.get_restic(self._minio_sal.container, bucket)

    def _backup_minio(self):
        self.state.check('actions', 'start', 'ok')
        self.logger.info('Backing up minio %s' % self.name)
        print(self.restic_sal.backup(META_DIR))

    def node_port(self):
        return self.data['node_port']

    def _update_zerodbs(self):
        for name in self.data['namespaces']:
            namespace = self.api.services.get(template_uid=NS_TEMPLATE_UID, name=name)
            result = namespace.schedule_action('connection_info').wait(die=True).result
            self.data['zerodbs'].append('{}:{}'.format(result['ip'], result['port']))

    def _update_config(self):
        self._update_zerodbs()
        minio_sal = self._minio_sal
        minio_sal.create_config()
        self.data['node_port'] = minio_sal.node_port

    def install(self):
        self.logger.info('Installing minio %s' % self.name)
        self._update_config()
        if not self.data['resticRepoPassword']:
            self.data['resticRepoPassword'] = j.data.idgenerator.generateXCharID(10)
        self.restic_sal.init_repo(password=self.data['resticRepoPassword'])

        self.state.set('actions', 'install', 'ok')

    def start(self):
        """
        start minio server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Starting minio %s' % self.name)
        self._update_zerodbs()
        self._minio_sal.start()
        self.restic_sal.restore(META_DIR)
        self.state.set('actions', 'start', 'ok')

    def stop(self):
        """
        stop minio server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Stopping minio %s' % self.name)
        self._minio_sal.stop()
        self.state.delete('actions', 'start')

    def uninstall(self):
        self.logger.info('Uninstalling minio %s' % self.name)
        self._minio_sal.destroy()
        self.state.delete('actions', 'install')
