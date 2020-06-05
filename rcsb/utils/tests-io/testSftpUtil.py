##
# File:    testSftpUtils.py
# Author:  jdw
# Date:    5-Jun-2020
#
# Updates:
#
##
"""
Archive data transfer operation utilities using SFTP protocol

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

#
#
import os.path
import time
import unittest
import logging

#
from rcsb.utils.io import __version__
from rcsb.utils.io.SftpUtil import SftpUtil


HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SftpUtilTests(unittest.TestCase):
    def setUp(self):
        self.__verbose = False
        #
        self.__serverId = "BACKUP_SERVER_RDI2"

        self.__hostName = "test.rebex.net"
        self.__userName = "demo"
        self.__password = "password"
        self.__hostPort = 22
        # self.__keyFilePath =
        # self.__keyFileType =
        #
        self.__testLocalFilePath = os.path.join(HERE, "test-data", "TEST-FILE.DAT")
        self.__testLocalOutputFilePath = os.path.join(HERE, "test-output", "readme.txt")
        self.__workPath = os.path.join(HERE, "test-output")
        #
        self.__startTime = time.time()
        logger.debug("Running tests on version %s", __version__)
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testSftpOpsPublic(self):
        """Test case - connection and ops to public server
        """
        try:
            sftpU = SftpUtil()
            ok = sftpU.connect(self.__hostName, self.__userName, pw=self.__password, port=self.__hostPort)
            self.assertTrue(ok)
            fL = sftpU.listdir("/pub/example")
            logger.info("listdir: %r", fL)
            self.assertGreater(len(fL), 2)
            #
            ok = sftpU.get("/pub/example/readme.txt", os.path.join(self.__workPath, "readme.txt"))
            self.assertTrue(ok)
            #
            result = sftpU.stat("/pub/example")
            logger.info("stat: %r", result)
            #
            # Read-only public server - expecting a failure here
            ok = sftpU.put(os.path.join(self.__workPath, "readme.txt"), "/pub/example/readme.txt")
            self.assertFalse(ok)
            #
            sftpU.close()
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    @unittest.skip("private test")
    def testSftpLocal(self):
        """Test case - connection to a local private server -
           1-receive

        """
        try:
            userName = "transporter"
            pw = ""
            hostName = ""
            sftpU = SftpUtil()
            ok = sftpU.connect(hostName, userName, pw=pw, port=22)
            self.assertTrue(ok)
            fL = sftpU.listdir("4-coastal")
            logger.info("listdir: %r", fL)
            self.assertGreater(len(fL), 2)
            ok = sftpU.close()
            self.assertEqual(ok, True)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    @unittest.skip("private test")
    def testSftpLocalTransferOps(self):
        """Test case -  transfer and remove files and directories -
        """
        try:
            userName = ""
            pw = ""
            hostName = "bl-east.rcsb.org"
            sftpU = SftpUtil()
            ok = sftpU.connect(hostName, userName, pw=pw, port=22)
            self.assertTrue(ok)

            testDirPath = os.path.join("4-coastal", "test")
            testFilePath1 = os.path.join(testDirPath, "TEST-FILE-1.DAT")
            testFilePath2 = os.path.join(testDirPath, "TEST-FILE-2.DAT")
            ok = sftpU.mkdir(testDirPath)
            ok = sftpU.put(self.__testLocalFilePath, testFilePath1)
            ok = sftpU.put(self.__testLocalFilePath, testFilePath2)
            #
            sftpU.get(testFilePath1, os.path.join(self.__workPath, "TEST-FILE-1.DAT"))
            sftpU.get(testFilePath2, os.path.join(self.__workPath, "TEST-FILE-2.DAT"))
            #
            result = sftpU.listdir(testDirPath)
            logger.info("listdir: %r", result)
            ok = sftpU.remove(testFilePath1)
            ok = sftpU.remove(testFilePath2)
            #
            result = sftpU.listdir(testDirPath)
            logger.debug("listdir: %r", result)
            #
            ok = sftpU.rmdir(testDirPath)
            result = sftpU.listdir("4-coastal")
            logger.info("listdir after remove: %r", result)
            ok = sftpU.close()
            self.assertEqual(ok, True)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteSftpTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(SftpUtilTests("testSftpOpsPublic"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = suiteSftpTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
    #
