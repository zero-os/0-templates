from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os

import pytest

from js9 import j
from zerodb import Zerodb
from zerorobot import config
from zerorobot.template_uid import TemplateUID


class TestZerodbTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {
            'container': 'container',
            'node': 'node',
            'dataDir': '/mnt/data',
            'indexDir': '/mnt/index',
            'listenAddr': '0.0.0.0',
            'listenPort': 9900,
            'mode': 'user',
            'sync': False
        }
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        Zerodb.template_uid = TemplateUID.parse('github.com/zero-os/0-templates/%s/%s' % (Zerodb.template_name, Zerodb.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def test_create_invalid_data(self):
        """
        Test initializing zerodb service with
        :return:
        """
        with pytest.raises(ValueError, message='template should fail to instantiate if data contains no container'):
            Zerodb(name="zdb", data=None)

    def test_create_valid_data(self):
        zdb = Zerodb('zdb', data=self.valid_data)
        assert zdb.data == self.valid_data

    def test_node_sal(self):
        """
        Test node_sal property
        """
        with patch('js9.j.clients.zero_os.sal.node_get', MagicMock(return_value='node_sal')) as node_get:
            zdb = Zerodb('zdb', data=self.valid_data)
            assert zdb.node_sal == 'node_sal'
            node_get.assert_called_once_with(zdb.data['node'])

    def test_container_sal(self):
        with patch('js9.j.clients.zero_os.sal.node_get', MagicMock()) as node_get:
            zdb = Zerodb('zdb', data=self.valid_data)
            zdb.node_sal.containers.get = MagicMock(return_value='container')
            assert zdb.container_sal == 'container'
            zdb.node_sal.containers.get.assert_called_once_with(zdb.data['container'])

    def test_zerodb_sal(self):
        """
        Test node_sal property
        """
        with patch('js9.j.clients.zero_os.sal.get_zerodb', MagicMock(return_value='zdb_sal')) as zdb_sal:
            patch('js9.j.clients.zero_os.sal.node_get', MagicMock()).start()
            zdb = Zerodb('zdb', data=self.valid_data)
            assert zdb.zerodb_sal == 'zdb_sal'
            assert zdb_sal.called