import time

from gevent import sleep

import redis
from js9 import j
from zerorobot.service_collection import ServiceConflictError
from zerorobot.template.base import TemplateBase
from zerorobot.template.decorator import retry

CONTAINER_TEMPLATE_UID = "github.com/jumpscale/0-robot/container/0.0.1"
VM_TEMPLATE_UID = "github.com/jumpscale/0-robot/vm/0.0.1"


class Node(TemplateBase):

    version = '0.0.1'
    template_name = "node"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._node = None
        self._validate_input()
        self._ensure_client_config()
        # self.recurring_action('monitor', 10)
        self.recurring_action('_healthcheck', 30)

    def _validate_input(self):
        for param in ['redisAddr', 'redisPort']:
            if not self.data[param]:
                raise ValueError("parameter '%s' not valid: %s", str(self.data[param]))

    def _ensure_client_config(self):
        data = {
            'host': self.data['redisAddr'],
            'port': self.data['redisPort'],
            'password_': self.data['redisPassword'],
            'ssl': True,
            'db': 0,
            'timeout': 120,
        }
        # make sure the config exists
        cl = j.clients.zero_os.get(
            instance=self.name,
            data=data,
            create=True,
            die=True)

        # update the config with correct value
        cl.config.data.update(data)
        cl.config.save()

    def update_data(self, d):
        self.data.update(d)
        # force recreation of the connection to the node
        for key in ['redisAddr', 'redisPort', 'redisPassword']:
            if d.get(key) != self.data[key]:
                self._node = None
                break

    @property
    def node(self):
        """
        connection to the node
        """
        if self._node is None:
            self._ensure_client_config()
            self._node = j.clients.zero_os.sal.node_get(self.name)
            self.data['version'] = "{branch}:{revision}".format(**self._node.client.info.version())
        return self._node

    @retry(Exception, tries=2, delay=2)
    def install(self):
        poolname = '{}_fscache'.format(self.name)

        self.logger.debug('create storage pool for fuse cache')
        self.node.ensure_persistance(poolname)

        # Set host name
        self.node.client.system('hostname %s' % self.data['hostname']).get()
        self.node.client.bash('echo %s > /etc/hostname' % self.data['hostname']).get()

        self.state.set('actions', 'install', 'ok')

    def create_container(self, name, flist, mounts=None, nics=None):
        self.state.check('actions', 'install', 'ok')

        args = {
            'flist': flist,
            'mounts': mounts,
            'nics': nics,
            'node': self.name,
        }

        try:
            container = self.api.services.create(CONTAINER_TEMPLATE_UID, name, args)
        except ServiceConflictError as err:
            container = self.api.services.names[name]
            container.data.update(args)

        container.parent = self
        container.schedule_action('install')
        container.schedule_action('start')
        return container

    def create_vm(self, name, flist, cpu=1, memory=128, nics=None):
        self.state.check('actions', 'install', 'ok')

        args = {
            'flist': flist,
            'cpu': cpu,
            'memory': memory,
            'nics': nics,
        }
        try:
            vm = self.api.services.create(VM_TEMPLATE_UID, name, args)
        except ServiceConflictError as err:
            vm = self.api.services.names[name]
            vm.data.update(args)

    def reboot(self):

        # TODO: review stop recurring
        self._gl_mgr.stop("recurring_monitor")

        try:
            # force_reboot = self.data['forceReboot']
            self._stop_all_container()
            self._stop_all_vm()

            self.logger.info('reboot node %s' % self.name)
            try:
                self.node.client.raw('core.reboot', {})
            except redis.exceptions.TimeoutError:
                # can happen if reboot is fast enough
                pass
        finally:
            timeout = 60
            start = time.time()
            while time.time() < start + timeout:
                try:
                    self._node = None
                    self.node.client.ping()
                    break
                except (RuntimeError, ConnectionError, redis.TimeoutError, TimeoutError):
                    sleep(1)

            else:
                self.logger.info("Could not wait within %d seconds for node to reboot" % timeout)

            self._start_all_container()
            self._start_all_vm()
            self.recurring_action('monitor', 60)

    def uninstall(self):
        # stats_collector_service = get_stats_collector(service)
        # if stats_collector_service:
        #     stats_collector_service.executeAction('uninstall', context=job.context)

        # statsdb_service = get_statsdb(service)
        # if statsdb_service and str(statsdb_service.parent) == str(service):
        #     statsdb_service.executeAction('uninstall', context=job.context)

        self._stop_all_container()
        self._stop_all_vm()

        # allow to search per template
        bootstrap = self.api.services.names['boot']
        # FIXME: not ideal cause we're leaking data info to other service
        bootstrap.schedule_action('delete_node', args={'redis_addr': self.data['redisAddr']}).wait()

        # # Remove etcd_cluster if this was the last node service
        # node_services = service.aysrepo.servicesFind(role='node')
        # if len(node_services) > 1:
        #     return

        # for etcd_cluster_service in service.aysrepo.servicesFind(role='etcd_cluster'):
        #     etcd_cluster_service.executeAction('delete', context=job.context)
        #     etcd_cluster_service.delete()

    def monitor(self):
        self.logger.info("monitor")

    def _healthcheck(self):
        if self.node.is_running():
            _update_healthcheck_state(self, self.node.healthcheck.openfiledescriptors())
            _update_healthcheck_state(self, self.node.healthcheck.cpu_mem())
            _update_healthcheck_state(self, self.node.healthcheck.rotate_logs())
            _update_healthcheck_state(self, self.node.healthcheck.network_bond())
            _update_healthcheck_state(self, self.node.healthcheck.interrupts())
            _update_healthcheck_state(self, self.node.healthcheck.context_switch())
            _update_healthcheck_state(self, self.node.healthcheck.threads())
            _update_healthcheck_state(self, self.node.healthcheck.qemu_vm_logs())
            _update_healthcheck_state(self, self.node.healthcheck.network_load())
            _update_healthcheck_state(self, self.node.healthcheck.disk_usage())

            # this is for VM. VM is not implemented yet, and we'll probably not need
            # some cleanup like this anyhow
            # self.node.healthcheck.ssh_cleanup(job=job)

            # TODO: this need to be configurable
            flist_healhcheck = 'https://hub.gig.tech/gig-official-apps/healthcheck.flist'
            with self.node.healthcheck.with_container(flist_healhcheck) as cont:
                _update_healthcheck_state(self, self.node.healthcheck.node_temperature(cont))
                _update_healthcheck_state(self, self.node.healthcheck.powersupply(cont))
                _update_healthcheck_state(self, self.node.healthcheck.fan(cont))

        # TODO: check network stability of  node with the rest of the nodes !

    def _start_all_container(self):
        for container in self.api.services.find(template_uid=CONTAINER_TEMPLATE_UID, parent=self):
            if container.name in self.api.services.names:
                self.logger.info("start container %s", container.name)
                self.api.services.names[container.name].schedule_action('start')

    def _start_all_vm(self):
        # TODO
        pass

    def _stop_all_container(self):
        tasks = []
        for container in self.api.services.find(template_uid=CONTAINER_TEMPLATE_UID, parent=self):
            if container.name in self.api.services.names:
                self.logger.info("stop container %s", container.name)
                tasks.append(self.api.services.names[container.name].schedule_action('stop'))
        self._wait_all(tasks)

    def _stop_all_vm(self):
        # TODO
        pass

    def _wait_all(self, tasks, timeout=60):
        for t in tasks:
            t.wait(timeout)


# healthchecks
def _update_healthcheck_state(service, healthcheck):
    def do(healcheck_result):
        category = healcheck_result['category'].lower()
        if len(healcheck_result['messages']) == 1:
            tag = healcheck_result['id'].lower()
            status = healcheck_result['messages'][0]['status'].lower()
        elif len(healcheck_result['messages']) > 1:
            for msg in healcheck_result['messages']:
                tag = ("%s-%s" % (healcheck_result['id'], msg['id'])).lower()
                status = msg['status'].lower()
        else:
            # probably something wrong in the format of the healthcheck
            service.logger.warning("no message in healthcheck result for %s-%s", healcheck_result['category'], healcheck_result['id'])
            return

        service.state.set(category, tag, status)

    if isinstance(healthcheck, list):
        for hc in healthcheck:
            do(hc)
    else:
        do(healthcheck)
