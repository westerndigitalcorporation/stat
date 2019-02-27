import os
from unittest import TestCase

from stat_main import StatMainEntrance

class RealTestCase(TestCase):
    __TEST_PATH = "../.."
    __CWD = ''

    @classmethod
    def setUpClass(cls):
        cls.__CWD = os.getcwd()
        os.chdir(cls.__TEST_PATH)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.__CWD)

    def test_realCase(self):
        #entrance = StatMainEntrance()
        #entrance.handleCommandLine([])
        pass
