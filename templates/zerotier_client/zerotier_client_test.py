from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os

import pytest

from zerotier_client import ZerotierClient
from zerorobot import config
from zerorobot.template_uid import TemplateUID


class TestZerotierClientTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        ZerotierClient.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (ZerotierClient.template_name, ZerotierClient.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def setUp(self):
        self.list = patch('js9.j.clients.zerotier.list', MagicMock(return_value=[])).start()
        self.get = patch('js9.j.clients.zerotier.get', MagicMock()).start()

    def tearDown(self):
        patch.stopall()

    def test_create_data_none(self):
        with pytest.raises(ValueError, message='template should fail to instantiate if data is None'):
            ZerotierClient(name="zttest", data=None)

    def test_create_data_no_token(self):
        with pytest.raises(ValueError, message="template should fail to instantiate if data doesn't contain 'token'"):
            ZerotierClient(name="zttest", data={'foo': 'bar'})

        with pytest.raises(ValueError, message="template should fail to instantiate if data doesn't contain 'token'"):
            ZerotierClient(name="zttest", data={'token': ''})

    def test_create(self):
        get = patch('js9.j.clients.zerotier.get', MagicMock()).start()
        data = {'token': 'foo'}
        ZerotierClient(name="zttest", data=data)

        self.list.assert_called_with()
        get.assert_called_with("zttest", data={'token_': data['token']})

    def test_create_already_exists(self):
        patch('js9.j.clients.zerotier.list', MagicMock(return_value=['zttest'])).start()
        ZerotierClient(name='zttest', data={'token': 'foo'})

        assert self.get.called is False

    def test_delete(self):
        delete = patch('js9.j.clients.zerotier.delete', MagicMock()).start()
        service = ZerotierClient(name='zttest', data={'token': 'foo'})
        service.delete()

        delete.assert_called_once_with('zttest')
