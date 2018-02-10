from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest

from js9 import j
from hypervisor import Hypervisor
from zerorobot.template.state import StateCheckError


class TestHypervisorTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {'node': 'node'}

    def tearDown(self):
        patch.stopall()

    def test_invalid_data(self):
        """
        Test creating a hypervisor with invalid data
        """
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the node'):
            Hypervisor(name='hypervisor', data={})

    def test_valid_data(self):
        """
        Test creating a hypervisor service with valid data
        """
        hyperevisor = Hypervisor('hypervisor', data=self.valid_data)

    def test_node_sal_node_is_none(self):
        """
        Test the node_sal property when Hypervisor._node is None
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.node_get',  MagicMock(return_value=node_sal_return)).start()
        node_sal = hypervisor.node_sal

        assert node_sal == node_sal_return
        j.clients.zero_os.sal.node_get.assert_called_with(self.valid_data['node'])

    def test_node_sal_node_is_set(self):
        """
        Test the node_sal property when Hypervisor._node is set
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        hypervisor._node = node_sal_return
        node_sal = hypervisor.node_sal

        assert node_sal == node_sal_return
        assert j.clients.zero_os.sal.node_get.called is False

    def test_create_hypervisor(self):
        """
        Test successfully creating a hypervisor
        :return:
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        hypervisor.node_sal.client.kvm.create = MagicMock()
        hypervisor.create()

        assert hypervisor.node_sal.client.kvm.create.called

    def test_destroy_hypervisor_not_created(self):
        """
        Test destroying the hypervisor without creation
        """
        with pytest.raises(StateCheckError, message='Starting hypervisor before install should raise an error'):
            hypervisor = Hypervisor('hypervisor', data=self.valid_data)
            hypervisor.node_sal.client.kvm.destroy = MagicMock()
            hypervisor.destroy()

    def test_destroy_hypervisor(self):
        """
        Test successfully destroying the hypervisor
        :return:
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        hypervisor.node_sal.client.kvm.destroy = MagicMock()
        hypervisor.state.set('actions', 'create', 'ok')
        hypervisor.data['uid'] = 'uid'
        hypervisor.destroy()

        assert hypervisor.node_sal.client.kvm.destroy.called

    def test_shutdown_hypervisor_not_created(self):
        """
        Test shuting down the hypervisor without creation
        """
        with pytest.raises(StateCheckError, message='Starting hypervisor before install should raise an error'):
            hypervisor = Hypervisor('hypervisor', data=self.valid_data)
            hypervisor.node_sal.client.kvm.shutdown = MagicMock()
            hypervisor.shutdown()

    def test_shutdown_hypervisor(self):
        """
        Test successfully shuting down the hypervisor
        :return:
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        hypervisor.node_sal.client.kvm.shutdown = MagicMock()
        hypervisor.state.set('actions', 'create', 'ok')
        hypervisor.data['uid'] = 'uid'
        hypervisor.shutdown()

        assert hypervisor.node_sal.client.kvm.shutdown.called

    def test_pause_hypervisor_not_created(self):
        """
        Test pause the hypervisor without creation
        """
        with pytest.raises(StateCheckError, message='Starting hypervisor before install should raise an error'):
            hypervisor = Hypervisor('hypervisor', data=self.valid_data)
            hypervisor.node_sal.client.kvm.pause = MagicMock()
            hypervisor.pause()

    def test_pause_hypervisor(self):
        """
        Test successfully pause the hypervisor
        :return:
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        hypervisor.node_sal.client.kvm.pause = MagicMock()
        hypervisor.state.set('actions', 'create', 'ok')
        hypervisor.data['uid'] = 'uid'
        hypervisor.pause()

        assert hypervisor.node_sal.client.kvm.pause.called

    def test_resume_hypervisor_not_created(self):
        """
        Test resume the hypervisor without creation
        """
        with pytest.raises(StateCheckError, message='Starting hypervisor before install should raise an error'):
            hypervisor = Hypervisor('hypervisor', data=self.valid_data)
            hypervisor.node_sal.client.kvm.resume = MagicMock()
            hypervisor.resume()

    def test_resume_hypervisor(self):
        """
        Test successfully resume the hypervisor
        :return:
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        hypervisor.node_sal.client.kvm.resume = MagicMock()
        hypervisor.state.set('actions', 'create', 'ok')
        hypervisor.data['uid'] = 'uid'
        hypervisor.resume()

        assert hypervisor.node_sal.client.kvm.resume.called

    def test_reboot_hypervisor_not_created(self):
        """
        Test reboot the hypervisor without creation
        """
        with pytest.raises(StateCheckError, message='Starting hypervisor before install should raise an error'):
            hypervisor = Hypervisor('hypervisor', data=self.valid_data)
            hypervisor.node_sal.client.kvm.reboot = MagicMock()
            hypervisor.reboot()

    def test_reboot_hypervisor(self):
        """
        Test successfully pause the hypervisor
        :return:
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        hypervisor.node_sal.client.kvm.reboot = MagicMock()
        hypervisor.state.set('actions', 'create', 'ok')
        hypervisor.data['uid'] = 'uid'
        hypervisor.reboot()

        assert hypervisor.node_sal.client.kvm.reboot.called

    def test_reset_hypervisor_not_created(self):
        """
        Test reset the hypervisor without creation
        """
        with pytest.raises(StateCheckError, message='Starting hypervisor before install should raise an error'):
            hypervisor = Hypervisor('hypervisor', data=self.valid_data)
            hypervisor.node_sal.client.kvm.reset = MagicMock()
            hypervisor.reset()

    def test_reset_hypervisor(self):
        """
        Test successfully reset the hypervisor
        :return:
        """
        hypervisor = Hypervisor('hypervisor', data=self.valid_data)
        hypervisor.node_sal.client.kvm.reset = MagicMock()
        hypervisor.state.set('actions', 'create', 'ok')
        hypervisor.data['uid'] = 'uid'
        hypervisor.reset()

        assert hypervisor.node_sal.client.kvm.reset.called
