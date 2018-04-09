from unittest import TestCase
from unittest.mock import MagicMock, patch
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
        Minio.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (Minio.template_name, Minio.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def setUp(self):
        patch('js9.j.clients.zero_os.sal', MagicMock()).start()

    def tearDown(self):
        patch.stopall()

    def _test_create_minio_invalid(self, data, missing_key):
        with pytest.raises(
                ValueError, message='template should fail to instantiate if data contains no %s' % missing_key):
            minio = Minio(name="minio", data=data)
            minio.validate()

    def test_create_invalid_data(self):
        """
        Test initializing minio service with
        """
        data = {}
        keys = {
            '': 'node',
            'node': 'zerodbs',
            'zerodbs': 'namespace',
            'namespace': 'login',
            'login': 'password',
        }
        for key, missing_key in keys.items():
            data[key] = key
            self._test_create_minio_invalid(data, missing_key)

    def test_create_valid_data(self):
        minio = Minio('minio', data=self.valid_data)
        minio.validate()
        assert minio.data == self.valid_data

    def test_node_sal(self):
        """
        Test node_sal property
        """
        get_node = patch('js9.j.clients.zero_os.sal.get_node', MagicMock(return_value='node_sal')).start()
        minio = Minio('minio', data=self.valid_data)

        assert minio.node_sal == 'node_sal'
        get_node.assert_called_once_with(minio.data['node'])

    def test_container_sal(self):
        patch('js9.j.clients.zero_os.sal.get_node', MagicMock()).start()
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
        minio.api.services.find_or_create.assert_called_once_with(
            CONTAINER_TEMPLATE_UID, self.valid_data['container'], data=container_data)
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

        minio.api.services.get.assert_called_once_with(
            template_uid=CONTAINER_TEMPLATE_UID, name=self.valid_data['container'])
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
