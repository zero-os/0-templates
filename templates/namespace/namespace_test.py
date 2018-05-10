from unittest import TestCase
from unittest.mock import MagicMock
import tempfile
import shutil
import os
import pytest

from namespace import Namespace
from zerorobot import config
from zerorobot.template_uid import TemplateUID
from zerorobot.template.state import StateCheckError


class TestNamespaceTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {
            'size': 10,
            'password': 'user',
            'zerodb': 'zerodb'
        }
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Namespace.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (Namespace.template_name, Namespace.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def test_invalid_data(self):
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the zerodb'):
            ns = Namespace(name='namespace', data={})
            ns.validate()

        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the size'):
            ns = Namespace(name='namespace', data={'zerodb': 'zerodb'})
            ns.validate()

    def test_valid_data(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.validate()
        assert ns.data == self.valid_data

    def test_zerodb_property(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.api.services.get = MagicMock(return_value='zerodb')
        assert ns._zerodb == 'zerodb'

    def test_install(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.api = MagicMock()
        args = {
            'name': ns.name,
            'size': ns.data['size'],
            'password': ns.data['password'],
        }
        ns.install()
        ns._zerodb.schedule_action.assert_called_once_with('namespace_create', args=args)
        ns.state.check('actions', 'install', 'ok')

    def test_info_without_install(self):
        with pytest.raises(StateCheckError, message='Executing info action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.info()

    def test_info(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        task = MagicMock(result='info')
        ns._zerodb.schedule_action = MagicMock(return_value=task)

        assert ns.info() == 'info'
        ns._zerodb.schedule_action.assert_called_once_with('namespace_info', args={'name': ns.name})

    def test_uninstall_without_install(self):
        with pytest.raises(StateCheckError, message='Executing uninstall action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.uninstall()

    def test_uninstall(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        ns.uninstall()
        ns._zerodb.schedule_action.assert_called_once_with('namespace_delete', args={'name': ns.name})

    def test_connection_info_without_install(self):
        with pytest.raises(StateCheckError, message='Executing connection_info action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.connection_info()

    def test_connection_info(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        result = {'ip': '127.0.0.1', 'port': 9900}
        task = MagicMock(result=result)
        ns._zerodb.schedule_action = MagicMock(return_value=task)
        assert ns.connection_info() == result
        ns._zerodb.schedule_action.assert_called_once_with('connection_info')

    def test_url_without_install(self):
        with pytest.raises(StateCheckError, message='Executing info action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.url()

    def test_url(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        task = MagicMock(result='url')
        ns._zerodb.schedule_action = MagicMock(return_value=task)

        assert ns.url() == 'url'
        ns._zerodb.schedule_action.assert_called_once_with('namespace_url', args={'name': ns.name})

    def test_private_url_without_install(self):
        with pytest.raises(StateCheckError, message='Executing info action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.url()

    def test_private_url(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        task = MagicMock(result='url')
        ns._zerodb.schedule_action = MagicMock(return_value=task)

        assert ns.private_url() == 'url'
        ns._zerodb.schedule_action.assert_called_once_with('namespace_private_url', args={'name': ns.name})
