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

from zeroboot_pool import ZerobootPool

class TestZerobootPoolTemplate(TestCase):
    @classmethod
    def setUpClass(cls):
        config.DATA_DIR = '/tmp'
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        ZerobootPool.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (
                ZerobootPool.template_name, ZerobootPool.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def test_valid_host_validation(self):
        pool = ZerobootPool(name="test")
        # mock racktivity host service
        pool.api.services.get = MagicMock(return_value=MagicMock(template_uid="github.com/zero-os/0-templates/zeroboot_racktivity_host/0.0.1"))
        pool.api.services.get().state.check = MagicMock(return_value=None)

        try:
            pool._validate_host("test_host_instance")
        except BaseException as err:
            pytest.fail("unexpected error: %s" % err)

    def test_host_validation_invalid_template(self):
        pool = ZerobootPool(name="test")
        # mock racktivity host service
        pool.api.services.get = MagicMock(return_value=MagicMock(template_uid="github.com/zero-os/0-templates/a_random_template/0.0.1"))
        pool.api.services.get().state.check = MagicMock(return_value=None)

        with pytest.raises(RuntimeError, message="Invalid template should raise RuntimeError"):
            pool._validate_host("test_host_instance")

    def test_host_validation_failed_state_check(self):
        pool = ZerobootPool(name="test")
        # mock racktivity host service
        pool.api.services.get = MagicMock(return_value=MagicMock(template_uid="github.com/zero-os/0-templates/zeroboot_racktivity_host/0.0.1"))
        pool.api.services.get().state.check = MagicMock(side_effect=StateCheckError("state check failed"))

        with pytest.raises(StateCheckError, message="Uninstalled host should raise StateCheckError"):
            pool._validate_host("test_host_instance")

    def test_validation_duplicate_hosts(self):
        # valid: doesn't contain duplicate hosts
        pool = ZerobootPool(name="test", data={"zerobootHosts": ["host1", "host2"]})
        pool._validate_host = MagicMock()

        try:
            pool.validate()
        except BaseException as err:
            pytest.fail("Unexpected error: %s" % err)

        # data contains duplicate hosts
        pool = ZerobootPool(name="test", data={"zerobootHosts": ["host1", "host2", "host1"]})
        pool._validate_host = MagicMock()

        with pytest.raises(ValueError, message="invalid data should contain duplicate host names"):
            pool.validate()

    def test_add_remove(self):
        pool = ZerobootPool(name="test", data={"zerobootHosts": ["host1", "host2"]})
        pool._validate_host = MagicMock()

        # add new host
        pool.add("host3")

        assert len(pool.data.get("zerobootHosts")) == 3

        # remove host
        pool.remove("host3")

        assert len(pool.data.get("zerobootHosts")) == 2

        # remove non existing host
        pool.remove("ghost_host")

        assert len(pool.data.get("zerobootHosts")) == 2

    def test_add_duplicate(self):
        pool = ZerobootPool(name="test", data={"zerobootHosts": ["host1", "host2"]})
        pool._validate_host = MagicMock()

        # add already existing host
        with pytest.raises(ValueError, message="Adding already present host should raise ValueError"):
            pool.add("host1")

    def test_unreserved_host(self):
        hosts = ["host1", "host2"]
        pool = ZerobootPool(name="test", data={"zerobootHosts": hosts})
        pool._validate_host = MagicMock()
        pool.api = MagicMock()

        # request unreserved host, check if host is in hosts list
        r1 = pool.unreserved_host("some-guid")

        if r1 not in hosts:
            pytest.fail("Returned host was not in set hosts list")

        # mock first reservation
        mock_res1 = MagicMock()
        mock_res1.schedule_action().wait().result = r1
        pool.api.services.find = MagicMock(return_value=[mock_res1])

        # request another unreserved host, check if host is in hosts list and is not the first host
        r2 = pool.unreserved_host("some-guid")

        if r2 not in hosts:
            pytest.fail("Returned host was not in set hosts list")
        
        if r1 == r2:
            pytest.fail("Different reservations can not be of the same host: reservation1:'%s'; reservation2:'%s'" % (r1, r2))

        # mock second reservation
        mock_res1 = MagicMock()
        mock_res1.schedule_action().wait().result = r1
        mock_res2 = MagicMock()
        mock_res2.schedule_action().wait().result = r2
        pool.api.services.find = MagicMock(return_value=[mock_res1, mock_res2])

        # there are only 2 available hosts, third reservation should fail
        with pytest.raises(ValueError, message="There should not be any free hosts left, thus unreserved_host will raise a ValueError"):
            r3 = pool.unreserved_host("some-guid")
