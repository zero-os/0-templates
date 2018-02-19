from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock
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
        cls.vnc_port = 5900

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

    def test_node_sal(self):
        """
        Test the node_sal property
        """
        vm = Vm('vm', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.node_get',  MagicMock(return_value=node_sal_return)).start()
        node_sal = vm.node_sal

        assert node_sal == node_sal_return
        j.clients.zero_os.sal.node_get.assert_called_with(self.valid_data['node'])

    def test_install_vm_node_not_found(self):
        """
        Test installing a vm with no service found for the node
        """
        with pytest.raises(scol.ServiceNotFoundError,
                           message='install action should raise an error if node service is not found'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.install()

    def test_install_vm_node_not_installed(self):
        """
        Test installing the vm without the node being installed
        """
        with pytest.raises(StateCheckError,
                           message='install action should raise an error if the node is not installed'):
            vm = Vm('vm', data=self.valid_data)
            node = MagicMock()
            vm.api.services.get = MagicMock(return_value=node)
            node.state.check = MagicMock(side_effect=StateCheckError)
            vm.install()

    def test_install_vm(self):
        """
        Test successfully creating a vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        task = MagicMock(state='ok')
        hyperviser = MagicMock()
        hyperviser.schedule_action = MagicMock(return_value=task)
        vm.api.services.create = MagicMock(return_value=hyperviser)
        vm.install()

    def test_install_vm_fail(self):
        """
        Test vm install fails and hypervisor guid not in services list
        """
        with pytest.raises(RuntimeError,
                           message='install action should raise an error if the hypervisor state is not ok'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services = MagicMock()
            patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
            vm.install()
            assert vm._hypervisor is not None

    def test_install_vm_fail_hypervisor_delete(self):
        """
        Test vm install fails and hypervisor guid in services list
        """
        with pytest.raises(RuntimeError,
                           message='install action should raise an error if the hypervisor state is not ok'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services = MagicMock(guids={'guid': MagicMock()})
            vm.api.services.create = MagicMock(guid='guid')
            patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
            vm.install()
            assert vm._hypervisor is None

    def test_uninstall_vm_hypervisor_not_created(self):
        """
        Test uninstalling the vm without creation
        """
        with pytest.raises(scol.ServiceNotFoundError, message='Uninstall vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.uninstall()

    def test_uninstall_vm(self):
        """
        Test successfully destroying the vm
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
        with pytest.raises(scol.ServiceNotFoundError, message='Shuting down vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.shutdown()

    def test_shutdown_vm(self):
        """
        Test successfully shutting down the vm
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
        with pytest.raises(scol.ServiceNotFoundError, message='Pausing vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.pause()

    def test_pause_vm(self):
        """
        Test successfully pausing the vm
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
        with pytest.raises(scol.ServiceNotFoundError, message='Resuming vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.resume()

    def test_resume_vm(self):
        """
        Test successfully resume the vm
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
        with pytest.raises(scol.ServiceNotFoundError, message='Rebooting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.reboot()

    def test_reboot_vm(self):
        """
        Test successfully reboot the vm
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
        with pytest.raises(scol.ServiceNotFoundError, message='Resetting vm before install should raise an error'):
            vm = Vm('vm', data=self.valid_data)
            vm.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            vm.reset()

    def test_reset_vm(self):
        """
        Test successfully reset the vm
        """
        vm = Vm('vm', data=self.valid_data)
        vm.api.services.get = MagicMock()
        vm.hypervisor.schedule_action = MagicMock()
        vm.reset()

        vm.hypervisor.schedule_action.assert_called_with('reset')

    def test_get_vnc_port(self):
        """
        Test _get_vnc_port when there is a vnc port
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        vm = Vm('vm', data=self.valid_data)
        vm.node_sal.client.kvm.list = MagicMock(return_value=[{'name': vm.hv_name, 'vnc': self.vnc_port}])
        assert vm._get_vnc_port() == self.vnc_port

    def test_get_vnc_port_no_port(self):
        """
        Test _get_vnc_port when there is no vnc port
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        vm = Vm('vm', data=self.valid_data)
        vm.node_sal.client.kvm.list = MagicMock(return_value=[])
        assert vm._get_vnc_port() is None

    def test_enable_vnc(self):
        """
        Test enable_vnc when there is a vnc port
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        vm = Vm('vm', data=self.valid_data)
        vm._get_vnc_port = MagicMock(return_value=self.vnc_port)
        vm.node_sal.client.nft.open_port = MagicMock()
        vm.enable_vnc()
        vm.node_sal.client.nft.open_port.assert_called_with(self.vnc_port)

    def test_enable_vnc_no_port(self):
        """
        Test enable_vnc when there is no vnc port
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        vm = Vm('vm', data=self.valid_data)
        vm._get_vnc_port = MagicMock(return_value=None)
        vm.node_sal.client.nft.open_port = MagicMock()
        vm.enable_vnc()
        vm.node_sal.client.nft.open_port.assert_not_called()

    def test_disable_vnc(self):
        """
        Test disable_vnc when there is a vnc port
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        vm = Vm('vm', data=self.valid_data)
        vm._get_vnc_port = MagicMock(return_value=self.vnc_port)
        vm.node_sal.client.nft.drop_port = MagicMock()
        vm.disable_vnc()
        vm.node_sal.client.nft.drop_port.assert_called_with(self.vnc_port)

    def test_disable_vnc_no_port(self):
        """
        Test disable_vnc when there is no vnc port
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        vm = Vm('vm', data=self.valid_data)
        vm._get_vnc_port = MagicMock(return_value=None)
        vm.node_sal.client.nft.drop_port = MagicMock()
        vm.disable_vnc()
        vm.node_sal.client.nft.drop_port.assert_not_called()
