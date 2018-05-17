import unittest
from framework.zos_utils.utils import ZOS_BaseTest
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
        """ ZRT-ZOS-001
        *Test case for creating a vm on a zero-os node*

        **Test Scenario:**

        #. Create vm[vm1], should succeed.
        #. Check that the vm have been created.
        #. Destroy [vm1], should succeed.
        #. Check that [vm1] has been destroyed successfully.
        """
        self.log('%s STARTED' % self._testID)

        self.log('Create vm[vm1], should succeed.')
        vm1_name = self.random_string()
        self.vms = {vm1_name: {'flist': self.vm_flist,            
                               'nics': {"name": self.random_string(), "type": "default"}
                               }}

        res = self.create_vm(vms=self.vms, temp_actions=self.temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(vm1_name, res[vm1_name]['install'])

        self.log('Check that the vm have been created.')
        vms = self.zos_client.kvm.list()
        vm = [vm for vm in vms if vm['name'] == vm1_name]
        self.assertTrue(vm)
        self.assertEqual(vm[0]['state'], "running")
        self.log('%s ENDED' % self._testID)

        self.log('Destroy [vm1], should succeed.')
        temp_actions = {'vm': {'actions': ['uninstall']}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(vm1_name, res[vm1_name]['uninstall'])        
        
        self.log("Check that [vm1] has been destroyed successfully.")
        vms = self.zos_client.kvm.list()
        self.assertNotIn(vm1_name, vms)
        self.log('%s ENDED' % self._testID)

    def test002_create_vm_with_non_valid_params(self):
        """ ZRT-ZOS-002
        *Test case for creating vm with non-valid parameters*
        **Test Scenario:**
        #. Create a vm without providing flist parameter, should fail.
        """
        self.log('Create a vm without providing flist parameter, should fail.')
        vm1_name = self.random_string()
        self.vms = {vm1_name: {     
                               'nics': {"name": self.random_string(), "type": "default"}}}
                                                              
        res = self.create_vm(vms=self.vms, temp_actions=self.temp_actions)
        self.assertEqual(res, "invalid input. Vm requires flist or ipxeUrl to be specifed.")

        self.log('%s ENDED' % self._testID)

    @unittest.skip("not-tested")
    def test003_pause_and_resume_vm(self):
        """ ZRT-ZOS-003
        *Test case for testing pause and resume vm*

        **Test Scenario:**

        #. Create a vm[vm1]  on node, should succeed.
        #. Pause [vm1], should succeed.
        #. Check that [vm1] has been paused successfully.
        #. Resume [vm1], should succeed.
        #. Check that [vm1] is runninng .
        """
        self.log('%s STARTED' % self._testID)

        self.log('Create a vm[vm1]  on node, should succeed.')
        vm1_name = self.random_string()
        self.vms = {vm1_name: {'flist': self.vm_flist,            
                               'nics': {"type": "default"}}}

        res = self.create_vm(vms=self.vms, temp_actions=self.temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.cont1_name, res[vm1_name]['install'])

        self.log('Pause [vm1], should succeed.')
        temp_actions = {'vm': {'actions': ['pause'], 'service': vm1_name}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.cont1_name, res[vm1_name]['pause'])        
        
        self.log("Check that [vm1] has been paused successfully..")
        vms = self.zos_client.kvm.list()
        vm1 = [vm for vm in vms if vm['name'] == vm1_name]
        self.assertEqual(vm1['state'], "paused")

        temp_actions = {'vm': {'actions': ['resume'], 'service': vm1_name}}
        res = self.create_vm(vms=self.vms, temp_actions=temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.cont1_name, res[vm1_name]['resume'])        
         
        self.log('Check that [vm1] is runninng ')
        vms = self.zos_client.kvm.list()
        vm1 = [vm for vm in vms if vm['name'] == vm1_name]
        self.assertEqual(vm1['state'], "running")

        self.log('%s ENDED' % self._testID)