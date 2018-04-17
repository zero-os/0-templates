from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os

import pytest

from node import Node, NODE_CLIENT
from zerorobot import config
from zerorobot.template_uid import TemplateUID
from zerorobot.template.state import StateCheckError


def mockdecorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


patch("zerorobot.template.decorator.timeout", MagicMock(return_value=mockdecorator)).start()
patch("zerorobot.template.decorator.retry", MagicMock(return_value=mockdecorator)).start()
patch("gevent.sleep", MagicMock()).start()


class TestNodeTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Node.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (Node.template_name, Node.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def setUp(self):
        self.client_get = patch('js9.j.clients', MagicMock()).start()

    def tearDown(self):
        patch.stopall()

    def test_node_sal(self):
        """
        Test node_sal property
        """
        get_node = patch('js9.j.clients.zero_os.sal.get_node', MagicMock(return_value='node_sal')).start()
        node = Node(name='node')
        node_sal = node.node_sal
        get_node.assert_called_with(NODE_CLIENT)
        assert node_sal == 'node_sal'

    def test_install(self):
        """
        Test node install
        """
        node = Node(name='node')
        node.node_sal.client.info.version = MagicMock(return_value={'branch': 'master', 'revision': 'revision'})
        node.install()

        node.state.check('actions', 'install', 'ok')

    def test_node_info_node_running(self):
        """
        Test node info
        """
        node = Node(name='node')
        node.state.set('status', 'running', 'ok')
        node.info()

        node.node_sal.client.info.os.assert_called_once_with()

    def test_node_stats_node_running(self):
        """
        Test node stats
        """
        node = Node(name='node')
        node.state.set('status', 'running', 'ok')
        node.stats()
        node.node_sal.client.aggregator.query.assert_called_once_with()

    def test_start_all_containers(self):
        """
        Test node _start_all_containers
        """
        node = Node(name='node')
        container = MagicMock()
        node.api.services.find = MagicMock(return_value=[container])
        node._start_all_containers()

        container.schedule_action.assert_called_once_with('start')

    def test_stop_all_containers(self):
        """
        Test node _stop_all_containers
        """
        node = Node(name='node')
        container = MagicMock()
        node.api.services.find = MagicMock(return_value=[container])
        node._wait_all = MagicMock()
        node._stop_all_containers()

        container.schedule_action.assert_called_once_with('stop')
        assert node._wait_all.called

    def test_wait_all(self):
        """
        Test node _wait_all
        """
        node = Node(name='node')
        task = MagicMock()
        node._wait_all([task])

        task.wait.assert_called_with(timeout=60, die=False)

        node._wait_all([task], timeout=30, die=True)
        task.wait.assert_called_with(timeout=30, die=True)

    def test_reboot_node(self):
        """
        Test node reboot if node already running
        """
        node = Node(name='node')
        node.node_sal.client.raw = MagicMock()
        node.reboot()

        node.node_sal.client.raw.assert_called_with('core.reboot', {})

    def test_monitor_node_reboot(self):
        """
        Test _monitor action called after node rebooted
        """
        node = Node(name='node', data={'uptime': 40.0})
        node.install = MagicMock()
        node._start_all_containers = MagicMock()
        node._start_all_vms = MagicMock()
        node.state.set('actions', 'install', 'ok')
        node.state.set('status', 'rebooting', 'ok')
        node.node_sal.is_running = MagicMock(return_value=True)
        node.node_sal.uptime = MagicMock(return_value=10.0)
        node._monitor()

        node._start_all_containers.assert_called_once_with()
        node._start_all_vms.assert_called_once_with()
        node.install.assert_called_once_with()

        with pytest.raises(StateCheckError,
                           message='template should remove the rebooting status after monitoring'):
            node.state.check('status', 'rebooting', 'ok')

    def test_monitor_node(self):
        """
        Test _monitor action without reboot
        """
        node = Node(name='node')
        node.install = MagicMock()
        node._start_all_containers = MagicMock()
        node._start_all_vms = MagicMock()
        node.state.set('actions', 'install', 'ok')
        node.node_sal.is_running = MagicMock(return_value=True)
        node.node_sal.uptime = MagicMock(return_value=40.0)
        node._monitor()

        assert not node._start_all_containers.called
        assert not node._start_all_vms.called
        assert not node.install.called

    def test_os_version(self):
        """
        Test os_version action when node is running
        """
        node = Node(name='node')
        node.state.set('status', 'running', 'ok')
        node.node_sal.client.ping = MagicMock(
            return_value='PONG Version: main @Revision: 41f7eb2e94f6fc9a447f9dec83c67de23537f119')
        node.os_version() == 'main @Revision: 41f7eb2e94f6fc9a447f9dec83c67de23537f119'
