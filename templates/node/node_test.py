from unittest import TestCase
from unittest.mock import MagicMock, patch, call
import tempfile
import shutil
import os

import pytest

from js9 import j
from node import Node, _update_healthcheck_state, _update
from zerorobot import service_collection as scol
from zerorobot import config
from zerorobot.template_uid import TemplateUID


class TestNodeTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        patch('gevent.sleep', MagicMock()).start()
        cls.valid_data = {'redisAddr': 'localhost'}
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Node.template_uid = TemplateUID.parse('github.com/zero-os/0-templates/%s/%s' % (Node.template_name, Node.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def tearDown(self):
        patch.stopall()

    def test_create_invalid_data(self):
        """
        Test Node creation with invalid data
        """
        with pytest.raises(ValueError,
                           message='template should fail to instantiate if data dict is missing the redisAddr'):
            Node(name='node')

    def test_create_with_valid_data_no_password(self):
        """
        Test create node service and password is not refreshed
        """
        with patch('js9.j.clients', MagicMock()) as client_get:
            client_get.start()
            node = Node(name='node', data=self.valid_data)
            data = {
                'host': node.data['redisAddr'],
                'port': node.data['redisPort'],
                'password_': node.data['redisPassword'],
                'ssl': True,
                'db': 0,
                'timeout': 120,
            }
            client_get.zero_os.get.assert_called_with(instance=node.name, data=data, create=True, die=True)
            client_get.itsyouonline.refresh_jwt_token.assert_not_called()

    def test_refresh_password(self):
        """
        Test refresh password when password is set
        """
        with patch('js9.j.clients', MagicMock()) as client_get:
            Node(name='node', data={'redisAddr': 'localhost', 'redisPassword': 'token'})
            client_get.itsyouonline.refresh_jwt_token.assert_called_with('token', validity=3600)

    def test_update_data(self):
        """
        test update_data with new data
        """
        node = Node(name='node', data=self.valid_data)
        node._ensure_client_config = MagicMock()
        node.update_data({'redisAddr': '127.0.0.1'})
        node._ensure_client_config.assert_called_once_with()

    def test_update_data_same_data(self):
        """
        Test update_data with same data
        """
        node = Node(name='node', data=self.valid_data)
        node._ensure_client_config = MagicMock()
        node.update_data(node.data)
        node._ensure_client_config.assert_not_called()

    def test_node_sal(self):
        """
        Test node_sal property
        """
        with patch('js9.j.clients.zero_os.sal.node_get', MagicMock()) as node_get:
            node = Node(name='node', data=self.valid_data)
            node.node_sal
            node_get.assert_called_once_with(node.name)

    def test_install(self):
        """
        Test node install
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        node = Node(name='node', data=self.valid_data)
        node.node_sal.client.info.version = MagicMock(return_value={'branch': 'master', 'revision': 'revision'})
        node.install()

        node.state.check('actions', 'install', 'ok')

    def test_node_info(self):
        """
        Test node info
        """
        with patch('js9.j.clients.zero_os.sal.node_get', MagicMock()):
            node = Node(name='node', data=self.valid_data)
            node.info()

            node.node_sal.client.info.os.assert_called_once_with()

    def test_node_stats(self):
        """
        Test node stats
        """
        with patch('js9.j.clients.zero_os.sal.node_get', MagicMock()):
            node = Node(name='node', data=self.valid_data)
            node.stats()
            node.node_sal.client.aggregator.query.assert_called_once_with()

    def test_start_all_containers(self):
        """
        Test node _start_all_containers
        """
        node = Node(name='node', data=self.valid_data)
        container = MagicMock()
        node.api.services.find = MagicMock(return_value=[container])
        node._start_all_containers()

        container.schedule_action.assert_called_once_with('start', args={'node_name': 'node'})

    def test_stop_all_containers(self):
        """
        Test node _stop_all_containers
        """
        node = Node(name='node', data=self.valid_data)
        container = MagicMock()
        node.api.services.find = MagicMock(return_value=[container])
        node._wait_all = MagicMock()
        node._stop_all_containers()

        container.schedule_action.assert_called_once_with('stop', args={'node_name': 'node'})
        assert node._wait_all.called

    def test_wait_all(self):
        """
        Test node _wait_all
        """
        node = Node(name='node', data=self.valid_data)
        task = MagicMock()
        node._wait_all([task])

        task.wait.assert_called_once_with(60)

    def test_healthcheck_node_running(self):
        """
        Test node healthcheck if node is running
        """
        with patch('node._update_healthcheck_state', MagicMock()) as healthcheck:
            patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
            node = Node(name='node', data=self.valid_data)
            node.node_sal.is_running = MagicMock(return_value=True)
            node._healthcheck()

            assert healthcheck.call_count == 13

    def test_healthcheck_node_not_running(self):
        """
        Test node healthcheck if node is not running
        """
        with patch('node._update_healthcheck_state', MagicMock()) as healthcheck:
            patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
            node = Node(name='node', data=self.valid_data)
            node.node_sal.is_running = MagicMock(return_value=False)
            node._healthcheck()

            healthcheck.assert_not_called()

    def test_uninstall(self):
        """
        Test node uninstall
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        node = Node(name='node', data=self.valid_data)
        node._stop_all_vms = MagicMock()
        node._stop_all_containers = MagicMock()
        bootstrap = MagicMock()
        node.api.services.find = MagicMock(return_value=[bootstrap])
        node.uninstall()

        node._stop_all_containers.assert_called_once_with()
        node._stop_all_vms.assert_called_once_with()
        bootstrap.schedule_action.assert_called_once_with('delete_node', args={'redis_addr': 'localhost'})

    def test_reboot(self):
        """
        Test node reboot with node reachable after reboot
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        node = Node(name='node', data=self.valid_data)
        node._stop_all_vms = MagicMock()
        node._stop_all_containers = MagicMock()
        node._start_all_vms = MagicMock()
        node._start_all_containers = MagicMock()
        node.recurring_action = MagicMock()
        node.node_sal.client.ping = MagicMock(side_effect=[RuntimeError, True])
        node.reboot()

        node._stop_all_vms.assert_called_once_with()
        node._stop_all_containers.assert_called_once_with()
        node._start_all_vms.assert_called_once_with()
        node._start_all_containers.assert_called_once_with()
        node.recurring_action.assert_called_once_with('_healthcheck', 60)

    def test_reboot_node_not_reachable(self):
        """
        Test node reboot with node not reachable after reboot
        """
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        node = Node(name='node', data=self.valid_data)
        node._stop_all_vms = MagicMock()
        node._stop_all_containers = MagicMock()
        node._start_all_vms = MagicMock()
        node._start_all_containers = MagicMock()
        node.recurring_action = MagicMock()
        node.node_sal.client.ping = MagicMock(side_effect=RuntimeError)
        node.reboot()

        node._stop_all_vms.assert_called_once_with()
        node._stop_all_containers.assert_called_once_with()
        node._start_all_vms.assert_not_called()
        node._start_all_containers.assert_not_called()
        node.recurring_action.assert_called_once_with('_healthcheck', 60)

    def test_update_healthcheck_state_list(self):
        """
        Test called with list
        """
        update = patch('node._update', MagicMock()).start()
        healthcheck = MagicMock()
        _update_healthcheck_state(MagicMock(), [healthcheck, healthcheck])
        assert update.call_count == 2

    def test_update_healthcheck_state(self):
        """
        Test called with one healthcheck
        """
        update = patch('node._update', MagicMock()).start()
        healthcheck = MagicMock()
        _update_healthcheck_state(MagicMock(), healthcheck)
        assert update.call_count == 1

    def test_update_warning(self):
        """
        Test called with invalid message
        """
        healthcheck = {'messages': [], 'category': 'category', 'id': 'id'}
        service = MagicMock()
        _update(service, healthcheck)
        assert service.logger.warning.called

    def test_update_one_message(self):
        """
        Test called with one message
        """
        healthcheck = {'messages': [{'status': 'status'}], 'category': 'category', 'id': 'id'}
        service = MagicMock()
        _update(service, healthcheck)
        service.state.set.assert_called_once_with('category', 'id', 'status')

    def test_update_multiple_messages(self):
        """
        Test called with one message
        """
        healthcheck = {
            'messages': [{'status': 'status', 'id': 1},
                         {'status': 'status', 'id': 2}],
            'category': 'category',
            'id': 'id'
        }
        service = MagicMock()
        _update(service, healthcheck)
        service.state.set.assert_has_calls([call('category', 'id-1', 'status'), call('category', 'id-2', 'status')])
