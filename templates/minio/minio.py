from js9 import j

from zerorobot.template.base import TemplateBase

ZDB_TEMPLATE_UID = 'github.com/zero-os/0-templates/zerodb/0.0.1'
CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'

MINIO_FLIST = 'https://hub.gig.tech/gig-official-apps/minio.flist'
META_DIR = '/bin/zerostor_meta'


class Minio(TemplateBase):

    version = '0.0.1'
    template_name = "minio"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

        self.recurring_action('_backup_minio', 30)

    def validate(self):
        for param in ['node', 'zerodbs', 'namespace', 'login', 'password']:
            if not self.data.get(param):
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))

        if not self.data['resticRepo'].endswith('/'):
            self.data['resticRepo'] += '/'

    @property
    def node_sal(self):
        return j.clients.zos.sal.get_node(self.data['node'])

    @property
    def container_sal(self):
        return self.node_sal.containers.get(self.data['container'])

    @property
    def minio_sal(self):
        kwargs = {
            'name': self.name,
            'container': self.container_sal,
            'namespace': self.data['namespace'],
            'namespace_secret': self.data['nsSecret'],
            'zdbs': self.data['zerodbs'],
            'port': self.data['listenPort'],
            'private_key': self.data['privateKey']
        }
        return j.clients.zos.sal.get_minio(**kwargs)

    @property
    def restic_sal(self):
        bucket = '{repo}{bucket}'.format(repo=self.data['resticRepo'], bucket=self.guid)
        return j.clients.zos.sal.get_restic(self.container_sal, bucket)

    def _backup_minio(self):
        self.state.check('actions', 'start', 'ok')
        self.logger.info('Backing up minio %s' % self.name)
        print(self.restic_sal.backup(META_DIR))

    def install(self):
        self.logger.info('Installing minio %s' % self.name)
        env = [
            {
                'name': 'MINIO_ACCESS_KEY',
                'value': self.data['login'],
            },
            {
                'name': 'MINIO_SECRET_KEY',
                'value': self.data['password'],
            }, {
                'name': 'AWS_ACCESS_KEY_ID',
                'value': self.data['resticUsername'],
            },
            {
                'name': 'AWS_SECRET_ACCESS_KEY',
                'value': self.data['resticPassword'],
            },
            {
                'name': 'MINIO_ZEROSTOR_META_PRIVKEY',
                'value': self.data['metaPrivateKey'],
            }
        ]
        container_data = {
            'flist': MINIO_FLIST,
            'node': self.data['node'],
            'env': env,
            'ports': ['%s:%s' % (self.data['listenPort'], self.data['listenPort'])],
            'nics': [{'type': 'default'}],
        }
        self.data['container'] = 'container_%s' % self.name
        container = self.api.services.find_or_create(
            CONTAINER_TEMPLATE_UID, self.data['container'], data=container_data)
        container.schedule_action('install').wait(die=True)

        self.minio_sal.create_config()
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
        container = self.api.services.get(template_uid=CONTAINER_TEMPLATE_UID, name=self.data['container'])
        container.schedule_action('start').wait(die=True)
        self.minio_sal.start()
        self.restic_sal.restore(META_DIR)
        self.state.set('actions', 'start', 'ok')

    def stop(self):
        """
        stop minio server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Stopping minio %s' % self.name)
        self.minio_sal.stop()
        self.state.delete('actions', 'start')

    def uninstall(self):
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Uninstalling minio %s' % self.name)
        self.stop()
        container = self.api.services.get(template_uid=CONTAINER_TEMPLATE_UID, name=self.data['container'])
        container.schedule_action('uninstall').wait(die=True)
        self.state.delete('actions', 'install')
