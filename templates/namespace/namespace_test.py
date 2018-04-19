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
            'secret': 'user',
            'zerodb': 'zerodb',
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
            'secret': ns.data['secret'],
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
