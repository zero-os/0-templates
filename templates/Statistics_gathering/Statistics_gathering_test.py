from unittest.mock import MagicMock, patch
import os

import pytest
from js9 import j
from Statistics_gathering import StatisticsGathering
from zerorobot.template.state import StateCheckError

from JumpScale9Zrobot.test.utils import ZrobotBaseTest, mock_decorator

patch("zerorobot.template.decorator.timeout", MagicMock(return_value=mock_decorator)).start()
patch("zerorobot.template.decorator.retry", MagicMock(return_value=mock_decorator)).start()


class TestStatisticsTemplate(ZrobotBaseTest):
    @classmethod
    def setUpClass(cls):
        super().preTest(os.path.dirname(__file__), StatisticsGathering)

    def setUp(self):
        self.client_get = patch('js9.j.clients', MagicMock()).start()

    def test_start_with_database(self):
        """
        Test statistics start
        """
        stat = StatisticsGathering('statistic')
        stat.state.set('actions', 'running', 'ok')

        stat.start()
        db=j.clients.influxdb.get('statistics-gathering', data={'database': 'statistics-gathering'})
        db.get_list_database = MagicMock(return_value='statistics-gathering')
        assert stat.state.check('actions', 'running', 'ok')
    
    def test_start_without_database(self):
        """
        Test statistics start
        """
        stat = StatisticsGathering('statistic')
        stat.state.set('actions', 'running', 'ok')
        db=j.clients.influxdb.get('statistics-gathering')
        db.get_list_database = MagicMock(return_value='')
        stat.start()
        assert stat.state.check('actions', 'running', 'ok')

    def test_stop(self):
        """
        Test statistics stop
        """
        stat = StatisticsGathering('statistic')
        stat.state.set('actions', 'running', 'ok')
        stat.state.delete = MagicMock(return_value=True)

        stat.stop()




