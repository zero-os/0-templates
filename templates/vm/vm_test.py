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
            'ports': ['80:80'],
            'media': [],
            'mount': {},
            'tags': [],
            'uuid': '444d10d7-77f8-4b33-a6df-feb76e34dbc4',
            'configs': [{'path': '/file/path', 'content': 'file-content'}]
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
        Test the _node_sal property
        """
        vm = Vm('vm', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.get_node',  MagicMock(return_value=node_sal_return)).start()

        assert vm._node_sal == node_sal_return
        j.clients.zero_os.sal.get_node.assert_called_with(NODE_CLIENT)

    def test_hypervisor_sal(self):
        """
        Test the _hypervisor_sal property
        """
        vm = Vm('vm', data=self.valid_data)
        hv_sal = 'hv_sal'
        vm._node_sal.hypervisor.get = MagicMock(return_value=hv_sal)
        assert vm._hypervisor_sal == hv_sal

    def test_install_vm(self):
        """
        Test successfully creating a vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.install()
        assert 'uuid' in vm.data
        args = {
            'name': 'vm',
            'media': self.valid_data['media'],
            'flist': self.valid_data['flist'],
            'cpu': self.valid_data['cpu'],
            'memory': self.valid_data['memory'],
            'nics': self.valid_data['nics'],
            'ports': self.valid_data['ports'],
            'mounts': self.valid_data.get('mount'),
            'tags': self.valid_data.get('tags'),
            'config': {'/file/path': 'file-content'},
        }
        vm._node_sal.hypervisor.create.called_once_with(**args)
        vm.state.check('actions', 'install', 'ok')
        vm.state.check('status', 'running', 'ok')

    def test_uninstall_vm(self):
        """
        Test successfully destroying the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'install', 'ok')
        vm.state.delete = MagicMock()
        vm.uninstall()

        self.node.hypervisor.get.return_value.destroy.assert_called_with(['80:80'])
        vm.state.delete.assert_called_once_with('actions', 'install')

    def test_uninstall_vm_not_installed(self):
        """
        Test uninstalling vm before install
        """
        with pytest.raises(StateCheckError, message='uninstall vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.uninstall()

    def test_shutdown_vm_not_running(self):
        """
        Test shutting down the vm without creation
        """
        with pytest.raises(StateCheckError, message='Shuting down vm that is not running should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.shutdown()

    def test_shutdown_vm(self):
        """
        Test successfully shutting down the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('status', 'running', 'ok')
        vm.state.delete = MagicMock()

        vm.shutdown()

        self.node.hypervisor.get.return_value.shutdown.assert_called_with(['80:80'])
        vm.state.check('status', 'shutdown', 'ok')
        vm.state.delete.assert_called_with('status', 'running')

    def test_pause_vm_not_running(self):
        """
        Test pausing the vm without creation
        """
        with pytest.raises(StateCheckError, message='Pausing vm that is not running'):
            vm = Vm('vm', data=self.valid_data)
            vm.pause()

    def test_pause_vm(self):
        """
        Test successfully pausing the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('status', 'running', 'ok')
        vm.state.delete = MagicMock()

        vm.pause()

        self.node.hypervisor.get.return_value.pause.assert_called_with()
        vm.state.delete.assert_called_once_with('status', 'running')
        vm.state.check('actions', 'pause', 'ok')

    def test_resume_vm_not_pause(self):
        """
        Test resume the vm without creation
        """
        with pytest.raises(StateCheckError, message='Resuming vm before pause should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.resume()

    def test_resume_vm(self):
        """
        Test successfully resume the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'pause', 'ok')
        vm.state.delete = MagicMock()
        vm.resume()

        self.node.hypervisor.get.return_value.resume.assert_called_with()
        vm.state.check('status', 'running', 'ok')
        vm.state.delete.assert_called_once_with('actions', 'pause')

    def test_reboot_vm_not_installed(self):
        """
        Test reboot the vm without creation
        """
        with pytest.raises(StateCheckError, message='Rebooting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.reboot()

    def test_reboot_vm(self):
        """
        Test successfully reboot the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'install', 'ok')
        vm.reboot()
        self.node.hypervisor.get.return_value.reboot.assert_called_with()
        vm.state.check('status', 'rebooting', 'ok')

    def test_reset_vm_not_installed(self):
        """
        Test reset the vm without creation
        """
        with pytest.raises(StateCheckError, message='Resetting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.reset()

    def test_reset_vm(self):
        """
        Test successfully reset the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'install', 'ok')
        vm.reset()
        self.node.hypervisor.get.return_value.reset.assert_called_with()

    def test_enable_vnc_vm_not_installed(self):
        """
        Test enable_vnc vm not installed
        """
        with pytest.raises(StateCheckError, message='enable vnc before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.enable_vnc()

    def test_enable_vnc(self):
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('actions', 'install', 'ok')
        self.node.hypervisor.get.return_value = MagicMock(info={'vnc': 90})
        vm.enable_vnc()
        self.node.hypervisor.get.return_value.enable_vnc.assert_called_with()
        vm.state.check('vnc', 90, 'ok')

    def test_disable_vnc(self):
        """
        Test disable_vnc when there is a vnc port
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('vnc', 90, 'ok')
        vm.state.set('actions', 'install', 'ok')
        vm.state.delete = MagicMock()
        self.node.hypervisor.get.return_value = MagicMock(info={'vnc': 90})
        vm.disable_vnc()
        self.node.hypervisor.get.return_value.disable_vnc.assert_called_with()
        vm.state.delete.assert_called_once_with('vnc', 90)

    def test_disable_vnc_before_enable(self):
        """
        Test disable vnc before enable
        :return:
        """
        with pytest.raises(StateCheckError, message='disable vnc before enable should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.disable_vnc()

    def test_monitor_vm_not_running(self):
        """
        Test monitor vm not running
        """
        vm = Vm('vm', data=self.valid_data)
        vm._hypervisor_sal.is_running.return_value = False
        vm.state.delete = MagicMock()
        vm.state.set('actions', 'install', 'ok')

        vm._monitor()
        vm.state.delete.assert_called_once_with('status', 'running')

    def test_monitor_vm_running(self):
        """
        Test monitor vm running
        """
        vm = Vm('vm', data=self.valid_data)
        vm.state.set('status', 'rebooting', 'ok')
        vm.state.set('status', 'shutdown', 'ok')
        vm.state.set('actions', 'install', 'ok')
        vm._hypervisor_sal.is_running.return_value = True
        vm.state.delete = MagicMock()

        vm._monitor()
        assert vm.state.delete.call_count == 2

    def test_monitor_before_install(self):
        """
        Test monitor before install
        :return:
        """
        with pytest.raises(StateCheckError, message='monitor vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm._monitor()
