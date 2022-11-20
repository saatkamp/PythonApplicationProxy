# -*- coding: utf-8 -*-

import unittest

from .context import drivermanager


class BasicTestSuite(unittest.TestCase):
    """ Basic test cases """

    def test_usage_driver_manager(self):
        manager = drivermanager.DriverManager("./tests/driver-manager.yml")
        manager.publish("temp-livingroom", 100)
        manager.close()
        assert True


if __name__ == '__main__':
    unittest.main()
