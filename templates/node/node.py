
from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.decorator import retry, timeout
from zerorobot.template.state import StateCheckError

CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
VM_TEMPLATE_UID = 'github.com/zero-os/0-templates/vm/0.0.1'
BOOTSTRAP_TEMPLATE_UID = 'github.com/zero-os/0-templates/zeroos_bootstrap/0.0.1'
ZDB_TEMPLATE_UID = 'github.com/zero-os/0-templates/zerodb/0.0.1'
NODE_CLIENT = 'local'


class Node(TemplateBase):

    version = '0.0.1'
    template_name = 'node'

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

        self.recurring_action('_monitor', 30)  # every 30 seconds

    @property
    def node_sal(self):
        """
        connection to the node
        """
        return j.clients.zero_os.sal.get_node(NODE_CLIENT)

    def _monitor(self):
        self.logger.info('Monitoring node %s' % self.name)
        self.state.check('actions', 'install', 'ok')
        self.state.set('status', 'running', 'ok')
        self._rename_cache()

        # make sure cache is always mounted
        sp = self.node_sal.storagepools.get('zos-cache')
        if not sp.mountpoint:
            self.node_sal.ensure_persistance()

        if self.node_sal.uptime() < self.data['uptime']:
            self.install()

        self.data['uptime'] = self.node_sal.uptime()

        try:
            # check if the node was rebooting and start containers and vms
            self.state.check('status', 'rebooting', 'ok')
            self._start_all_containers()
            self._start_all_vms()
            self.state.delete('status', 'rebooting')
        except StateCheckError:
            pass

    def _rename_cache(self):
        """Rename old cache storage pool to new convention if needed"""
        try:
            self.state.check("migration", "fs_cache_renamed", "ok")
            return
        except StateCheckError:
            pass

        poolname = '{}_fscache'.format(self.node_sal.name)
        try:
            sp = self.node_sal.storagepools.get(poolname)
        except ValueError:
            self.logger.info("storage pool %s doesn't exist on node %s" % (poolname, self.node_sal.name))
            return

        if sp.mountpoint:
            self.logger.info("rename mounted volume %s..." % poolname)
            cmd = 'btrfs filesystem label %s sp_zos-cache' % sp.mountpoint
        else:
            self.logger.info("rename unmounted volume %s..." % poolname)
            cmd = 'btrfs filesystem label %s sp_zos-cache' % sp.devices[0]
        result = self.node_sal.client.system(cmd).get()
        if result.state == "SUCCESS":
            self.logger.info("Rebooting %s ..." % self.node_sal.name)
            self.state.set("migration", "fs_cache_renamed", "ok")
            self.reboot()
            raise RuntimeWarning("Aborting monitor because system is rebooting for a migration.")
        self.logger.error('error: %s' % result.stderr)

    @retry(Exception, tries=2, delay=2)
    def install(self):
        self.logger.info('Installing node %s' % self.name)
        self.data['version'] = '{branch}:{revision}'.format(**self.node_sal.client.info.version())

        # Set host name
        self.node_sal.client.system('hostname %s' % self.data['hostname']).get()
        self.node_sal.client.bash('echo %s > /etc/hostname' % self.data['hostname']).get()

        self.state.set('status', 'running', 'ok')

        # @todo rethink the network cycle
        # configure networks
        # tasks = []
        # for nw in self.data.get('networks', []):
        #     network = self.api.services.get(name=nw)
        #     self.logger.info("configure network %s", nw)
        #     tasks.append(network.schedule_action('configure', args={'node_name': self.name}))
        # self._wait_all(tasks, timeout=120, die=True)

        # FIXME: need to be configurable base on the type of node
        # disabled for now
        # mounts = self.node_sal.partition_and_mount_disks()
        # port = 9900
        # tasks = []
        # for mount in mounts:
        #     zdb_name = 'zdb_%s_%s' % (self.name, mount['disk'])
        #     zdb_data = {
        #         'node': self.name,
        #         'nodeMountPoint': mount['mountpoint'],
        #         'containerMountPoint': '/zerodb',
        #         'listenPort': port,
        #         'admin': j.data.idgenerator.generateXCharID(10),
        #         'mode': 'direct',
        #     }

        #     zdb = self.api.services.find_or_create(ZDB_TEMPLATE_UID, zdb_name, zdb_data)
        #     tasks.append(zdb.schedule_action('install'))
        #     tasks.append(zdb.schedule_action('start'))
        #     port += 1

        # self._wait_all(tasks, timeout=120, die=True)
        self.data['uptime'] = self.node_sal.uptime()
        self.state.set('actions', 'install', 'ok')

    def reboot(self):
        self.state.check('status', 'running', 'ok')
        self.state.delete('status', 'running')

        self._stop_all_containers()
        self._stop_all_vms()

        self.logger.info('Rebooting node %s' % self.name)
        self.node_sal.client.raw('core.reboot', {})
        self.state.set('status', 'rebooting', 'ok')

    @timeout(30, error_message='info action timeout')
    def info(self):
        self.state.check('status', 'running', 'ok')
        return self.node_sal.client.info.os()

    @timeout(30, error_message='stats action timeout')
    def stats(self):
        self.state.check('status', 'running', 'ok')
        return self.node_sal.client.aggregator.query()

    @timeout(30, error_message='processes action timeout')
    def processes(self):
        self.state.check('status', 'running', 'ok')
        return self.node_sal.client.process.list()

    @timeout(30, error_message='processes action version')
    def os_version(self):
        self.state.check('status', 'running', 'ok')
        return self.node_sal.client.ping()[13:].strip()

    def _start_all_containers(self):
        for container in self.api.services.find(template_uid=CONTAINER_TEMPLATE_UID):
            container.schedule_action('start')

    def _start_all_vms(self):
        # TODO
        pass

    def _stop_all_containers(self):
        tasks = []
        for container in self.api.services.find(template_uid=CONTAINER_TEMPLATE_UID):
            tasks.append(container.schedule_action('stop'))
        self._wait_all(tasks)

    def _stop_all_vms(self):
        # TODO
        pass

    def _wait_all(self, tasks, timeout=60, die=False):
        for t in tasks:
            t.wait(timeout=timeout, die=die)
