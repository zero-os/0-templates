from unittest import TestCase
from unittest.mock import MagicMock

import pytest
from js9 import j

from zerotier_client import ZerotierClient


class TestZerotierClientTemplate(TestCase):

    def test_create_data_none(self):
        j.clients.zerotier.list = MagicMock(return_value=[])

        ZerotierClient.template_dir = '/tmp'
        with pytest.raises(RuntimeError, message='template should fail to instanciate if data is None'):
            service = ZerotierClient(name="zttest", data=None)

    def test_create_data_no_token(self):
        j.clients.zerotier.list = MagicMock(return_value=[])

        ZerotierClient.template_dir = '/tmp'
        with pytest.raises(RuntimeError, message="template should fail to instanciate if data doesn't contain 'token'"):
            service = ZerotierClient(name="zttest", data={'foo': 'bar'})

        with pytest.raises(RuntimeError, message="template should fail to instanciate if data doesn't contain 'token'"):
            service = ZerotierClient(name="zttest", data={'token': ''})

    def test_create(self):
        j.clients.zerotier.list = MagicMock(return_value=[])
        j.clients.zerotier.get = MagicMock()

        ZerotierClient.template_dir = '/tmp'
        data = {'token': 'foo'}
        service = ZerotierClient(name="zttest", data={'token': 'foo'})
        j.clients.zerotier.list.assert_called_with()
        j.clients.zerotier.get.assert_called_with("zttest", data={'token_': data['token']})

    def test_create_already_exists(self):
        j.clients.zerotier.list = MagicMock(return_value=['zttest'])
        j.clients.zerotier.get = MagicMock()

        ZerotierClient.template_dir = '/tmp'
        data = {'token': 'foo'}
        service = ZerotierClient(name="zttest", data={'token': 'foo'})
        assert j.clients.zerotier.get.called is False

    def test_delete(self):
        j.clients.zerotier.delete = MagicMock()

        ZerotierClient.template_dir = '/tmp'
        service = ZerotierClient(name="zttest", data={'token': 'foo'})
        service.delete()
        assert j.clients.zerotier.delete.called
