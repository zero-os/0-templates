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
        self.temp_actions = {'node': {'actions': ['install']},
                             'container': {'actions': ['install']}
                             }

    def test001_create_container(self):
        """ ZRT-ZOS-001
        *Test case for creatings container on a zero-os node*

        **Test Scenario:**

        #. Create a node service, should succeed.
        #. Create a two container on that node, should succeed.
        #. Check that the container have been created.
        """
        self.log('%s STARTED' % self._testID)

        self.log('Create a two container on that node, should succeed.')
        self.cont1_name = self.random_string()
        self.containers = {self.cont1_name: {'node': self.zos_node_name,
                                             'hostname': self.cont1_name,
                                             'flist': self.cont_flist,
                                             'storage': self.cont_storage}}

        self.cont2_name = self.random_string()
        self.containers = {self.cont2_name: {'node': self.zos_node_name,
                                             'hostname': self.cont2_name,
                                             'flist': self.cont_flist,
                                             'storage': self.cont_storage}}

        res = self.create_container(containers=self.containers, temp_actions=self.temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.cont1_name, res[self.cont1_name]['install'])
        self.wait_for_service_action_status(self.cont2_name, res[self.cont2_name]['install'])

        self.log('Check that the container have been created.')
        self.assertEqual(self.zos_client.containers.list(), 3)
        ## make sure they exist by name and the params are reflected correctly

        self.log('%s ENDED' % self._testID)
