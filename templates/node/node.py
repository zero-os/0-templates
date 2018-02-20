import time

from gevent import sleep

import redis
from js9 import j
from zerorobot.service_collection import ServiceConflictError
from zerorobot.template.base import TemplateBase
from zerorobot.template.decorator import retry

CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
VM_TEMPLATE_UID = 'github.com/zero-os/0-templates/vm/0.0.1'
BOOTSTRAP_TEMPLATE_UID = 'github.com/zero-os/0-templates/zeroos_bootstrap/0.0.1'


class Node(TemplateBase):

    version = '0.0.1'
    template_name = 'node'

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self._validate_input()

        self._refresh_password()
        self._ensure_client_config()

        self.recurring_action('_healthcheck', 30)  # every 30 secondes
        self.recurring_action('_refresh_password', 1200)  # every 20 minutes

    def _validate_input(self):
        for param in ['redisAddr', 'redisPort']:
            if not self.data[param]:
                raise ValueError("parameter '%s' not valid: %s" % (param, str(self.data[param])))

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

        cl.config.save()

    def _refresh_password(self):
        """
        this method is reponsible to automaticly refresh a jwt token used as password
        """
        if not self.data.get('redisPassword'):
            return

        # refresh jwt
        self.data['redisPassword'] = j.clients.itsyouonline.refresh_jwt_token(self.data['redisPassword'], validity=3600)
        # update the configuration of the client
        self._ensure_client_config()

    def update_data(self, data):
        self.data.update(data)
        # force recreation of the connection to the node
        for key in ['redisAddr', 'redisPort', 'redisPassword']:
            if data.get(key) != self.data[key]:
                self._ensure_client_config()
                break

    @property
    def node_sal(self):
        """
        connection to the node
        """
        return j.clients.zero_os.sal.node_get(self.name)

    @retry(Exception, tries=2, delay=2)
    def install(self):
        self.data['version'] = '{branch}:{revision}'.format(**self.node_sal.client.info.version())

        poolname = '{}_fscache'.format(self.name)

        self.logger.debug('create storage pool for fuse cache')
        self.node_sal.ensure_persistance(poolname)

        # Set host name
        self.node_sal.client.system('hostname %s' % self.data['hostname']).get()
        self.node_sal.client.bash('echo %s > /etc/hostname' % self.data['hostname']).get()

        self.state.set('actions', 'install', 'ok')

    def reboot(self):

        # TODO: review stop recurring
        self.gl_mgr.stop('recurring_monitor')

        try:
            # force_reboot = self.data['forceReboot']
            self._stop_all_containers()
            self._stop_all_vms()

            self.logger.info('reboot node %s' % self.name)
            self.node_sal.client.raw('core.reboot', {})
        finally:
            timeout = 2
            start = time.time()
            while time.time() < start + timeout:
                try:
                    self.node_sal.client.ping()
                    break
                except (RuntimeError, ConnectionError, redis.TimeoutError, TimeoutError):
                    sleep(1)

            else:
                self.logger.info('Could not wait within %d seconds for node to reboot' % timeout)
                self.recurring_action('_healthcheck', 60)
                return

            self._start_all_containers()
            self._start_all_vms()
            self.recurring_action('_healthcheck', 60)

    def uninstall(self):
        self.logger.info('uninstalling  node')
        # stats_collector_service = get_stats_collector(service)
        # if stats_collector_service:
        #     stats_collector_service.executeAction('uninstall', context=job.context)

        # statsdb_service = get_statsdb(service)
        # if statsdb_service and str(statsdb_service.parent) == str(service):
        #     statsdb_service.executeAction('uninstall', context=job.context)

        self._stop_all_containers()
        self._stop_all_vms()

        # allow to search per template

        for bootstrap in self.api.services.find(template_uid=BOOTSTRAP_TEMPLATE_UID):
            # FIXME: not ideal cause we're leaking data info to other service
            bootstrap.schedule_action('delete_node', args={'redis_addr': self.data['redisAddr']}).wait()

        # # Remove etcd_cluster if this was the last node service
        # node_services = service.aysrepo.servicesFind(role='node')
        # if len(node_services) > 1:
        #     return

        # for etcd_cluster_service in service.aysrepo.servicesFind(role='etcd_cluster'):
        #     etcd_cluster_service.executeAction('delete', context=job.context)
        #     etcd_cluster_service.delete()

    def info(self):
        return self.node_sal.client.info.os()

    def stats(self):
        return self.node_sal.client.aggregator.query()

    def _healthcheck(self):
        node_sal = self.node_sal
        if node_sal.is_running():
            _update_healthcheck_state(self, node_sal.healthcheck.openfiledescriptors())
            _update_healthcheck_state(self, node_sal.healthcheck.cpu_mem())
            _update_healthcheck_state(self, node_sal.healthcheck.rotate_logs())
            _update_healthcheck_state(self, node_sal.healthcheck.network_bond())
            _update_healthcheck_state(self, node_sal.healthcheck.interrupts())
            _update_healthcheck_state(self, node_sal.healthcheck.context_switch())
            _update_healthcheck_state(self, node_sal.healthcheck.threads())
            _update_healthcheck_state(self, node_sal.healthcheck.qemu_vm_logs())
            _update_healthcheck_state(self, node_sal.healthcheck.network_load())
            _update_healthcheck_state(self, node_sal.healthcheck.disk_usage())

            # this is for VM. VM is not implemented yet, and we'll probably not need
            # some cleanup like this anyhow
            # node_sal.healthcheck.ssh_cleanup(job=job)

            # TODO: this need to be configurable
            flist_healhcheck = 'https://hub.gig.tech/gig-official-apps/healthcheck.flist'
            with node_sal.healthcheck.with_container(flist_healhcheck) as cont:
                _update_healthcheck_state(self, node_sal.healthcheck.node_temperature(cont))
                _update_healthcheck_state(self, node_sal.healthcheck.powersupply(cont))
                _update_healthcheck_state(self, node_sal.healthcheck.fan(cont))

        # TODO: check network stability of  node with the rest of the nodes !

    def _start_all_containers(self):
        for container in self.api.services.find(template_uid=CONTAINER_TEMPLATE_UID):
            container.schedule_action('start', args={'node_name': self.name})

    def _start_all_vms(self):
        # TODO
        pass

    def _stop_all_containers(self):
        tasks = []
        for container in self.api.services.find(template_uid=CONTAINER_TEMPLATE_UID):
            tasks.append(container.schedule_action('stop', args={'node_name': self.name}))
        self._wait_all(tasks)

    def _stop_all_vms(self):
        # TODO
        pass

    def _wait_all(self, tasks, timeout=60):
        for t in tasks:
            t.wait(timeout)


def _update(service, healcheck_result):
    category = healcheck_result['category'].lower()
    if len(healcheck_result['messages']) == 1:
        tag = healcheck_result['id'].lower()
        status = healcheck_result['messages'][0]['status'].lower()
        service.state.set(category, tag, status)
    elif len(healcheck_result['messages']) > 1:
        for msg in healcheck_result['messages']:
            tag = ('%s-%s' % (healcheck_result['id'], msg['id'])).lower()
            status = msg['status'].lower()
            service.state.set(category, tag, status)
    else:
        # probably something wrong in the format of the healthcheck
        service.logger.warning('no message in healthcheck result for %s-%s',
                               healcheck_result['category'], healcheck_result['id'])
        return


def _update_healthcheck_state(service, healthcheck):
    if isinstance(healthcheck, list):
        for hc in healthcheck:
            _update(service, hc)
    else:
        _update(service, healthcheck)
