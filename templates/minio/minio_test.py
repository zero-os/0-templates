from unittest import TestCase
from unittest.mock import MagicMock, patch, call
import tempfile
import shutil
import os
import pytest

from minio import Minio, CONTAINER_TEMPLATE_UID, MINIO_FLIST
from zerorobot import config
from zerorobot.template_uid import TemplateUID
from zerorobot.template.state import StateCheckError


class TestMinioTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {
            'container': 'container_minio',
            'node': 'node',
            'listenPort': 9000,
            'namespace': 'namespace',
            'nsSecret': 'nsSecret',
            'login': 'login',
            'password': 'password',
            'zerodbs': ['192.24.121.42:9900'],
            'privateKey': '',
            'resticPassword': 'pass',
            'resticRepo': 'repo/',
            'resticRepoPassword': '',
            'resticUsername': 'username'
        }
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Minio.template_uid = TemplateUID.parse('github.com/zero-os/0-templates/%s/%s' % (Minio.template_name, Minio.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def setUp(self):
        patch('js9.j.clients.zero_os.sal', MagicMock()).start()

    def tearDown(self):
        patch.stopall()

    def test_create_invalid_data(self):
        """
        Test initializing minio service with
        """
        data = {}
        with pytest.raises(ValueError, message='template should fail to instantiate if data contains no node'):
            Minio(name="minio", data=data)

        data['node'] = 'node'
        with pytest.raises(ValueError, message='template should fail to instantiate if data contains no zerodbs'):
            Minio(name="minio", data=data)

        data['zerodbs'] = ['zerodb']
        with pytest.raises(ValueError, message='template should fail to instantiate if data contains no namespace'):
            Minio(name="minio", data=data)
        data['namespace'] = 'namespace'
        with pytest.raises(ValueError, message='template should fail to instantiate if data contains no login'):
            Minio(name="minio", data=data)
        data['login'] = 'login'
        with pytest.raises(ValueError, message='template should fail to instantiate if data contains no password'):
            Minio(name="minio", data=data)

    def test_create_valid_data(self):
        minio = Minio('minio', data=self.valid_data)
        assert minio.data == self.valid_data

    def test_node_sal(self):
        """
        Test node_sal property
        """
        node_get = patch('js9.j.clients.zero_os.sal.node_get', MagicMock(return_value='node_sal')).start()
        minio = Minio('minio', data=self.valid_data)

        assert minio.node_sal == 'node_sal'
        node_get.assert_called_once_with(minio.data['node'])

    def test_container_sal(self):
        node_get = patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
        minio = Minio('minio', data=self.valid_data)
        minio.node_sal.containers.get = MagicMock(return_value='container')

        assert minio.container_sal == 'container'
        minio.node_sal.containers.get.assert_called_once_with(minio.data['container'])

    def test_minio_sal(self):
        """
        Test node_sal property
        """
        minio_sal = patch('js9.j.clients.zero_os.sal.get_minio', MagicMock(return_value='minio_sal')).start()
        minio = Minio('minio', data=self.valid_data)
        minio._get_zdbs = MagicMock()

        assert minio.minio_sal == 'minio_sal'
        assert minio_sal.called

    def test_install(self):
        """
        Test install action
        """
        minio = Minio('minio', data=self.valid_data)
        minio.api.services.find_or_create = MagicMock()
        minio._get_zdbs = MagicMock()
        minio.install()

        assert minio.data['resticRepoPassword'] != ''
        container_data = {
            'flist': MINIO_FLIST,
            'node': self.valid_data['node'],
            'env':  [
                {'name': 'MINIO_ACCESS_KEY', 'value': 'login'}, {'name': 'MINIO_SECRET_KEY', 'value': 'password'},
                {'name': 'AWS_ACCESS_KEY_ID', 'value': 'username'}, {'name': 'AWS_SECRET_ACCESS_KEY', 'value': 'pass'}],
            'ports': ['9000:9000'],
            'nics': [{'type': 'default'}],
        }
        minio.api.services.find_or_create.assert_called_once_with(CONTAINER_TEMPLATE_UID, self.valid_data['container'], data=container_data)
        minio.state.check('actions', 'install', 'ok')

    def test_start(self):
        """
        Test start action
        """
        minio = Minio('minio', data=self.valid_data)
        minio.state.set('actions', 'install', 'ok')
        minio.api.services.get = MagicMock()
        minio._get_zdbs = MagicMock()
        minio.start()

        minio.api.services.get.assert_called_once_with(template_uid=CONTAINER_TEMPLATE_UID, name=self.valid_data['container'])
        minio.minio_sal.start.assert_called_once_with()
        minio.state.check('actions', 'start', 'ok')

    def test_start_before_install(self):
        """
        Test start action without installing
        """
        with pytest.raises(StateCheckError,
                           message='start action should raise an error if minio is not installed'):
            minio = Minio('minio', data=self.valid_data)
            minio.start()

    def test_stop(self):
        """
        Test stop action
        """
        minio = Minio('minio', data=self.valid_data)
        minio.state.set('actions', 'install', 'ok')
        minio.state.delete = MagicMock()
        minio._get_zdbs = MagicMock()
        minio.stop()

        minio.minio_sal.stop.assert_called_once_with()
        minio.state.delete.assert_called_once_with('actions', 'start')

    def test_stop_before_install(self):
        """
        Test stop action without install
        """
        with pytest.raises(StateCheckError,
                           message='stop action should raise an error if minio is not installed'):
            minio = Minio('minio', data=self.valid_data)
            minio.stop()

    def test_uninstall(self):
        """
        Test uninstall action
        """
        minio = Minio('minio', data=self.valid_data)
        minio.state.set('actions', 'install', 'ok')
        minio.state.delete = MagicMock()
        minio.stop = MagicMock()
        minio.api.services.get = MagicMock()

        minio.uninstall()

        minio.stop.assert_called_once_with()
        minio.state.delete.assert_called_once_with('actions', 'install')

    def test_uninstall_before_install(self):
        """
        Test uninstall action without install
        """
        with pytest.raises(StateCheckError,
                           message='uninstall action should raise an error if minio is not installed'):
            minio = Minio('minio', data=self.valid_data)
            minio.uninstall()