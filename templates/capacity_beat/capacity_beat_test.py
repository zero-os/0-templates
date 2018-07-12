from unittest.mock import MagicMock, patch
import os

import pytest

from node import Node, NODE_CLIENT
from zerorobot.template.state import StateCheckError

from JumpScale9Zrobot.test.utils import ZrobotBaseTest, mock_decorator


patch("zerorobot.template.decorator.timeout", MagicMock(return_value=mock_decorator)).start()
patch("zerorobot.template.decorator.retry", MagicMock(return_value=mock_decorator)).start()
patch("gevent.sleep", MagicMock()).start()


class TestCapacityBeatTemplate(ZrobotBaseTest):

    @classmethod
    def setUpClass(cls):
        super().preTest(os.path.dirname(__file__), Node)

    def setUp(self):
        self.client_get = patch('js9.j.clients', MagicMock()).start()

    def tearDown(self):
        patch.stopall()

    # more TBD