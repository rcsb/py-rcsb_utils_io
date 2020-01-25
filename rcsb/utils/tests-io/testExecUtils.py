##
# File:    ExecUtilsTests.py
# Author:  J. Westbrook
# Date:    25-Jan-2020
# Version: 0.001
#
# Updates:
##
"""
Test cases for subprocess execution wrapper
"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import time
import unittest

from rcsb.utils.io.ExecUtils import ExecUtils

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ExecUtilsTests(unittest.TestCase):
    """
    Test cases for session encryption round trip -
    """

    def setUp(self):
        self.__workPath = os.path.join(HERE, "test-output")
        self.__testFilePath = os.path.join(self.__workPath, "TEST-REMOVE-SUBPROCESS-OUT.TXT")
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testSubprocessExecution(self):
        """Test case -  subprocess execution
        """
        try:
            exU = ExecUtils()
            ok = exU.run("/bin/ls", execArgList=["-l", "-a"], outPath=self.__testFilePath, outAppend=True, timeOut=1.0)
            self.assertTrue(ok)
            ok = exU.run("/bin/ls", execArgList=["-88", "-a"], outPath=self.__testFilePath, outAppend=True, timeOut=1.0)
            self.assertFalse(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteExecSubprocess():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ExecUtilsTests("testSubprocessExecution"))
    return suiteSelect


if __name__ == "__main__":
    #
    mySuite = suiteExecSubprocess()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
