##
# File:    testFtpUtils.py
# Author:  dwp
# Date:    3-Aug-2021
#
# Updates:
#
##
"""
Archive data transfer operation utilities using FTP protocol

"""

__docformat__ = "google en"
__author__ = "Dennis Piehl"
__email__ = "dennis.piehl@rcsb.org"
__license__ = "Apache 2.0"

#
#
import os.path
import time
import unittest
import logging

#
from rcsb.utils.io import __version__
from rcsb.utils.io.FtpUtil import FtpUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FtpUtilTests(unittest.TestCase):
    def setUp(self):
        self.__verbose = False
        #
        self.__serverId = "BACKUP_SERVER_RDI2"

        self.__hostName = "test.rebex.net"
        self.__userName = "demo"
        self.__password = "password"
        # self.__keyFilePath =
        # self.__keyFileType =
        #
        # self.__testLocalOutputFilePath = os.path.join(HERE, "test-output", "readme.txt")
        self.__workPath = os.path.join(HERE, "test-output")
        #
        self.__startTime = time.time()
        logger.debug("Running tests on version %s", __version__)
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testFtpOpsPublic(self):
        """Test case - connection and ops to public server"""
        try:
            ftpU = FtpUtil()
            ok = ftpU.connect(self.__hostName, self.__userName, pw=self.__password)
            self.assertTrue(ok)
            fL = ftpU.listdir("/pub/example")
            logger.info("listdir: %r", fL)
            self.assertGreater(len(fL), 2)
            #
            ok = ftpU.get("/pub/example/readme.txt", os.path.join(self.__workPath, "readme.txt"))
            self.assertTrue(ok)
            #
            # Read-only public server - expecting a failure here
            ok = ftpU.put(os.path.join(self.__workPath, "readme.txt"), "/pub/example/readme.txt")
            self.assertFalse(ok)
            #
            ftpU.close()
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    # @unittest.skip("private test")
    def testFtpRemote(self):
        """Test case - connection to a remote public server -"""
        try:
            hostName = "ftp.rcsb.org"
            userName = "anonymous"
            pw = ""
            ftpU = FtpUtil()
            ok = ftpU.connect(hostName, userName, pw=pw)
            self.assertTrue(ok)
            fL = ftpU.listdir("/pub/pdb")
            logger.info("listdir: %r", fL)
            self.assertGreater(len(fL), 2)
            result = ftpU.stat("/pub/pdb")
            logger.info("stat: %r", result)
            ok = ftpU.close()
            self.assertEqual(ok, True)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    # @unittest.skip("private test")
    def testFtpRemoteReadOps(self):
        """Test case -  list directories and retrieve files -"""
        try:
            hostName = "ftp.rcsb.org"
            userName = "anonymous"
            pw = ""
            ftpU = FtpUtil()
            ok = ftpU.connect(hostName, userName, pw=pw)
            self.assertTrue(ok)

            testDirPath = os.path.join("/pub", "pdb")
            testFilePath1 = os.path.join(testDirPath, "README")
            testFilePath2 = os.path.join(testDirPath, "welcome.msg")
            #
            result = ftpU.listdir(testDirPath)
            logger.info("listdir: %r", result)
            #
            ftpU.get(testFilePath1, os.path.join(self.__workPath, "README"))
            ftpU.get(testFilePath2, os.path.join(self.__workPath, "welcome.msg"))
            #
            ok = ftpU.close()
            self.assertEqual(ok, True)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteFtpTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(FtpUtilTests("testFtpOpsPublic"))
    suiteSelect.addTest(FtpUtilTests("testFtpRemote"))
    suiteSelect.addTest(FtpUtilTests("testFtpRemoteReadOps"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = suiteFtpTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
    #
