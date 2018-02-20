from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os

import pytest

from hardware_check import HardwareCheck
from zerorobot import config
from zerorobot.template_uid import TemplateUID
from js9 import j


class TestHardwareCheckTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_data = {
            'chatId': 'chatId',
            'supported': [{'hddCount': 2, 'ram': 4, 'cpu': 4, 'ssdCount': 2, 'name': 'name'}],
            'botToken': 'botToken'}

        config.DATA_DIR = tempfile.mkdtemp(prefix='0-templates_')
        HardwareCheck.template_uid = TemplateUID.parse(
            'github.com/zero-os/0-templates/%s/%s' % (HardwareCheck.template_name, HardwareCheck.version))
        patch('js9.j.tools')

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DATA_DIR):
            shutil.rmtree(config.DATA_DIR)

    def test_invalid_data(self):
        data = {}
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the botToken'):
            HardwareCheck(name='hw', data=data)

        data['botToken'] = 'botToken'
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the chatId'):
            HardwareCheck(name='hw', data=data)

        data['chatId'] = 'chatId'
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the supported'):
            HardwareCheck(name='hw', data=data)

        data['supported'] = [{'ssdCount': 2}]
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the hddCount'):
            HardwareCheck(name='hw', data=data)

        data['supported'] = [{'ssdCount': 2, 'hddCount': 2}]
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the ram'):
            HardwareCheck(name='hw', data=data)

        data['supported'] = [{'ssdCount': 2, 'hddCount': 2, 'ram': 4}]
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the cpu'):
            HardwareCheck(name='hw', data=data)

        data['supported'] = [{'ssdCount': 2, 'hddCount': 2, 'ram': 4, 'cpu': 4}]
        with pytest.raises(ValueError, message='template should fail to instantiate if data dict is missing the name'):
            HardwareCheck(name='hw', data=data)

    def test_valid_data(self):
        HardwareCheck(name='hw', data=self.valid_data)

    def test_get_bot_client(self):
        with patch('js9.j.clients.telegram_bot.get', MagicMock()) as client_get:
            hw = HardwareCheck(name='hw', data=self.valid_data)
            hw._get_bot_client()
            data = {
                'bot_token_': hw.data['botToken'],
            }
            client_get.assert_called_with(instance=hw.guid, data=data, create=True, die=True)
