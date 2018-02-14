from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os

import pytest

from js9 import j
from container import Container
from zerorobot.template.state import StateCheckError
from zerorobot import service_collection as scol
from zerorobot import config
from zerorobot.template_uid import TemplateUID


class TestContainerTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {'flist': 'flist', 'node': 'node', 'ports': ['80:80']}
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Container.template_uid = TemplateUID.parse('github.com/zero-os/0-templates/%s/%s' % (Container.template_name, Container.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def tearDown(self):
        patch.stopall()

    def test_create_invalid_data(self):
        """
        Test Container creation with invalid data
        """
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the node'):
            Container(name='container', data={'flist': 'flist'})

        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the flist'):
            Container(name='container', data={'node': 'node'})

    def test_create_valid_data(self):
        Container(name='container', data=self.valid_data)

    def test_node_sal_node_is_none(self):
        """
        Test the node_sal property when Container._node is None
        """
        container = Container('container', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.node_get',  MagicMock(return_value=node_sal_return)).start()
        node_sal = container.node_sal

        assert node_sal == node_sal_return
        j.clients.zero_os.sal.node_get.assert_called_with(self.valid_data['node'])

    def test_node_sal_node_is_set(self):
        """
        Test the node_sal property when Container._node is set
        """
        container = Container('container', data=self.valid_data)
        node_sal_return = 'node_sal'
        patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        container._node = node_sal_return
        node_sal = container.node_sal

        assert node_sal == node_sal_return
        assert j.clients.zero_os.sal.node_get.called is False

    def test_container_sal_container_installed(self):
        """
        Test container_sal property when container is exists
        """
        container = Container('container', data=self.valid_data)
        container_sal_return = 'container_sal'
        container.node_sal.containers.get = MagicMock(return_value=container_sal_return)
        container.install = MagicMock()
        container_sal = container.container_sal

        container.node_sal.containers.get.assert_called_once_with(container.name)
        assert container_sal == container_sal_return
        assert container.install.called is False

    def test_container_sal_container_not_installed(self):
        """
        Test container_sal property when container doesn't exist
        """
        container_sal_return = 'container_sal'
        container = Container('container', data=self.valid_data)
        container.node_sal.containers.get = MagicMock(side_effect=[LookupError, container_sal_return])

        container.install = MagicMock()
        container_sal = container.container_sal

        assert container_sal == container_sal_return
        assert container.install.called
        assert container.node_sal.containers.get.call_count == 2

    def test_install_container_no_node_connection(self):
        """
        Test installing a container with no connection to the node
        """
        with pytest.raises(RuntimeError,
                           message='install action should raise an error if there is no connection to the node'):
            container = Container('container', data=self.valid_data)
            container.api.services.get = MagicMock()
            patch('js9.j.clients.zero_os.sal.node_get', MagicMock(return_value=None)).start()
            container.install()

    def test_install_container_node_not_found(self):
        """
        Test installing a container with no service found for the node
        """
        with pytest.raises(scol.ServiceNotFoundError,
                           message='install action should raise an error if there is no connection to the node'):
            container = Container('container', data=self.valid_data)
            container.api.services.get = MagicMock(side_effect=scol.ServiceNotFoundError())
            container.install()

    def test_install_container_node_not_installed(self):
        """
        Test installing the container without the node being installed
        """
        with pytest.raises(StateCheckError,
                           message='install action should raise an error if there is no connection to the node'):
            container = Container('container', data=self.valid_data)
            node = MagicMock()
            container.api.services.get = MagicMock(return_value=node)
            node.state.check = MagicMock(side_effect=StateCheckError)
            container.install()

    def test_install_container_success(self):
        """
        Test successfully installing a container
        """
        container = Container('container', data=self.valid_data)
        container.api.services.get = MagicMock()
        container.node_sal.containers.create = MagicMock()

        container.install()

        container.state.check('actions', 'start', 'ok')
        container.state.check('actions', 'start', 'ok')
        assert container.node_sal.containers.create.called
        assert container.api.services.get.called

    def test_start_container_wrong_node(self):
        """
        Test starting a container that belongs to another node
        """
        container = Container('container', data=self.valid_data)
        container.state.check = MagicMock()
        container.start(node_name='node2')

        assert container.state.check.called is False

    def test_start_container_before_install(self):
        """
        Test starting a container without installing first
        """
        with pytest.raises(StateCheckError, message='Starting container before install should raise an error'):
            container = Container('container', data=self.valid_data)
            container.start()

    def test_start_container_after_install(self):
        """
        Test successfully starting a container
        """
        container = Container('container', data=self.valid_data)
        container.state.set('actions', 'install', 'ok')
        container.node_sal.containers = MagicMock()
        container.container_sal.start = MagicMock()
        container.start()

        assert container.state.check('actions', 'start', 'ok')

    def test_stop_container_wrong_node(self):
        """
        Test stopping a container that belongs to another node
        """
        container = Container('container', data=self.valid_data)
        container.state.check = MagicMock()
        container.stop(node_name='node2')

        assert container.state.check.called is False

    def test_stop_container_before_start(self):
        """
        Test stopping a container without starting
        """
        with pytest.raises(StateCheckError, message='Starting container before install should raise an error'):
            container = Container('container', data=self.valid_data)
            container.stop()

    def test_stop_container_after_start(self):
        """
        Test successfully stopping a container
        """
        container = Container('container', data=self.valid_data)
        container.state.check = MagicMock(return_value=True)
        container.node_sal.containers = MagicMock()
        container.container_sal.stop = MagicMock()

        assert container.state.check('actions', 'start', 'ok')
