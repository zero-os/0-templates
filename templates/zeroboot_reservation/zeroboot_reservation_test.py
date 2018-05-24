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

from zeroboot_reservation import ZerobootReservation

class TestZerobootReservationTemplate(TestCase):
    @classmethod
    def setUpClass(cls):
        config.DATA_DIR = '/tmp'
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        ZerobootReservation.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (
                ZerobootReservation.template_name, ZerobootReservation.version))

        cls._valid_data = {"zerobootPool": "pool1", "ipxeUrl": "some-url"}

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def test_validation(self):
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()

        reservation.validate()
    
    def test_validation_invalid_data(self):
        data = {
            "zerobootPool": "pool1",
        }
        reservation = ZerobootReservation(name="test", data=data)
        reservation.api = MagicMock()

        # missing ipxeUrl
        with pytest.raises(ValueError, message="Should fail due to missing ipxeUrl") as exinfo:
            reservation.validate()
        if not "ipxeUrl" in str(exinfo):
            pytest.fail("Validation failed but did not contain missing data 'ipxeUrl': %s" % exinfo)

        # missing pool 
        reservation.data = {
            "ipxeUrl": "some-url",
        }

        with pytest.raises(ValueError, message="Should fail due to missing zerobootPool") as exinfo:
            reservation.validate()
        if not "zerobootPool" in str(exinfo):
            pytest.fail("Validation failed but did not contain missing data 'zerobootPool': %s" % exinfo)

    def test_validation_zeroboot_host(self):
        # provide zeroboot host before installing
        data = {
            "ipxeUrl": "some-url",
            "zerobootPool": "pool1",
            "zerobootHost": "host-foo",
        }
        reservation = ZerobootReservation(name="test", data=data)
        reservation.api = MagicMock()

        with pytest.raises(ValueError, message="Should fail due to provided zerobootHost before installing") as exinfo:
            reservation.validate()
        if not "zerobootHost" in str(exinfo):
            pytest.fail("Expected an error but received error was not for 'zerobootHost': %s" % exinfo)

        # no zeroboot host after installing
        reservation.state.set("actions", "install", "ok")
        reservation.data = {
            "ipxeUrl": "some-url",
            "zerobootPool": "pool1",
        }
        with pytest.raises(ValueError, message="Should fail due to provided missing zerobootHost after installing") as exinfo:
            reservation.validate()
        if not "zerobootHost" in str(exinfo):
            pytest.fail("Expected an error but received error was not for 'zerobootHost': %s" % exinfo)

    def test_install(self):
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()
        reserved_host = "host1"
        mock_pool1 = MagicMock()
        mock_pool1.schedule_action().wait().result = reserved_host
        reservation.api.services.get = MagicMock(return_value=mock_pool1)

        reservation.install()

        reservation.state.check("actions", "install", "ok")

    def test_uninstall(self):
        # install
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()
        reserved_host = "host1"
        mock_pool1 = MagicMock()
        mock_pool1.schedule_action().wait().result = reserved_host
        reservation.api.services.get = MagicMock(return_value=mock_pool1)
        reservation.install()

        # should not fail as service was installed
        reservation.state.check("actions", "install", "ok")

        # uninstall
        reservation.uninstall()

        # check power off called
        reservation.api.services.get().schedule_action.assert_called_with("power_off")

        # check 'zerobootHost' cleared
        if reservation.data.get('zerobootHost'):
            pytest.fail("'zerobootHost' should be cleared after uninstall")

        # check action install state
        with pytest.raises(StateCheckError, message="reservation service should now be uninstalled"):
            reservation.state.check("actions", "install", "ok")

    def test_power_on_installed(self):
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()

        with pytest.raises(StateCheckError, message="power_on should failed as the service in not installed"):
            reservation.power_on()

        reservation.install()

        reservation.power_on()

    def test_power_off_installed(self):
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()

        with pytest.raises(StateCheckError, message="power_off should failed as the service in not installed"):
            reservation.power_off()

        reservation.install()

        reservation.power_off()

    def test_power_cycle_installed(self):
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()

        with pytest.raises(StateCheckError, message="power_cycle should failed as the service in not installed"):
            reservation.power_cycle()

        reservation.install()

        reservation.power_cycle()

    def test_power_status_installed(self):
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()

        with pytest.raises(StateCheckError, message="power_status should failed as the service in not installed"):
            reservation.power_status()

        reservation.install()

        reservation.power_status()

    def test_monitor_installed(self):
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()

        with pytest.raises(StateCheckError, message="monitor should failed as the service in not installed"):
            reservation.monitor()

        reservation.install()

        reservation.monitor()

    def test_configure_ipxe_boot_installed(self):
        reservation = ZerobootReservation(name="test", data=self._valid_data)
        reservation.api = MagicMock()

        with pytest.raises(StateCheckError, message="configure_ipxe_boot should failed as the service in not installed"):
            reservation.configure_ipxe_boot("some.boot.url")

        reservation.install()

        reservation.configure_ipxe_boot("some.boot.url")
