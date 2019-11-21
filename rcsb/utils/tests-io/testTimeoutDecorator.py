##
# File:    TimeoutDecoratorTests.py
# Author:  J. Westbrook
# Date:    25-Oct-2019
# Version: 0.001
#
# Updates:
##
"""
Test cases for timeout decorator
"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import time
import unittest

from rcsb.utils.io.decorators import timeout, timeoutMp, TimeoutException

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TimeoutDecoratorTests(unittest.TestCase):
    """
    Test cases for timeout decorator
    """

    def setUp(self):
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    @timeout(10)
    def __longrunner1(self, iSeconds=10):
        logger.info("SLEEPING FOR %d seconds", iSeconds)
        time.sleep(iSeconds)
        logger.info("SLEEPING COMPLETED")

    def testTimeoutSignal(self):
        """Test case - timeout decorator (signal)
        """
        try:
            self.__longrunner1(20)
        except TimeoutException as e:
            logger.info("Caught timeout exception %s", str(e))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()
        else:
            logger.info("Successful completion")

    @timeoutMp(10)
    def __longrunner2(self, iSeconds=10):
        logger.info("SLEEPING FOR %d seconds", iSeconds)
        time.sleep(iSeconds)
        logger.info("SLEEPING COMPLETED")

    @unittest.skip("Python 3.8 serialization issue")
    def testTimeoutMulti(self):
        """Test case - timeout decorator (multiprocessing)
        """
        try:
            self.__longrunner2(20)
        except TimeoutException as e:
            logger.info("Caught timeout exception %s", str(e))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()
        else:
            logger.info("Successful completion")


def suiteTimeout():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(TimeoutDecoratorTests("testTimeoutMulti"))
    suiteSelect.addTest(TimeoutDecoratorTests("testTimeoutSignal"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = suiteTimeout()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
