from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os

import pytest

from js9 import j
from vm import Vm
from zerorobot.template.state import StateCheckError
from zerorobot import service_collection as scol
from zerorobot import config
from zerorobot.template_uid import TemplateUID


class TestVmTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {'node': 'node', 'flist': 'flist'}
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Vm.template_uid = TemplateUID.parse('github.com/zero-os/0-templates/%s/%s' % (Vm.template_name, Vm.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def tearDown(self):
        patch.stopall()

    def test_invalid_data(self):
        """
        Test creating a vm with invalid data
        """
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the node'):
            Vm(name='vm', data={})

        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the node'):
            Vm(name='vm', data={'node': 'node'})

    def test_valid_data(self):
        """
        Test creating a vm service with valid data
        """
        vm = Vm('vm', data=self.valid_data)
        # assert self.valid_data == vm.data

    def test_node_sal_node_is_none(self):
        """
        Test the node_sal property when Vm._node is None
        """
        vm = Vm('vm', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.node_get',  MagicMock(return_value=node_sal_return)).start()
        node_sal = vm.node_sal

        assert node_sal == node_sal_return
        j.clients.zero_os.sal.node_get.assert_called_with(self.valid_data['node'])

    def test_node_sal_node_is_set(self):
        """
        Test the node_sal property when Vm._node is set
        """
        vm = Vm('vm', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        vm._node = node_sal_return
        node_sal = vm.node_sal

        assert node_sal == node_sal_return
        assert j.clients.zero_os.sal.node_get.called is False

    # def test_create_vm(self):
    #     """
    #     Test successfully creating a vm
    #     :return:
    #     """
    #     vm = Vm('vm', data=self.valid_data)
    #     vm.node_sal.client.kvm.create = MagicMock()
    #     vm.create()
    #
    #     assert vm.node_sal.client.kvm.create.called

    def test_uninstall_vm_hypervisor_not_created(self):
        """
        Test uninstalling the vm without creation
        """
        with pytest.raises(scol.ServiceNotFoundError, message='Starting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.uninstall()

    def test_uninstall_vm(self):
        """
        Test successfully destroying the vm
        :return:
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.hypervisor.schedule_action = MagicMock()
        vm.uninstall()

        vm.hypervisor.schedule_action.assert_called_with('destroy')

    def test_shutdown_vm_hypervisor_not_created(self):
        """
        Test shutting down the vm without creation
        """
        with pytest.raises(scol.ServiceNotFoundError, message='Starting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.shutdown()

    def test_shutdown_vm(self):
        """
        Test successfully shuting down the vm
        :return:
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.hypervisor.schedule_action = MagicMock()
        vm.shutdown()

        vm.hypervisor.schedule_action.assert_called_with('shutdown')

    def test_pause_vm_hypervisor_not_created(self):
        """
        Test pausing the vm without creation
        """
        with pytest.raises(scol.ServiceNotFoundError, message='Starting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.pause()

    def test_pause_vm(self):
        """
        Test successfully pausing the vm
        :return:
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.hypervisor.schedule_action = MagicMock()
        vm.pause()

        vm.hypervisor.schedule_action.assert_called_with('pause')

    def test_resume_vm_hypervisor_not_created(self):
        """
        Test resume the vm without creation
        """
        with pytest.raises(scol.ServiceNotFoundError, message='Starting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.resume()

    def test_resume_vm(self):
        """
        Test successfully resume the vm
        :return:
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.hypervisor.schedule_action = MagicMock()
        vm.resume()

        vm.hypervisor.schedule_action.assert_called_with('resume')

    def test_reboot_vm_hypervisor_not_created(self):
        """
        Test reboot the vm without creation
        """
        with pytest.raises(scol.ServiceNotFoundError, message='Starting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.reboot()

    def test_reboot_vm(self):
        """
        Test successfully reboot the vm
        :return:
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.hypervisor.schedule_action = MagicMock()
        vm.reboot()

        vm.hypervisor.schedule_action.assert_called_with('reboot')

    def test_reset_vm_hypervisor_not_created(self):
        """
        Test reset the vm without creation
        """
        with pytest.raises(scol.ServiceNotFoundError, message='Starting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.reset()

    def test_reset_vm(self):
        """
        Test successfully reset the vm
        :return:
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.hypervisor.schedule_action = MagicMock()
        vm.reset()

        vm.hypervisor.schedule_action.assert_called_with('reset')
