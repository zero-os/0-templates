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
        for param in ['node', 'zerodbs', 'namespace', 'login', 'password']:
            if not self.data.get(param):
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))

        self.recurring_action('_backup_minio', 30)

    @property
    def node_sal(self):
        return j.clients.zero_os.sal.node_get(self.data['node'])

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
            'zdbs': self._get_zdbs(),
            'port': self.data['listenPort'],
            'private_key': self.data['privateKey']
        }
        return j.clients.zero_os.sal.get_minio(**kwargs)

    @property
    def restic_sal(self):
        bucket = '{repo}{bucket}'.format(repo=self.data['resticRepo'], bucket=self.guid)
        return j.clients.zero_os.sal.get_restic(self.container_sal, bucket)

    def _backup_minio(self):
        self.state.check('actions', 'start', 'ok')
        self.logger.info('Backing up minio %s' % self.name)
        print(self.restic_sal.backup(META_DIR))

    def _get_zdbs(self):
        zdbs_hosts = []
        for zdb_name in self.data['zerodbs']:
            zdb = self.api.services.get(template_uid=ZDB_TEMPLATE_UID, name=zdb_name)
            task = zdb.schedule_action('get_bind_address')
            task.wait()
            zdbs_hosts.append(task.result)

        return zdbs_hosts

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
            },{
                'name': 'AWS_ACCESS_KEY_ID',
                'value': self.data['resticUsername'],
            },
            {
                'name': 'AWS_SECRET_ACCESS_KEY',
                'value': self.data['resticPassword'],
            },
        ]
        container_data = {
            'flist': MINIO_FLIST,
            'node': self.data['node'],
            'env': env,
            'ports': ['%s:%s' % (self.data['listenPort'], self.data['listenPort'])],
            'nics': [{'type': 'default'}],
        }
        self.data['container'] = 'container_%s' % self.name
        container = self.api.services.create(CONTAINER_TEMPLATE_UID, self.data['container'], data=container_data)
        container.schedule_action('install').wait()
        self.minio_sal.create_config()
        self.restic_sal.init_repo()
        self.state.set('actions', 'install', 'ok')

    def start(self):
        """
        start minio server
        """
        self.state.check('actions', 'install', 'ok')
        self.logger.info('Starting minio %s' % self.name)
        container = self.api.services.get(template_uid=CONTAINER_TEMPLATE_UID, name=self.data['container'])
        container.schedule_action('start').wait()
        self.minio_sal.start()
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
        container.schedule_action('uninstall').wait()
        self.state.delete('actions', 'install')
