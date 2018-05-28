import unittest
from framework.zos_utils.utils import ZOS_BaseTest
from random import randint
import time
from nose_parameterized import parameterized
from random import randint


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
        self.vms = {vm1_name: {'flist': self.vm_flist, 'memory': 512}}
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

        cls.temp_actions = {
                             'vm': {'actions': ['install']}
                            }
        cls.vm1_name = cls.random_string()
        cls.vms = {cls.vm1_name: {'flist': self.vm_flist,
                                  'memory': 2048}}

        res = self.create_vm(vms=cls.vms, temp_actions=cls.temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.vm1_name, res[self.vm1_name]['install'])

    @classmethod
    def tearDownClass(cls):
        self = cls()
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
        temp_actions = {'vm': {'actions': ['shutdown'], 'service': self.vm1_name, 'args':{'force':True}}}
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
