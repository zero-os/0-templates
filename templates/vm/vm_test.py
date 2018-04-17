from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os

import pytest

from js9 import j
from vm import Vm, NODE_CLIENT
from zerorobot.template.state import StateCheckError
from zerorobot import service_collection as scol
from zerorobot import config
from zerorobot.template_uid import TemplateUID


class TestVmTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {
            'cpu': 1,
            'flist': 'flist',
            'memory': 128,
            'nics': [],
            'vnc': -1,
            'ports': [],
            'media': [],
            'mount': {},
            'tags': [],
            'uuid': '444d10d7-77f8-4b33-a6df-feb76e34dbc4',
        }

        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Vm.template_uid = TemplateUID.parse('github.com/zero-os/0-templates/%s/%s' % (Vm.template_name, Vm.version))
        cls.vnc_port = 5900

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def setUp(self):
        mock = MagicMock()
        self.node = mock.return_value
        patch('js9.j.clients.zero_os.sal.get_node', mock).start()
        patch('js9.j.clients.zero_os.sal.get_vm', MagicMock()).start()

    def tearDown(self):
        patch.stopall()

    def test_invalid_data(self):
        """
        Test creating a vm with invalid data
        """
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the node'):
            vm = Vm(name='vm', data={})
            vm.validate()

    def test_valid_data(self):
        """
        Test creating a vm service with valid data
        """
        vm = Vm('vm', data=self.valid_data)
        vm.validate()
        assert vm.data == self.valid_data

    def test_node_sal(self):
        """
        Test the node_sal property
        """
        vm = Vm('vm', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.get_node',  MagicMock(return_value=node_sal_return)).start()
        node_sal = vm.node_sal

        assert node_sal == node_sal_return
        j.clients.zero_os.sal.get_node.assert_called_with(NODE_CLIENT)

    def test_install_vm(self):
        """
        Test successfully creating a vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.install()
        assert 'uuid' in vm.data

    def test_uninstall_vm(self):
        """
        Test successfully destroying the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.uninstall()

        self.node.hypervisor.get.return_value.destroy.assert_called_with()

    def test_shutdown_vm_hypervisor_not_created(self):
        """
        Test shutting down the vm without creation
        """
        with pytest.raises(StateCheckError, message='Shuting down vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.shutdown()

    def test_shutdown_vm(self):
        """
        Test successfully shutting down the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.state = MagicMock()
        vm.shutdown()
        self.node.hypervisor.get.return_value.shutdown.assert_called_with()

    def test_pause_vm_hypervisor_not_created(self):
        """
        Test pausing the vm without creation
        """
        with pytest.raises(StateCheckError, message='Pausing vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.pause()

    def test_pause_vm(self):
        """
        Test successfully pausing the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.state = MagicMock()
        vm.pause()
        self.node.hypervisor.get.return_value.pause.assert_called_with()

    def test_resume_vm_hypervisor_not_created(self):
        """
        Test resume the vm without creation
        """
        with pytest.raises(StateCheckError, message='Resuming vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.resume()

    def test_resume_vm(self):
        """
        Test successfully resume the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.state = MagicMock()
        vm.resume()
        self.node.hypervisor.get.return_value.resume.assert_called_with()

    def test_reboot_vm_hypervisor_not_created(self):
        """
        Test reboot the vm without creation
        """
        with pytest.raises(StateCheckError, message='Rebooting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.reboot()

    def test_reboot_vm(self):
        """
        Test successfully reboot the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.state = MagicMock()
        vm.reboot()
        self.node.hypervisor.get.return_value.reboot.assert_called_with()

    def test_reset_vm_hypervisor_not_created(self):
        """
        Test reset the vm without creation
        """
        with pytest.raises(StateCheckError, message='Resetting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.reset()

    def test_reset_vm(self):
        """
        Test successfully reset the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.state = MagicMock()
        vm.reset()
        self.node.hypervisor.get.return_value.reset.assert_called_with()

    def test_enable_vnc(self):
        """
        Test enable_vnc when there is a vnc port
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state = MagicMock()
        vm.enable_vnc()
        self.node.hypervisor.get.return_value.enable_vnc.assert_called_with()

    def test_disable_vnc(self):
        """
        Test disable_vnc when there is a vnc port
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state = MagicMock()
        vm.disable_vnc()
        self.node.hypervisor.get.return_value.disable_vnc.assert_called_with()
