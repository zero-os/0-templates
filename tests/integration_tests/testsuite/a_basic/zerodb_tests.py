import time
import unittest
from random import randint
from framework.zos_utils.utils import ZOS_BaseTest


class BasicTests(ZOS_BaseTest):
    def __init__(self, *args, **kwargs):
        super(BasicTests, self).__init__(*args, **kwargs)

    def setUp(self):
        super(BasicTests, self).setUp()

    def test001_get_list_zerodb_info(self):
        """ ZRT-ZOS-009
        *Test case for listing and getting zerodb information*

        **Test Scenario:**

        #. Create zerodb (zdb) with basic params, should succeed.
        #. Check that the params has been reflected correctly.
        #. List the namespaces, should be empty.
        #. Create namespace (NS), should succeed.
        #. List namespaces, NS should be found.
        #. Set the namespace (Ns) settings.
        #. Check that NS setting has been changed.
        """
        self.log('%s STARTED' % self._testID)

        self.log('Create zerodb (zdb) with basic params, should succeed')
        adminpassword = self.random_string()
        zdb_service_name = self.random_string()
        zdb = self.robot.services.create(
            template_uid='{}/zerodb/{}'.format(self.repo, self.version),
            service_name=zdb_service_name,
            data={'sync': True,
                  'mode': 'user',
                  'admin': adminpassword,
                  'path': '/var/cache'})
        zdb.schedule_action('install').wait(die=True, timeout=30)

        self.log('Check that the params has been reflected correctly.')
        tag = 'zdb_' + zdb_service_name
        container = self.zos_client.container.find(tag)
        zdb_cl = self.zos_client.container.client(list(container.keys())[0])
        jobs = zdb_cl.job.list()
        job_id = 'zerodb.' + zdb_service_name
        job_args = [job for job in jobs if job['cmd']['id'] == job_id][0]['cmd']['arguments']['args']
        self.assertIn('user', job_args)
        self.assertIn('--sync', job_args)
        self.assertIn(adminpassword, job_args)

        self.log('list the namespaces, should be empty')
        namespaces = zdb.schedule_action('namespace_list')
        self.assertEqual(namespaces.result, [])

        self.log('Create namespace (NS), should succeed')
        ns_name = self.random_string()
        namespace = zdb.schedule_action('namespace_create', args={'name': ns_name})
        time.sleep(2)
        self.assertEqual(namespace.state, 'ok')

        self.log('List namespaces, NS should be found')
        namespaces = zdb.schedule_action('namespace_list')
        self.assertEqual(len(namespaces.result), 1)
        self.assertEqual(namespaces.result[0]['name'], ns_name)

        self.log('set the namespace (NS) settings')
        size = randint(1, 9)
        zdb.schedule_action('namespace_set', args={'name': ns_name, 'value': self.random_string(), 'prop': 'password'})
        zdb.schedule_action('namespace_set', args={'name': ns_name, 'value': False, 'prop': 'public'})
        zdb.schedule_action('namespace_set', args={'name': ns_name, 'value': size, 'prop': 'size'})

        self.log('Check that NS setting has been changed')
        ns_info = zdb.schedule_action('namespace_info', args={'name': ns_name}).wait()
        self.assertEqual(ns_info.result['public'], 'no')
        self.assertEqual(ns_info.result['password'], 'yes')
        namespaces = zdb.schedule_action('namespace_list')
        self.assertEqual(namespaces.result[0]['size'], size)
        zdb.schedule_action('stop').wait(die=True, timeout=30)

        self.log('%s ENDED' % self._testID)

    def test002_start_stop_zerodb(self):
        """ ZRT-ZOS-010
        *Test case for starting and stopping zerodb service*

        **Test Scenario:**

        #. Create zerodb (zdb).
        #. Create namespace (NS), should succeed.
        #. Stop zerodb service, should succeed.
        #. Make sure zerodb container has been removed.
        #. Start zerodb service, should succeed.
        #. Check that Namespace (NS) is still there.
        """
        self.log('%s STARTED' % self._testID)

        self.log('Create zerodb (zdb)')
        zdb_service_name = self.random_string()
        zdb = self.robot.services.create(
            template_uid='{}/zerodb/{}'.format(self.repo, self.version),
            service_name=zdb_service_name,
            data={'sync': True,
                  'mode': 'user',
                  'admin': self.random_string(),
                  'path': '/var/cache'})
        zdb.schedule_action('install').wait(die=True, timeout=30)

        self.log('Create namespace (NS), should succeed')
        ns_name = self.random_string()
        namespace = zdb.schedule_action('namespace_create', args={'name': ns_name})
        time.sleep(2)
        self.assertEqual(namespace.state, 'ok')

        self.log('Stop zerodb service, should succeed')
        zdb.schedule_action('stop').wait(die=True, timeout=30)

        self.log('Make sure zerodb container has been removed')
        conts = self.zos_client.container.list()
        self.assertFalse([c for c in conts.values() if zdb_service_name in c['container']['arguments']['name']])

        self.log('Start zerodb service, should succeed.')
        zdb.schedule_action('start').wait(die=True, timeout=30)
        conts = self.zos_client.container.list()
        self.assertTrue([c for c in conts.values() if zdb_service_name in c['container']['arguments']['name']])

        self.log('Check that Namespace (NS) is still there.')
        namespaces = zdb.schedule_action('namespace_list')
        self.assertEqual(len(namespaces.result), 1)
        self.assertEqual(namespaces.result[0]['name'], ns_name)
        zdb.schedule_action('stop')

        self.log('%s ENDED' % self._testID)


    def test003_create_get_namespace(self):
        """ ZRT-ZOS-011
        *Test case for creating and getting namespace service*

        **Test Scenario:**

        #. Create a zerodb (ZDb1).
        #. Create a namespace (NS) on ZDb1 using namespace template, should succeed.
        #. Get info for NS, should succeed.
        #. Get public url of NS, should succeed.
        #. Get private url of the NS, should succeed.
        """

        self.log('Create a namespace (NS) on ZDb1 using namespace template')
        ns_service_name = self.random_string()
        ns = self.robot.services.create(
            template_uid='{}/namespace/{}'.format(self.repo, self.version),
            service_name=ns_service_name,
            data={'size': 10,
                  'password': 'password',
                  'diskType': 'ssd'})
        ns.schedule_action('install').wait(die=True, timeout=30)

        self.log('Get info for NS')
        res_info = ns.schedule_action('info').wait(die=True, timeout=30)
        self.assertEqual(res_info.state, 'ok')

        self.log('Get public url of the namespace, should succeed')
        res_url = ns.schedule_action('url').wait(die=True, timeout=30)
        self.assertEqual(res_url.state, 'ok')
        self.assertTrue(res_url.result.startswith('zdb://'))

        self.log('private_url')
        res_pri_url = ns.schedule_action('private_url').wait(die=True, timeout=30)
        self.assertEqual(res_pri_url.state, 'ok')
        self.assertTrue(res_pri_url.result.startswith('zdb://'))
        self.assertNotEqual(res_url.result, res_pri_url.result)

        self.log('%s ENDED' % self._testID)

    def test004_create_attach_vdisk(self):
        """ ZRT-ZOS-012
        *Test case for creating and attaching vdisk*

        **Test Scenario:**

        #. Create a vdisk (VD1) and namespace (NS1).
        #. Get info for NS1, should succeed.
        #. Get public url of NS1, should succeed.
        #. Get private url of NS1, should succeed.
        #. Create a VM and attach VD1 to it, should succeed.
        #. Uninstall vdisk service, should succeed.
        """
        self.log('%s STARTED' % self._testID)

        self.log('Create a vdisk (VD1) and namespace (NS1)')
        disk_label = self.random_string()
        vdisk_service_name = self.random_string()
        vdisk = self.robot.services.create(
            template_uid='{}/vdisk/{}'.format(self.repo, self.version),
            service_name=vdisk_service_name,
            data={'size': 10,
                  'password': 'password',
                  'diskType': 'ssd',
                  'label': disk_label,
                  'nsName': 'ns_name'})
        vdisk.schedule_action('install').wait(die=True, timeout=30)

        self.log('Get info for NS')
        res_info = vdisk.schedule_action('info').wait(die=True, timeout=30)
        self.assertEqual(res_info.state, 'ok')

        self.log('Get public url of the namespace, should succeed')
        res_url = vdisk.schedule_action('url').wait(die=True, timeout=30)
        self.assertEqual(res_url.state, 'ok')
        self.assertTrue(res_url.result.startswith('zdb://'))

        self.log('private_url')
        res_pri_url = vdisk.schedule_action('private_url').wait(die=True, timeout=30)
        self.assertEqual(res_pri_url.state, 'ok')
        self.assertTrue(res_pri_url.result.startswith('zdb://'))
        self.assertNotEqual(res_url.result, res_pri_url.result)

        self.log('Create a VM and attach Attach VD1 to it, should succeed.')
        vm_service_name = self.random_string()
        vm = self.robot.services.create(
                template_uid='{}/vm/{}'.format(self.repo, self.version),
                service_name=vm_service_name,
                data={'disks':[{'name': vdisk_service_name}],
                      'flist': self.vm_flist,
                      'memory': 2048})
        vm.schedule_action('install').wait(die=True, timeout=30)
        vms = self.zos_client.kvm.list()
        disk_url = [vm['params']['media'][0]['url'] for vm in vms if vm['name']==vm_service_name][0]
        self.assertEqual(res_pri_url.result, disk_url)

        self.log('Uninstall vdisk service, should succeed')
        res = vdisk.schedule_action('uninstall').wait(die=True, timeout=30)
        self.assertEqual(res.state, 'ok')

        self.log('%s ENDED' % self._testID)
