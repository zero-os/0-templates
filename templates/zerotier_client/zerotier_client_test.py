from unittest import TestCase
from unittest.mock import MagicMock
import tempfile
import shutil
import os

import pytest

from js9 import j
from zerotier_client import ZerotierClient
from zerorobot import config
from zerorobot.template_uid import TemplateUID


class TestZerotierClientTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        ZerotierClient.template_uid = TemplateUID.parse('github.com/zero-os/0-templates/%s/%s' % (ZerotierClient.template_name, ZerotierClient.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def test_create_data_none(self):
        j.clients.zerotier.list = MagicMock(return_value=[])

        with pytest.raises(ValueError, message='template should fail to instantiate if data is None'):
            ZerotierClient(name="zttest", data=None)

    def test_create_data_no_token(self):
        j.clients.zerotier.list = MagicMock(return_value=[])

        with pytest.raises(ValueError, message="template should fail to instantiate if data doesn't contain 'token'"):
            ZerotierClient(name="zttest", data={'foo': 'bar'})

        with pytest.raises(ValueError, message="template should fail to instantiate if data doesn't contain 'token'"):
            ZerotierClient(name="zttest", data={'token': ''})

    def test_create(self):
        j.clients.zerotier.list = MagicMock(return_value=[])
        j.clients.zerotier.get = MagicMock()

        data = {'token': 'foo'}
        ZerotierClient(name="zttest", data=data)
        j.clients.zerotier.list.assert_called_with()
        j.clients.zerotier.get.assert_called_with("zttest", data={'token_': data['token']})

    def test_create_already_exists(self):
        j.clients.zerotier.list = MagicMock(return_value=['zttest'])
        j.clients.zerotier.get = MagicMock()

        ZerotierClient(name="zttest", data={'token': 'foo'})
        assert j.clients.zerotier.get.called is False

    def test_delete(self):
        j.clients.zerotier.delete = MagicMock()

        service = ZerotierClient(name="zttest", data={'token': 'foo'})
        service.delete()
        assert j.clients.zerotier.delete.called
