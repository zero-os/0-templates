
from js9 import j
from zerorobot.template.base import TemplateBase
from zerorobot.template.decorator import retry, timeout
from zerorobot.template.state import StateCheckError

CONTAINER_TEMPLATE_UID = 'github.com/zero-os/0-templates/container/0.0.1'
VM_TEMPLATE_UID = 'github.com/zero-os/0-templates/vm/0.0.1'
BOOTSTRAP_TEMPLATE_UID = 'github.com/zero-os/0-templates/zeroos_bootstrap/0.0.1'
ZDB_TEMPLATE_UID = 'github.com/zero-os/0-templates/zerodb/0.0.1'


class Node(TemplateBase):

    version = '0.0.1'
    template_name = 'node'

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self.validate()

        self._ensure_client_config()
        self.recurring_action('_monitor', 30)  # every 30 seconds

    def validate(self):
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
        return j.clients.zero_os.sal.get_node(self.name)

    def _monitor(self):
        self.logger.info('Monitoring node %s' % self.name)
        self.state.check('actions', 'install', 'ok')

        # if node was previously running set timeout to 300 else 30
        try:
            self.state.check('status', 'running', 'ok')
            timeout = 300
        except StateCheckError:
            timeout = 30

        if not self.node_sal.is_running(timeout):
            self.state.delete('status', 'running')
            return

        self.state.set('status', 'running', 'ok')
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

        self._healthcheck()

    @retry(Exception, tries=2, delay=2)
    def install(self):
        self.logger.info('Installing node %s' % self.name)
        self.data['version'] = '{branch}:{revision}'.format(**self.node_sal.client.info.version())

        # Set host name
        self.node_sal.client.system('hostname %s' % self.data['hostname']).get()
        self.node_sal.client.bash('echo %s > /etc/hostname' % self.data['hostname']).get()

        self.state.set('status', 'running', 'ok')

        # configure networks
        tasks = []
        for nw in self.data.get('networks', []):
            network = self.api.services.get(name=nw)
            self.logger.info("configure network %s", nw)
            tasks.append(network.schedule_action('configure', args={'node_name': self.name}))
        self._wait_all(tasks, timeout=120, die=True)

        mounts = self.node_sal.partition_and_mount_disks()
        port = 9900
        tasks = []
        for mount in mounts:
            zdb_name = 'zdb_%s_%s' % (self.name, mount['disk'])
            zdb_data = {
                'node': self.name,
                'nodeMountPoint': mount['mountpoint'],
                'containerMountPoint': '/zerodb',
                'listenPort': port,
                'admin': j.data.idgenerator.generateXCharID(10),
                'mode': 'direct',
            }

            zdb = self.api.services.find_or_create(ZDB_TEMPLATE_UID, zdb_name, zdb_data)
            tasks.append(zdb.schedule_action('install'))
            tasks.append(zdb.schedule_action('start'))
            port += 1

        self._wait_all(tasks, timeout=120, die=True)
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

    def uninstall(self):
        self.logger.info('Uninstalling node %s' % self.name)

        self._stop_all_containers()
        self._stop_all_vms()

        # allow to search per template

        for bootstrap in self.api.services.find(template_uid=BOOTSTRAP_TEMPLATE_UID):
            # FIXME: not ideal cause we're leaking data info to other service
            bootstrap.schedule_action('delete_node', args={'redis_addr': self.data['redisAddr']}).wait(die=True)

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

    def _healthcheck(self):
        node_sal = self.node_sal
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

    def _wait_all(self, tasks, timeout=60, die=False):
        for t in tasks:
            t.wait(timeout=timeout, die=die)


def _update(service, healcheck_result):
    for rprtr in service.data.get('alerta', []):
        reporter = service.api.services.get(name=rprtr)
        reporter.schedule_action('process_healthcheck', args={'name': service.name, 'healcheck_result': healcheck_result})

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


def _update_healthcheck_state(service, healthcheck):
    if isinstance(healthcheck, list):
        for hc in healthcheck:
            _update(service, hc)
    else:
        _update(service, healthcheck)
