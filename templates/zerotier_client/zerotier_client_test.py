from unittest import TestCase

import pytest

from js9 import j
from zerotier_client import ZerotierClient


class TestZerotierClientTemplate(TestCase):

    def setUp(self):
        j.clients.zerotier.reset()

    def test_create_data_none(self):
        ZerotierClient.template_dir = '/tmp'
        with pytest.raises(RuntimeError, message='template should fail to instanciate if data is None'):
            service = ZerotierClient(name="zttest", data=None)

    def test_create_data_no_token(self):
        ZerotierClient.template_dir = '/tmp'
        with pytest.raises(RuntimeError, message="template should fail to instanciate if data doesn't contain 'token'"):
            service = ZerotierClient(name="zttest", data={'foo': 'bar'})

        with pytest.raises(RuntimeError, message="template should fail to instanciate if data doesn't contain 'token'"):
            service = ZerotierClient(name="zttest", data={'token': ''})

    def test_create(self):
        ZerotierClient.template_dir = '/tmp'
        service = ZerotierClient(name="zttest", data={'token': 'foo'})
        assert 'zttest'in j.clients.zerotier.list()

    def test_create_already_exists(self):
        ZerotierClient.template_dir = '/tmp'
        service = ZerotierClient(name="zttest", data={'token': 'foo'})
        assert 'zttest'in j.clients.zerotier.list()

        service = ZerotierClient(name="zttest", data={'token': 'foo'})

    def test_delete(self):
        ZerotierClient.template_dir = '/tmp'
        service = ZerotierClient(name="zttest", data={'token': 'foo'})
        assert 'zttest'in j.clients.zerotier.list()
        service.delete()
        assert 'zttest' not in j.clients.zerotier.list()
