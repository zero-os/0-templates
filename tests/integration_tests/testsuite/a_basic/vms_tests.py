import unittest
from framework.zos_utils.utils import ZOS_BaseTest
from random import randint
import time
from nose_parameterized import parameterized
from random import randint
from testconfig import config
from zerorobot.cli import utils
from js9 import j
from termcolor import colored

class BasicTests(ZOS_BaseTest):
    def __init__(self, *args, **kwargs):
        super(BasicTests, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        super(BasicTests, cls).setUpClass()

    def setUp(self):
        super(BasicTests, self).setUp()
        self.temp_actions = {
                             'vm': {'actions': ['install']}
                            }

    def test001_create_vm(self):
        """ ZRT-ZOS-003
        *Test case for creating a vm.*

        **Test Scenario:**

        #. Create vm[vm1], should succeed.
        #. Check that the vm have been created.
        #. Destroy [vm1], should succeed.
        #. Check that [vm1] has been destroyed successfully.
        """
        self.log('%s STARTED' % self._testID)

        self.log('Create vm[vm1], should succeed.')
        vm1_name = self.random_string()
        self.vms = {vm1_name: {'flist': self.vm_flist, 'memory': 2048}}
        res = self.create_vm(vms=self.vms, temp_actions=self.temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(vm1_name, res[vm1_name]['install'])
        self.log('Check that the vm have been created.')
        time.sleep(3)
        vms = self.zos_client.kvm.list()
        vm = [vm for vm in vms if vm['name'] == vm1_name]
        self.assertTrue(vm)
        self.assertEqual(vm[0]['state'], "running")

        self.log('Destroy [vm1], should succeed.')
        temp_actions = {'vm': {'actions': ['uninstall']}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(vm1_name, res[vm1_name]['uninstall'])        
        
        self.log("Check that [vm1] has been destroyed successfully.")
        vms = self.zos_client.kvm.list()
        vm = [vm for vm in vms if vm['name'] == vm1_name]
        self.assertFalse(vm)        
        self.log('%s ENDED' % self._testID)

    @unittest.skip('https://github.com/zero-os/0-templates/issues/140')
    def test002_create_vm_with_non_valid_params(self):
        """ ZRT-ZOS-004
        *Test case for creating vm with non-valid parameters*

        **Test Scenario:**
        #. Create a vm without providing flist parameter, should fail.

        """
        self.log('Create a vm without providing flist parameter, should fail.')
        vm1_name = self.random_string()
        self.vms = {vm1_name: {}}
                                                              
        res = self.create_vm(vms=self.vms, temp_actions=self.temp_actions)
        self.assertEqual(res, "invalid input. Vm requires flist or ipxeUrl to be specifed.")
        self.log('%s ENDED' % self._testID)

class VM_actions(ZOS_BaseTest):
    def __init__(self, *args, **kwargs):
        super(VM_actions, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        self = cls()
        super(VM_actions, cls).setUpClass()
        cls.zt_service = self.random_string()
        zt = self.robot.services.create('github.com/zero-os/0-templates/zerotier_client/0.0.1', cls.zt_service , {'token': self.zt_token})

        cls.temp_actions = {
                             'vm': {'actions': ['install']}
                            }
        cls.vm1_name = cls.random_string()
        cls.vms = {cls.vm1_name: {'flist': self.vm_flist,
                                  'memory': 2048,
                                  'nics': [{'type': 'default', 'name': cls.random_string()}]}}

        res = self.create_vm(vms=cls.vms, temp_actions=cls.temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(cls.vm1_name, res[cls.vm1_name]['install'])
        cls.vm1_info = self.get_vm(cls.vm1_name)[0]
        vm_vnc_port = cls.vm1_info['vnc'] - 5900
        cls.vm_ip_vncport = '{}:{}'.format(self.zos_redisaddr, vm_vnc_port)

    @classmethod
    def tearDownClass(cls):
        self = cls()
        instance, _ = utils.get_instance()
        self.zrobot_client = j.clients.zrobot.get(instance)
        temp_actions = {'vm': {'actions': ['uninstall']}}
        if self.check_if_service_exist(self.vm1_name):
            res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
            self.wait_for_service_action_status(self.vm1_name, res[self.vm1_name]['uninstall'])
        self.delete_services()

    def test001_pause_and_resume_vm(self):
        """ ZRT-ZOS-005
        *Test case for testing pause and resume vm*

        **Test Scenario:**

        #. Create a vm[vm1]  on node, should succeed.
        #. Pause [vm1], should succeed.
        #. Check that [vm1] has been paused successfully.
        #. Resume [vm1], should succeed.
        #. Check that [vm1] is runninng .
        """
        self.log('%s STARTED' % self._testID)

        self.log('Pause [vm1], should succeed.')
        temp_actions = {'vm': {'actions': ['pause'], 'service': self.vm1_name}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.vm1_name, res[self.vm1_name]['pause'])        
        
        self.log("Check that [vm1] has been paused successfully..")
        vms = self.zos_client.kvm.list()
        vm1 = [vm for vm in vms if vm['name'] == self.vm1_name]
        self.assertEqual(vm1[0]['state'], "paused")

        self.log("Resume [vm1], should succeed.")
        temp_actions = {'vm': {'actions': ['resume'], 'service': self.vm1_name}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.vm1_name, res[self.vm1_name]['resume'])        
         
        self.log('Check that [vm1] is runninng ')
        vms = self.zos_client.kvm.list()
        vm1 = [vm for vm in vms if vm['name'] == self.vm1_name]
        self.assertEqual(vm1[0]['state'], "running")

        self.log('%s ENDED' % self._testID)

    def test002_shutdown_and_start_vm(self):
        """ ZRT-ZOS-006
        *Test case for testing shutdown and reset vm*

        **Test Scenario:**

        #. Create a vm[vm1]  on node, should succeed.
        #. Shutdown [vm1], should succeed.
        #. Check that [vm1] has been forced shutdown successfully.
        #. Start [vm1], should succeed.
        #. Check that [vm1] is running again.
        """
        self.log('%s STARTED' % self._testID)
        
        self.log('Shutdown [vm1], should succeed.')
        temp_actions = {'vm': {'actions': ['shutdown'], 'service': self.vm1_name, 'args': {'force':True}}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.vm1_name, res[self.vm1_name]['shutdown'])        
        
        self.log("Check that [vm1] has been forced shutdown successfully..")
        time.sleep(10)
        vms = self.zos_client.kvm.list()
        vm1 = [vm for vm in vms if vm['name'] == self.vm1_name]
        self.assertFalse(vm1)

        self.log("Start [vm1], should succeed.")
        temp_actions = {'vm': {'actions': ['start'], 'service': self.vm1_name}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.vm1_name, res[self.vm1_name]['start'])        

        self.log("Check that [vm1] is running again.")
        vms = self.zos_client.kvm.list()
        vm1 = [vm for vm in vms if vm['name'] == self.vm1_name]
        self.assertEqual(vm1[0]['state'], "running")

        self.log('%s ENDED' % self._testID)

    @unittest.skip('https://github.com/zero-os/0-templates/issues/141')
    def test003_enable_and_disable_vm_vnc(self):
        """ ZRT-ZOS-007
        *Test case for testing reset vm*

        **Test Scenario:**

        #. Create a vm[vm1]  on node, should succeed.
        #. Enable vnc_port for [vm1], should succeed.
        #. Check that vnc_port has been enabled successfully.
        #. Disable vnc_port for [vm1], should succeed.
        #. Check that vnc_port has been disabled successfully.
        """
        self.log('%s STARTED' % self._testID)
        
        self.log('Enable vnc_port for [vm1], should succeed.')
        temp_actions = {'vm': {'actions': ['enable_vnc'], 'service': self.vm1_name}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.vm1_name, res[self.vm1_name]['enable_vnc'])        

        self.log("Check that vnc_port has been enabled successfully.")
        self.assertTrue(self.check_vnc_connection(self.vm_ip_vncport))

        self.log("Disable vnc_port for [vm1], should succeed.")
        temp_actions = {'vm': {'actions': ['disable_vnc'], 'service': self.vm1_name}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.vm1_name, res[self.vm1_name]['disable_vnc'])        

        self.log("Check that vnc_port has been disabled successfully.")
        self.assertFalse(self.check_vnc_connection(self.vm_ip_vncport))

    @parameterized.expand(["reset", "reboot"])
    def test004_reset_and_reboot_vm(self, action_type):
        """ ZRT-ZOS-008
        *Test case for testing reset vm*

        **Test Scenario:**

        #. Create a vm[vm1]  on node, should succeed.
        #. Enable vnc_port for [vm1], should succeed.
        #. Reset or reboot the vm, should suceeed.
        #. Check that [vm] has been rebooted/reset successfully.
        """
        self.log('%s STARTED' % self._testID)
        vm_name = self.random_string()
        data = {'flist': self.vm_flist,
                'memory': 2048,
                'nics': [{'type': 'zerotier', 'id': self.zt_id, 'name': self.random_string(), 'ztClient': self.zt_service}],
                'configs': [{'path': '/root/.ssh/authorized_keys',
                             'content': self.ssh_key,
                             'name': 'sshkey'}]}
                             
        vm = self.robot.services.find_or_create('github.com/zero-os/0-templates/vm/0.0.1', service_name=vm_name,data=data)
        install_result = vm.schedule_action("install").wait(die=True)
        self.assertEqual(install_result.state, 'ok')
        for _ in range(10):
            vm_info = vm.schedule_action("info").wait(die=True).result
            vm_nics = vm_info['nics']
            if 'ip' not in vm_nics[0].keys():
                time.sleep(25)
            else:
                vm_ip = vm_nics[0]['ip']
                break
        else:
            RuntimeError(colored("vm didn't join the zerotier network", 'red'))

        self.log("%s the vm , should succeed"%action_type)
        vm.schedule_action(action_type).wait(die=True).result
        self.log("Check that [vm] has been %s successfully."%action_type)

        result = self.execute_command(vm_ip, 'uptime') 
        uptime = int(result[result.find('up')+2:result.find('min')])
        self.assertAlmostEqual(uptime, 0, delta=3)
        vm_info = vm.schedule_action("uninstall").wait(die=True).result
