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
from zerorobot.service_collection import ServiceNotFoundError


def _task_mock(result):
    task = MagicMock()
    task.wait = MagicMock(return_value=task)
    task.result = result
    return task


class TestNamespaceTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {
            'disktype': 'HDD',
            'mode': 'user',
            'password': 'mypasswd',
            'public': False,
            'size': 20,
        }
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Namespace.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (Namespace.template_name, Namespace.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def test_invalid_data(self):
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the size'):
            data = self.valid_data.copy()
            data.pop('size')
            ns = Namespace(name='namespace', data=data)
            ns.api.services.get = MagicMock()
            ns.validate()

    def test_no_node_installed(self):
        with pytest.raises(RuntimeError, message='template should fail to install if no service node is installed'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.api.services.get = MagicMock(side_effect=ServiceNotFoundError)
            ns.validate()

        with pytest.raises(RuntimeError, message='template should fail to install if no service node is installed'):
            ns = Namespace(name='namespace', data=self.valid_data)
            node = MagicMock()
            node.state.check = MagicMock(side_effect=StateCheckError)
            ns.api.services.get = MagicMock(return_value=node)
            ns.validate()

    def test_valid_data(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.api.services.get = MagicMock()
        ns.validate()
        data = self.valid_data.copy()
        data['zerodb'] = ''
        assert ns.data == data

    def test_zerodb_property(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.api.services.get = MagicMock(return_value='zerodb')
        assert ns._zerodb == 'zerodb'

    def test_install(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        node = MagicMock()
        node.schedule_action = MagicMock(return_value=_task_mock(('instance', 'ns_name')))
        ns.api = MagicMock()
        ns.api.services.get = MagicMock(return_value=node)
        ns.install()
        node.schedule_action.assert_called_once_with('create_zdb_namespace', self.valid_data)
        ns.state.check('actions', 'install', 'ok')
        assert ns.data['ns_name'] == 'ns_name'
        assert ns.data['zerodb'] == 'instance'

    def test_info_without_install(self):
        with pytest.raises(StateCheckError, message='Executing info action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.info()

    def test_info(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.data['ns_name'] = 'ns_name'
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        task = _task_mock('info')
        ns._zerodb.schedule_action = MagicMock(return_value=task)

        assert ns.info() == 'info'
        ns._zerodb.schedule_action.assert_called_once_with('namespace_info', args={'name': ns.data['ns_name']})

    def test_uninstall_without_install(self):
        with pytest.raises(StateCheckError, message='Executing uninstall action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.uninstall()

    def test_uninstall(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.data['ns_name'] = 'ns_name'
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        ns.uninstall()
        ns._zerodb.schedule_action.assert_called_once_with('namespace_delete', args={'name': 'ns_name'})

    def test_connection_info_without_install(self):
        with pytest.raises(StateCheckError, message='Executing connection_info action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.connection_info()

    def test_connection_info(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.state.set('actions', 'install', 'ok')
        ns.state.set('status', 'running', 'ok')
        ns.api = MagicMock()
        result = {'ip': '127.0.0.1', 'port': 9900}
        task = _task_mock(result)
        ns._zerodb.schedule_action = MagicMock(return_value=task)
        assert ns.connection_info() == result
        ns._zerodb.schedule_action.assert_called_once_with('connection_info')

    def test_url_without_install(self):
        with pytest.raises(StateCheckError, message='Executing info action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.url()

    def test_url(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.data['ns_name'] = 'ns_name'
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        ns._zerodb.schedule_action = MagicMock(return_value=_task_mock('url'))

        assert ns.url() == 'url'
        ns._zerodb.schedule_action.assert_called_once_with('namespace_url', args={'name': 'ns_name'})

    def test_private_url_without_install(self):
        with pytest.raises(StateCheckError, message='Executing info action without install should raise an error'):
            ns = Namespace(name='namespace', data=self.valid_data)
            ns.url()

    def test_private_url(self):
        ns = Namespace(name='namespace', data=self.valid_data)
        ns.data['ns_name'] = 'ns_name'
        ns.state.set('actions', 'install', 'ok')
        ns.api = MagicMock()
        ns._zerodb.schedule_action = MagicMock(return_value=_task_mock('url'))

        assert ns.private_url() == 'url'
        ns._zerodb.schedule_action.assert_called_once_with('namespace_private_url', args={'name': 'ns_name'})
