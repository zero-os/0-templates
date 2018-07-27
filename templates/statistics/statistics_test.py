from unittest.mock import MagicMock, patch
import os

import pytest
from js9 import j
from statistics import Statistics
from zerorobot.template.state import StateCheckError

from JumpScale9Zrobot.test.utils import ZrobotBaseTest, mock_decorator

patch("zerorobot.template.decorator.timeout", MagicMock(return_value=mock_decorator)).start()
patch("zerorobot.template.decorator.retry", MagicMock(return_value=mock_decorator)).start()


class TestStatisticsTemplate(ZrobotBaseTest):
    @classmethod
    def setUpClass(cls):
        super().preTest(os.path.dirname(__file__), Statistics)

    def setUp(self):
        self.client_get = patch('js9.j.clients', MagicMock()).start()

    def test_install_with_database(self):
        """
        Test statistics start
        """
        stat = Statistics('statistic')
        stat.state.set('actions', 'running', 'ok')

        stat.install()
        assert stat.state.check('actions', 'running', 'ok')
    
    def test_install_without_database(self):
        """
        Test statistics start
        """
        stat = Statistics('statistic')
        stat.state.set('actions', 'running', 'ok')
        db=j.clients.influxdb.get('statistics')
        db.get_list_database = MagicMock(return_value='')
        stat.install()
        assert stat.state.check('actions', 'running', 'ok')

    def test_uninstall(self):
        """
        Test statistics stop
        """
        stat = Statistics('statistic')
        stat.state.set('actions', 'running', 'ok')
        stat.state.delete = MagicMock(return_value=True)

        stat.uninstall()




