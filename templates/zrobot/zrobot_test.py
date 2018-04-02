from unittest import TestCase
from unittest.mock import MagicMock, patch
from js9 import j
import tempfile
import shutil
import os
import pytest

from zrobot import Zrobot
from zerorobot.template.state import StateCheckError
from zerorobot import service_collection as scol
from zerorobot import config
from zerorobot.template_uid import TemplateUID


class TestZrobotTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {
            'node': 'node',
            'templates': [],
            'organization': 'dfsfd',
            'nics': []
        }
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Zrobot.template_uid = TemplateUID.parse('github.com/zero-os/0-templates/%s/%s' % (Zrobot.template_name, Zrobot.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def setUp(self):
        mock = MagicMock()
        patch('js9.j.clients.zero_os.sal.get_node', mock).start()

    def tearDown(self):
        patch.stopall()

    def test_invalid_data(self):
        """
        Test creating a zrobot with invalid data
        """
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the node'):
            zrobot = Zrobot(name='zrobot', data={})
            zrobot.validate()

    def test_valid_data(self):
        """
        Test creating a zrobot service with valid data
        """
        zrobot = Zrobot('zrobot', data=self.valid_data)
        zrobot.api.services.get = MagicMock()
        zrobot.validate()
        assert zrobot.data == self.valid_data

    def test_node_sal(self):
        """
        Test the node_sal property
        """
        zrobot = Zrobot('zrobot', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.get_node',  MagicMock(return_value=node_sal_return)).start()
        node_sal = zrobot.node_sal

        assert node_sal == node_sal_return
        j.clients.zero_os.sal.get_node.assert_called_with(self.valid_data['node'])

    def test_install_zrobot_node_not_found(self):
        """
        Test installing a zrobot with no service found for the node
        """
        with pytest.raises(scol.ServiceNotFoundError,
                           message='install action should raise an error if node service is not found'):
            zrobot = Zrobot('zrobot', data=self.valid_data)
            zrobot.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            zrobot.validate()

    def test_install(self):
        """
        Test successfully creating zrobot
        """
        zrobot = Zrobot('zrobot', data=self.valid_data)
        container = MagicMock()
        zrobot._get_container = MagicMock(return_value=container)
        patch('js9.j.clients.zero_os.sal.get_node',  MagicMock()).start()
        zrobot.install()
        zrobot.state.check('actions', 'install', 'ok')
        zrobot.state.check('actions', 'start', 'ok')
        container.schedule_action.assert_called_once_with('install')

    def test_start(self):
        zrobot = Zrobot('zrobot', data=self.valid_data)
        container = MagicMock()
        zrobot._get_container = MagicMock(return_value=container)
        patch('js9.j.clients.zero_os.sal.get_node',  MagicMock()).start()
        zrobot.start()
        zrobot.state.check('actions', 'start', 'ok')
        container.schedule_action.assert_called_once_with('start')

    def test_stop_before_starting(self):
        """
        Test stopping without starting
        """
        with pytest.raises(StateCheckError, message='Stop before start should raise an error'):
            zrobot = Zrobot('zrobot', data=self.valid_data)
            zrobot.stop()

    def test_stop(self):
        zrobot = Zrobot('zrobot', data=self.valid_data)
        zrobot.api.services.get = MagicMock()
        zrobot._get_zrobot_client = MagicMock()
        zrobot.state.set('actions', 'start', 'ok')
        zrobot.state.delete = MagicMock(return_value=True)
        zrobot.stop()
        zrobot.state.delete.assert_called_with('status', 'running')

    def test_uninstall_before_install(self):
        """
        Test uninstall without installing
        """
        with pytest.raises(StateCheckError, message='Uninstall before install should raise an error'):
            zrobot = Zrobot('zrobot', data=self.valid_data)
            zrobot.uninstall()

    def test_uninstall(self):
        zrobot = Zrobot('zrobot', data=self.valid_data)
        container = MagicMock()
        zrobot.api.services.get = MagicMock(return_value=container)
        zrobot._get_zrobot_client = MagicMock()
        zrobot.state.set('actions', 'install', 'ok')
        zrobot.state.delete = MagicMock(return_value=True)
        zrobot.uninstall()
        zrobot.state.delete.assert_called_with('status', 'running')
        container.schedule_action.assert_called_once_with('uninstall')
        container.delete.assert_called_once_with()