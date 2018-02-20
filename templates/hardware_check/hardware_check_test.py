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
            'supported': [{'hddCount': 2, 'ram': 8, 'cpu': 'cpu', 'ssdCount': 2, 'name': 'name'}],
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
        """
        Test HardwareCheck creation with valid data
        """
        hw = HardwareCheck(name='hw', data=self.valid_data)
        assert hw.data == self.valid_data

    def test_get_bot_client(self):
        """
        test _get_bot_client
        """
        with patch('js9.j.clients.telegram_bot.get', MagicMock()) as client_get:
            hw = HardwareCheck(name='hw', data=self.valid_data)
            hw._get_bot_client()
            data = {
                'bot_token_': hw.data['botToken'],
            }
            client_get.assert_called_with(instance=hw.guid, data=data, create=True, die=True)

    def test_ram(self):
        """
        Test ram returns correct ram
        """
        hw = HardwareCheck(name='hw', data=self.valid_data)
        client = MagicMock()
        client.info.mem = MagicMock(return_value={'total': 1048576})
        ram = hw._ram(client)

        assert ram == 1

    def test_cpu(self):
        """
        Test cpu returns correct name
        """
        hw = HardwareCheck(name='hw', data=self.valid_data)
        client = MagicMock()
        client.info.cpu = MagicMock(return_value=[{'modelName': 'model name cpu'}])
        cpu = hw._cpu(client)

        assert cpu == 'cpu'

    def test_disk(self):
        """
        test disk returns correct count
        """
        hw = HardwareCheck(name='hw', data=self.valid_data)
        disks = {
            'blockdevices': [
                {
                    'tran': 'usb'
                },
                {
                    'rota': '1',
                    'name': 'hdd',
                    'size': 16,
                    'phy-sec': 2,
                },
                {
                    'rota': '0',
                    'name': 'ssd',
                    'size': 16,
                    'phy-sec': 2,
                }
            ]
        }
        client = MagicMock()
        system_get_result = MagicMock(stdout='test\n')
        system = MagicMock()
        system.get = MagicMock(return_value=system_get_result)
        client.system = MagicMock(return_value=system)
        client.disk.list = MagicMock(return_value=disks)
        hdd, ssd = hw._disk(client)

        assert hdd == 1
        assert ssd == 1

    def test_disk_exception(self):
        """
        Test disk throws exception when sector test fails
        """
        with pytest.raises(j.exceptions.RuntimeError, message='Template should raise error if stdout is not test\n'):
            hw = HardwareCheck(name='hw', data=self.valid_data)
            disks = {
                'blockdevices': [
                    {
                        'tran': 'usb'
                    },
                    {
                        'rota': '1',
                        'name': 'hdd',
                        'size': 16,
                        'phy-sec': 2,
                    },
                    {
                        'rota': '0',
                        'name': 'ssd',
                        'size': 16,
                        'phy-sec': 2,
                    }
                ]
            }
            client = MagicMock()
            client.disk.list = MagicMock(return_value=disks)
            hw._disk(client)

    def test_check_succussful(self):
        """
        Test check is successful when hardware is supported
        :return:
        """
        patch('js9.j.clients.zero_os.get', MagicMock()).start()
        hw = HardwareCheck(name='hw', data=self.valid_data)
        supported = self.valid_data['supported'][0]
        hw._disk = MagicMock(return_value=(supported['hddCount'], supported['ssdCount']))
        hw._ram = MagicMock(return_value=supported['ram'])
        hw._cpu = MagicMock(return_value=supported['cpu'])
        client = MagicMock()
        hw._get_bot_client = MagicMock(return_value=client)
        hw.check('node')

        client.send_message.assert_called_once_with('chatId', 'Node with id node has completed the hardwarecheck successfully.')

    def test_check_fail(self):
        """
        Test that check fails if any of hardware specs arent supported
        """
        patch('js9.j.clients.zero_os.get', MagicMock()).start()
        hw = HardwareCheck(name='hw', data=self.valid_data)
        supported = self.valid_data['supported'][0]
        hw._disk = MagicMock(return_value=(supported['hddCount'], supported['ssdCount']))
        hw._cpu = MagicMock(return_value=supported['cpu'])
        client = MagicMock()
        hw._get_bot_client = MagicMock(return_value=client)

        # check with no supported ram
        hw._ram = MagicMock(return_value=supported['ram'] -6)
        with pytest.raises(j.exceptions.RuntimeError, message='Template should raise error if ram is not supported'):
            hw.check('node')
        hw._ram = MagicMock(return_value=supported['ram'])

        # check with no supported cpu
        hw._cpu = MagicMock(return_value='othercpu')
        with pytest.raises(j.exceptions.RuntimeError, message='Template should raise error if cpu is not supported'):
            hw.check('node')
        hw._cpu = MagicMock(return_value=supported['cpu'])

        # check with no supported hdd
        hw._disk = MagicMock(return_value=(0, supported['ssdCount']))
        with pytest.raises(j.exceptions.RuntimeError, message='Template should raise error if hddCount is not supported'):
            hw.check('node')
        hw._disk = MagicMock(return_value=(supported['hddCount'], supported['ssdCount']))

        # check with no supported ssd
        hw._disk = MagicMock(return_value=(supported['hddCount'], 0))
        with pytest.raises(j.exceptions.RuntimeError, message='Template should raise error if ssdCount is not supported'):
            hw.check('node')
