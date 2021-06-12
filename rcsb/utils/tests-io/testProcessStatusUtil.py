##
# File:    ExecProcessStatusTests.py
# Author:  J. Westbrook
# Date:    25-Jan-2020
# Version: 0.001
#
# Updates:
##
"""
Test cases for process status info methods
"""
__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import pprint
import time
import unittest

from rcsb.utils.io.ProcessStatusUtil import ProcessStatusUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ProcessStatusTests(unittest.TestCase):
    """
    Test cases for  process status info methods
    """

    def setUp(self):
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testProcessStatus(self):
        """Test case -  process status request"""
        try:
            psU = ProcessStatusUtil()
            psD = psU.getInfo()
            logger.debug("Process status dictionary \n%s", pprint.pformat(psD, indent=3))
            self.assertGreater(psD["uptimeSeconds"], 10)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteProcessStatus():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ProcessStatusTests("testProcessStatus"))
    return suiteSelect


if __name__ == "__main__":
    #
    mySuite = suiteProcessStatus()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
