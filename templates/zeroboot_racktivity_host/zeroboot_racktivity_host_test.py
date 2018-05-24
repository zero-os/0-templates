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

from zeroboot_racktivity_host import ZerobootRacktivityHost

class TestZerobootRacktivityHostTemplate(TestCase):
    @classmethod
    def setUpClass(cls):
        config.DATA_DIR = '/tmp'
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        ZerobootRacktivityHost.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (
                ZerobootRacktivityHost.template_name, ZerobootRacktivityHost.version))

        cls._valid_data = {
            'zerobootClient': 'zboot1-zb',
            'racktivityClient': 'zboot1-rack',
            'mac': 'well:this:a:weird:mac:address',
            'ip': '10.10.1.1',
            'network': '10.10.1.0/24',
            'hostname': 'test-01',
            'ipxeUrl': 'some.ixpe.url',
            'racktivityPort': 123456,
        }

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    @mock.patch.object(j.clients, '_racktivity')
    @mock.patch.object(j.clients, '_zboot')
    def test_validation_required_fields(self, zboot, rack):
        zboot.list = MagicMock(return_value=[self._valid_data['zerobootClient']])
        rack.list = MagicMock(return_value=[self._valid_data['racktivityClient']])

        test_cases = [
            {
                'data': {
                    'racktivityClient': 'zboot1-rack',
                    'mac': 'well:this:a:weird:mac:address',
                    'ip': '10.10.1.1',
                    'network': '10.10.1.0/24',
                    'hostname': 'test-01',
                    'ipxeUrl': 'some.ixpe.url',
                    'racktivityPort': 1,
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
                    'racktivityPort': 1,
                },
                'message': "Should fail: missing racktivityClient",
                'valid': False,
                'missing': 'racktivityClient',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'racktivityClient': 'zboot1-rack',
                    'mac': 'well:this:a:weird:mac:address',
                    'ip': '10.10.1.1',
                    'hostname': 'test-01',
                    'ipxeUrl': 'some.ixpe.url',
                    'racktivityPort': 1,
                },
                'message': "Should fail: missing network",
                'valid': False,
                'missing': 'network',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'racktivityClient': 'zboot1-rack',
                    'mac': 'well:this:a:weird:mac:address',
                    'ip': '10.10.1.1',
                    'network': '10.10.1.0/24',
                    'ipxeUrl': 'some.ixpe.url',
                    'racktivityPort': 1,
                },
                'message': "Should fail: missing hostname",
                'valid': False,
                'missing': 'hostname',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'racktivityClient': 'zboot1-rack',
                    'mac': 'well:this:a:weird:mac:address',
                    'ip': '10.10.1.1',
                    'network': '10.10.1.0/24',
                    'hostname': 'test-01',
                    'ipxeUrl': 'some.ixpe.url',
                },
                'message': "Should fail: missing racktivityPort",
                'valid': False,
                'missing': 'racktivityPort',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'racktivityClient': 'zboot1-rack',
                    'ip': '10.10.1.1',
                    'network': '10.10.1.0/24',
                    'hostname': 'test-01',
                    'ipxeUrl': 'some.ixpe.url',
                    'racktivityPort': 1,
                },
                'message': "Should fail: missing mac address",
                'valid': False,
                'missing': 'mac',
            },
            {
                'data': {
                    'zerobootClient': 'zboot1-zb',
                    'racktivityClient': 'zboot1-rack',
                    'network': '10.10.1.0/24',
                    'mac': 'well:this:a:weird:mac:address',
                    'hostname': 'test-01',
                    'racktivityPort': 1,
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
            instance = ZerobootRacktivityHost(name="test", data=tc['data'])
            if tc['valid']:
                instance.validate()
            else:
                with pytest.raises(
                        ValueError, message="Unexpected success: %s\n\nData: %s" %(tc['message'], tc['data'])) as excinfo:
                    instance.validate()
                
                if tc['missing'] not in str(excinfo):
                    pytest.fail(
                        "Error message did not contain missing field('%s'): %s" % (tc['missing'], str(excinfo)))

    @mock.patch.object(j.clients, '_racktivity')
    @mock.patch.object(j.clients, '_zboot')
    def test_validate_no_zboot_instance(self, zboot, rack):
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)

        zboot.list = MagicMock(return_value=[])
        rack.list = MagicMock(return_value=[self._valid_data['racktivityClient']])
        instance.power_status = MagicMock(return_value=True)

        with pytest.raises(RuntimeError, message="zeroboot instance should not be present") as excinfo:
            instance.validate()
        if "zboot client" not in str(excinfo.value):
            pytest.fail("Received unexpected error message for missing zboot instance: %s" % str(excinfo.value))

    @mock.patch.object(j.clients, '_racktivity')
    @mock.patch.object(j.clients, '_zboot')
    def test_validate_no_racktivity_instance(self, zboot, rack):
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)

        zboot.list = MagicMock(return_value=[self._valid_data['zerobootClient']])
        rack.list = MagicMock(return_value=[])
        instance.power_status = MagicMock(return_value=True)

        with pytest.raises(RuntimeError, message="racktivity instance should not be present") as excinfo:
            instance.validate()
        if "racktivity client" not in str(excinfo.value):
            pytest.fail("Received unexpected error message for missing racktivity instance: %s" % str(excinfo.value))

    @mock.patch.object(j.clients, '_racktivity')
    @mock.patch.object(j.clients, '_zboot')
    def test_install(self, zboot, rack):
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
        instance._network.hosts.list = MagicMock(return_value=[])

        instance.install()

        instance._network.hosts.add.assert_called_with(
            self._valid_data['mac'], self._valid_data['ip'], self._valid_data['hostname'])
        instance._host.configure_ipxe_boot.assert_called_with(self._valid_data['ipxeUrl'])

        # state check should pass
        instance.state.check('actions', 'install', 'ok')

    @mock.patch.object(j.clients, '_zboot')
    def test_uninstall(self, zboot):
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
        instance.state.set('actions', 'install', 'ok')

        instance.uninstall()

        instance._network.hosts.remove.assert_called_with(self._valid_data['hostname'])

        with pytest.raises(StateCheckError, message="install action state check should fail"):
            instance.state.check('actions', 'install', 'ok')

    @mock.patch.object(j.clients, '_racktivity')
    @mock.patch.object(j.clients, '_zboot')
    def test_power_on(self, zboot, rack):
        # check when not installed
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="power_on should be not be able to be called before install"):
            instance.power_on()

        # prep mock
        instance.state.set('actions', 'install', 'ok')
        rack.get = MagicMock()

        instance.power_on()
        zboot.get().port_power_on.assert_called_with(
            self._valid_data['racktivityPort'], mock.ANY, None)

        # check if instance power state True
        assert instance.data['powerState']

    @mock.patch.object(j.clients, '_racktivity')
    @mock.patch.object(j.clients, '_zboot')
    def test_power_off(self, zboot, rack):
        # check when not installed
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="power_off should be not be able to be called before install"):
            instance.power_off()

        # prep mock
        instance.state.set('actions', 'install', 'ok')
        rack.get = MagicMock()

        instance.power_off()
        zboot.get().port_power_off.assert_called_with(
            self._valid_data['racktivityPort'], mock.ANY, None)

        # check if instance power state False
        assert not instance.data['powerState']

    @mock.patch.object(j.clients, '_racktivity')
    @mock.patch.object(j.clients, '_zboot')
    def test_power_cycle(self, zboot, rack):
        # check when not installed
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="power_cycle should be not be able to be called before install"):
            instance.power_cycle()

        # prep mock
        instance.state.set('actions', 'install', 'ok')
        rack.get = MagicMock()

        instance.power_cycle()
        zboot.get().port_power_cycle.assert_called_with(
            [self._valid_data['racktivityPort']], mock.ANY, None)

    @mock.patch.object(j.clients, '_racktivity')
    @mock.patch.object(j.clients, '_zboot')
    def test_power_status(self, zboot, rack):
        # check when not installed
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
        with pytest.raises(StateCheckError, message="power_status should be not be able to be called before install"):
            instance.power_status()

        # prep mock
        instance.state.set('actions', 'install', 'ok')
        rack.get = MagicMock()

        instance.power_status()
        zboot.get().port_info.assert_called_with(
            self._valid_data['racktivityPort'], mock.ANY, None)

    def test_monitor_matching_state(self):
        # check when not installed
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
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
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
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
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
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
        instance = ZerobootRacktivityHost(name="test", data=self._valid_data)
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
