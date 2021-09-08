##
# File:    LogUtilTests.py
# Author:  J. Westbrook
# Date:    7-Sep-2021
# Version: 0.001
#
# Updates:
##
"""
Test cases structured logging formatter.
"""
__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import json
import logging
import os
import time
import unittest

from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.LogUtil import StructFormatter, DetailedStructFormatter
from rcsb.utils.io.MarshalUtil import MarshalUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LogUtilTests(unittest.TestCase):
    """Test cases for structured logging tools -"""

    def setUp(self):
        self.__workPath = os.path.join(HERE, "test-output")
        #
        self.__testLogFileMin = os.path.join(self.__workPath, "logfile-min.json")
        self.__testLogFileDetailed = os.path.join(self.__workPath, "logfile-detailed.json")
        fU = FileUtil()
        fU.remove(self.__testLogFileMin)
        fU.remove(self.__testLogFileDetailed)

        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testStructLogging(self):
        try:
            sl = logging.FileHandler(filename=self.__testLogFileMin)
            sl.setFormatter(StructFormatter(fmt=None, mask=None))
            myLogger = logging.getLogger("test")
            myLogger.addHandler(sl)
            myLogger.setLevel(logging.INFO)
            s1 = "string one"
            i1 = 5
            f1 = 2.0
            myLogger.info("s1 %r i1 %r f1 %r", s1, i1, f1, extra={"q1": 1, "q2": (1, 1)})
            try:
                rD = {}
                rD["b"] = rD["a"]
            except Exception as e:
                myLogger.exception("Failing with %s", str(e), extra={"q1": 1, "q2": (1, 1)})

            mU = MarshalUtil()
            tSL = mU.doImport(self.__testLogFileMin, fmt="list")
            for tS in tSL:
                tD = json.loads(tS)
                self.assertEqual(tD["q1"], 1)
                self.assertEqual(tD["q2"], [1, 1])

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testDetailedStructLogging(self):
        try:
            sl = logging.FileHandler(filename=self.__testLogFileDetailed)
            sl.setFormatter(DetailedStructFormatter(fmt=None, mask=None))
            myLogger = logging.getLogger("test")
            myLogger.addHandler(sl)
            myLogger.setLevel(logging.INFO)
            s1 = "string one"
            i1 = 5
            f1 = 2.0
            myLogger.info("s1 %r i1 %r f1 %r", s1, i1, f1, extra={"q1": 1, "q2": (1, 1)})
            try:
                rD = {}
                rD["b"] = rD["a"]
            except Exception as e:
                myLogger.exception("Failing with %s", str(e), extra={"q1": 1, "q2": (1, 1)})
            #
            mU = MarshalUtil()
            tSL = mU.doImport(self.__testLogFileDetailed, fmt="list")
            for tS in tSL:
                tD = json.loads(tS)
                self.assertEqual(tD["q1"], 1)
                self.assertEqual(tD["q2"], [1, 1])
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteLogFile():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(LogUtilTests("testStructLogging"))
    suiteSelect.addTest(LogUtilTests("testDetailedStructLogging"))
    return suiteSelect


if __name__ == "__main__":
    #
    mySuite = suiteLogFile()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
