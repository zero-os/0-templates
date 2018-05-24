import os
import pytest
import tempfile
import shutil
from unittest import TestCase
from unittest import mock
from unittest.mock import MagicMock

from js9 import j
from zerorobot import config, template_collection
from zerorobot.template_uid import TemplateUID
from zerorobot.template.state import StateCheckError

from zeroboot_ipmi_host import ZerobootIpmiHost

class TestZerobootIpmiHostTemplate(TestCase):
    @classmethod
    def setUpClass(cls):
        config.DATA_DIR = '/tmp'
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        ZerobootIpmiHost.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (
                ZerobootIpmiHost.template_name, ZerobootIpmiHost.version))

        cls._valid_data = {
            'zerobootClient': 'zboot1-zb',
            'ipmiClient': 'zboot1-ipmi',
            'mac': 'well:this:a:weird:mac:address',
            'ip': '10.10.1.1',
            'network': '10.10.1.0/24',
            'hostname': 'test-01',
            'ipxeUrl': 'some.ixpe.url',
        }

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    @mock.patch.object(j.clients, '_ipmi')
    @mock.patch.object(j.clients, '_zboot')
    def test_validation_required_fields(self, zboot, ipmi):
        zboot.list = MagicMock(return_value=[self._valid_data['zerobootClient']])
        ipmi.list = MagicMock(return_value=[self._valid_data['ipmiClient']])

        test_cases = [
            {
                'data': {
                    'ipmiClient': 'zboot1-ipmi',
                    'mac': 'well:this:a:weird:mac:address',
                    'ip': '10.10.1.1',
                    'network': '10.10.1.0/24',
                    'hostname': 'test-01',
                    'ipxeUrl': 'some.ixpe.url',
                },
                'message': "Should fail: missing zerobootClient",
                'valid': False,
                'missing': 'zerobootClient',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'mac': 'well:this:a:weird:mac:address',
                    'ip': '10.10.1.1',
                    'network': '10.10.1.0/24',
                    'hostname': 'test-01',
                    'ipxeUrl': 'some.ixpe.url',
                },
                'message': "Should fail: missing ipmiClient",
                'valid': False,
                'missing': 'ipmiClient',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'ipmiClient': 'zboot1-ipmi',
                    'mac': 'well:this:a:weird:mac:address',
                    'ip': '10.10.1.1',
                    'hostname': 'test-01',
                    'ipxeUrl': 'some.ixpe.url',
                },
                'message': "Should fail: missing network",
                'valid': False,
                'missing': 'network',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'ipmiClient': 'zboot1-ipmi',
                    'mac': 'well:this:a:weird:mac:address',
                    'ip': '10.10.1.1',
                    'network': '10.10.1.0/24',
                    'ipxeUrl': 'some.ixpe.url',
                },
                'message': "Should fail: missing hostname",
                'valid': False,
                'missing': 'hostname',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'ipmiClient': 'zboot1-ipmi',
                    'ip': '10.10.1.1',
                    'network': '10.10.1.0/24',
                    'hostname': 'test-01',
                    'ipxeUrl': 'some.ixpe.url',
                },
                'message': "Should fail: missing mac address",
                'valid': False,
                'missing': 'mac',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'ipmiClient': 'zboot1-ipmi',
                    'network': '10.10.1.0/24',
                    'mac': 'well:this:a:weird:mac:address',
                    'hostname': 'test-01',
                },
                'message': "Should fail: missing ip address",
                'valid': False,
                'missing': 'ip',
            },
            {
                'data': self._valid_data,
                'message': "Should succeed: all mandatory fields should be provided",
                'valid': True,
            },
        ]

        for tc in test_cases:
            instance = ZerobootIpmiHost(name="test", data=tc['data'])
            if tc['valid']:
                instance.validate()

            else:
                with pytest.raises(
                        ValueError, message="Unexpected success: %s\n\nData: %s" %(tc['message'], tc['data'])) as excinfo:
                    instance.validate()
                
                if tc['missing'] not in str(excinfo):
                    pytest.fail(
                        "Error message did not contain missing field('%s'): %s" % (tc['missing'], str(excinfo)))

    @mock.patch.object(j.clients, '_ipmi')
    @mock.patch.object(j.clients, '_zboot')
    def test_validate_no_zboot_instance(self, zboot, ipmi):
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)

        zboot.list = MagicMock(return_value=[])
        ipmi.list = MagicMock(return_value=[self._valid_data['ipmiClient']])
        instance.power_status = MagicMock(return_value=True)

        with pytest.raises(RuntimeError, message="zeroboot instance should not be present") as excinfo:
            instance.validate()
        if "zboot client" not in str(excinfo.value):
            pytest.fail("Received unexpected error message for missing zboot instance: %s" % str(excinfo.value))

    @mock.patch.object(j.clients, '_ipmi')
    @mock.patch.object(j.clients, '_zboot')
    def test_validate_no_ipmi_instance(self, zboot, ipmi):
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)

        zboot.list = MagicMock(return_value=[self._valid_data['zerobootClient']])
        ipmi.list = MagicMock(return_value=[])
        instance.power_status = MagicMock(return_value=True)

        with pytest.raises(RuntimeError, message="ipmi instance should not be present") as excinfo:
            instance.validate()
        if "ipmi client" not in str(excinfo.value):
            pytest.fail("Received unexpected error message for missing ipmi instance: %s" % str(excinfo.value))

    @mock.patch.object(j.clients, '_ipmi')
    @mock.patch.object(j.clients, '_zboot')
    def test_install(self, zboot, ipmi):
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        instance._network.hosts.list = MagicMock(return_value=[])
        ipmi.get().power_status = MagicMock(return_value="on")

        instance.install()

        instance._network.hosts.add.assert_called_with(
            self._valid_data['mac'], self._valid_data['ip'], self._valid_data['hostname'])
        instance._host.configure_ipxe_boot.assert_called_with(self._valid_data['ipxeUrl'])

        # state check should pass
        instance.state.check('actions', 'install', 'ok')

    @mock.patch.object(j.clients, '_zboot')
    def test_uninstall(self, zboot):
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        instance.state.set('actions', 'install', 'ok')

        instance.uninstall()

        instance._network.hosts.remove.assert_called_with(self._valid_data['hostname'])

        with pytest.raises(StateCheckError, message="install action state check should fail"):
            instance.state.check('actions', 'install', 'ok')

    @mock.patch.object(j.clients, '_ipmi')
    @mock.patch.object(j.clients, '_zboot')
    def test_power_on(self, zboot, ipmi):
        # check when not installed
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="power_on should be not be able to be called before install"):
            instance.power_on()

        # prep mock
        instance.state.set('actions', 'install', 'ok')

        instance.power_on()
        ipmi.get().power_on.assert_called_with()

        # check if instance power state True
        assert instance.data['powerState']

    @mock.patch.object(j.clients, '_ipmi')
    @mock.patch.object(j.clients, '_zboot')
    def test_power_off(self, zboot, ipmi):
        # check when not installed
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="power_off should be not be able to be called before install"):
            instance.power_off()

        # prep mock
        instance.state.set('actions', 'install', 'ok')

        instance.power_off()
        ipmi.get().power_off.assert_called_with()

        # check if instance power state False
        assert not instance.data['powerState']

    @mock.patch.object(j.clients, '_ipmi')
    @mock.patch.object(j.clients, '_zboot')
    def test_power_cycle(self, zboot, ipmi):
        # check when not installed
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="power_cycle should be not be able to be called before install"):
            instance.power_cycle()

        # prep mock
        instance.state.set('actions', 'install', 'ok')

        instance.power_cycle()
        ipmi.get().power_cycle.assert_called_with()

    @mock.patch.object(j.clients, '_ipmi')
    @mock.patch.object(j.clients, '_zboot')
    def test_power_status(self, zboot, ipmi):
        # check when not installed
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="power_status should be not be able to be called before install"):
            instance.power_status()

        # prep mock
        instance.state.set('actions', 'install', 'ok')
        ipmi.get().power_status = MagicMock(return_value="on")

        status = instance.power_status()

        assert status == True

        ipmi.get().power_status = MagicMock(return_value="off")
        status = instance.power_status()

        assert status == False

    def test_monitor_matching_state(self):
        # check when not installed
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="monitor should be not be able to be called before install"):
            instance.monitor()

        # prep mock
        instance.state.set('actions', 'install', 'ok')
        instance.power_on = MagicMock()
        instance.power_off = MagicMock()
        instance.power_status = MagicMock(return_value=True)
        instance.data['powerState'] = True

        instance.monitor()

        # no power calls should be make
        instance.power_on.assert_not_called()
        instance.power_off.assert_not_called()

    def test_monitor_power_on(self):
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        instance.state.set('actions', 'install', 'ok')
        instance.power_on = MagicMock()
        instance.power_off = MagicMock()
        instance.power_status = MagicMock(return_value=False)
        instance.data['powerState'] = True

        instance.monitor()

        # power state mismatched, power_on should have been called
        instance.power_on.assert_called_with()
        instance.power_off.assert_not_called()

    def test_monitor_power_off(self):
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        instance.state.set('actions', 'install', 'ok')
        instance.power_on = MagicMock()
        instance.power_off = MagicMock()
        instance.power_status = MagicMock(return_value=True)
        instance.data['powerState'] = False

        instance.monitor()

        # power state mismatched, power_off should have been called
        instance.power_on.assert_not_called()
        instance.power_off.assert_called_with()

    @mock.patch.object(j.clients, '_zboot')
    def test_configure_ipxe_boot(self, zboot):
        boot_url = "some.url"

        # check when not installed
        instance = ZerobootIpmiHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="monitor should be not be able to be called before install"):
            instance.configure_ipxe_boot(boot_url)
        instance.state.set('actions', 'install', 'ok')

        # call with same ipxe URL as set in data
        instance.configure_ipxe_boot(self._valid_data["ipxeUrl"])
        instance._host.configure_ipxe_boot.assert_not_called()

        # call with difference ipxe URL as set in data
        instance.configure_ipxe_boot(boot_url)
        instance._host.configure_ipxe_boot.assert_called_with(boot_url)

        assert instance.data["ipxeUrl"] == boot_url
