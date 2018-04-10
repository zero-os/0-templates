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
        self.containers.update({self.cont2_name: {'node': self.zos_node_name,
                                                  'hostname': self.cont2_name,
                                                  'flist': self.cont_flist,
                                                  'storage': self.cont_storage}})

        res = self.create_container(containers=self.containers, temp_actions=self.temp_actions)
        self.assertEqual(type(res), type(dict()))
        self.wait_for_service_action_status(self.cont1_name, res[self.cont1_name]['install'])
        self.wait_for_service_action_status(self.cont2_name, res[self.cont2_name]['install'])

        self.log('Check that the container have been created.')
        conts = self.zos_client.container.list()
        self.assertTrue([c for c in conts.values() if c['container']['arguments']['name'] == self.cont1_name])
        self.assertTrue([c for c in conts.values() if c['container']['arguments']['name'] == self.cont2_name])
        cont1 = [c for c in conts.values() if c['container']['arguments']['name'] == self.cont1_name][0]
        self.assertTrue(cont1['container']['arguments']['storage'], self.cont_storage)
        self.assertTrue(cont1['container']['arguments']['root'], self.cont_flist)
        self.assertTrue(cont1['container']['arguments']['hostname'], self.cont_flist)

        self.log('%s ENDED' % self._testID)
