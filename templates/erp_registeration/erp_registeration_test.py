from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os

import pytest

from erp_registeration import ErpRegisteration
from zerorobot import config
from zerorobot.template_uid import TemplateUID
from js9 import j


class TestErpRegisterationTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {
            'url': 'url',
            'db': 'db',
            'username': 'username',
            'password': 'password',
            'productId': 'productId',
            'botToken': 'botToken',
            'chatId': 'chatId'
        }
        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        ErpRegisteration.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (ErpRegisteration.template_name, ErpRegisteration.version))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def test_invalid_data(self):
        """
        Test create with invalid data
        :return:
        """
        data = {}
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the url'):
            ErpRegisteration(name='erp', data=data)

        data['url'] = 'url'
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the db'):
            ErpRegisteration(name='erp', data=data)

        data['db'] = 'db'
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the username'):
            ErpRegisteration(name='erp', data=data)

        data['username'] = 'username'
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the password'):
            ErpRegisteration(name='erp', data=data)

        data['password'] = 'password'
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the productId'):
            ErpRegisteration(name='erp', data=data)

        data['productId'] = 'productId'
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the botToken'):
            ErpRegisteration(name='erp', data=data)

        data['botToken'] = 'botToken'
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the chatId'):
            ErpRegisteration(name='erp', data=data)

    def test_create_valid_data(self):
        """
        Test create ErpRegisteration with valid data
        """
        erp = ErpRegisteration(name='erp', data=self.valid_data)
        erp.data = self.valid_data

    def test_get_erp_client(self):
        """
        Test _get_erp_client
        """
        with patch('js9.j.clients.erppeek.get', MagicMock()) as client_get:
            erp = ErpRegisteration(name='erp', data=self.valid_data)
            erp._get_erp_client()
            data = {
                'url': erp.data['url'],
                'db': erp.data['db'],
                'password_': erp.data['password'],
                'username': erp.data['username'],
            }
            client_get.assert_called_with(instance=erp.guid, data=data, create=True, die=True)

    def test_get_bot_client(self):
        """
        Test _get_bot_client
        :return:
        """
        with patch('js9.j.clients.telegram_bot.get', MagicMock()) as client_get:
            erp = ErpRegisteration(name='erp', data=self.valid_data)
            erp._get_bot_client()
            data = {
                'bot_token_': erp.data['botToken'],
            }
            client_get.assert_called_with(instance=erp.guid, data=data, create=True, die=True)

    def test_register_new_node(self):
        """
        Test register new node
        """
        erp = ErpRegisteration(name='erp', data=self.valid_data)
        client = MagicMock()
        client.count_records = MagicMock(return_value=0)
        erp._get_erp_client = MagicMock(return_value=client)
        erp._get_bot_client = MagicMock()
        erp.register('node')

        client.create_record.assert_called_once_with('stock.production.lot',
                                                     {'name': 'node', 'product_id': erp.data['productId']})
        assert erp._get_erp_client.called
        assert erp._get_bot_client.called

    def test_register_old_node(self):
        """
        Test register old node
        """
        erp = ErpRegisteration(name='erp', data=self.valid_data)
        client = MagicMock()
        client.count_records = MagicMock(return_value=1)
        erp._get_erp_client = MagicMock(return_value=client)
        erp._get_bot_client = MagicMock()
        erp.register('node')

        client.create_record.assert_not_called()
        assert erp._get_erp_client.called
        assert erp._get_bot_client.called

    def test_registeration_error(self):
        """
        Test error during registeration
        """
        with pytest.raises(j.exceptions.RuntimeError, message='action should fail if an error was raised'):
            erp = ErpRegisteration(name='erp', data=self.valid_data)
            erp._get_erp_client = MagicMock(side_effect=Exception)
            erp._get_bot_client = MagicMock()
            erp.register('node')
