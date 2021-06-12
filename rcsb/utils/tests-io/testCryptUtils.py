##
# File:    CryptUtilsTests.py
# Author:  J. Westbrook
# Date:    25-Oct-2017
# Version: 0.001
#
# Updates:
##
"""
Test cases for message encryption utilities
"""
__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import time
import unittest

from rcsb.utils.io.CryptUtils import CryptUtils

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CryptUtilsTests(unittest.TestCase):
    """
    Test cases for session encryption round trip -
    """

    def setUp(self):
        self.__workPath = os.path.join(HERE, "test-output")
        self.__testFilePath = os.path.join(self.__workPath, "TEST-REMOVE-ME.DAT")
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def __makeTestFile(self, filePath):
        lines = 1024 * 1024
        with open(filePath, "w") as ofh:
            for _ in range(lines):
                ofh.write("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n")
        logger.debug("Tests file created %s lines %d", filePath, lines)

    def testCryptFileRoundtrip(self):
        """Test case -  file encryption roundtrip"""
        try:
            ok = True
            fp = self.__testFilePath
            cu = CryptUtils()
            ky = cu.newKey()
            self.__makeTestFile(fp)
            #
            hDOrg = cu.getFileHash(fp)
            fnEnc = fp + ".enc"
            ok = cu.encryptFile(fp, fnEnc, ky)
            self.assertEqual(ok, True)
            fnRec = fnEnc + ".rec"
            ok = cu.decryptFile(fnEnc, fnRec, ky)
            self.assertEqual(ok, True)
            hDRec = cu.getFileHash(fnRec)
            self.assertEqual(hDOrg["hashDigest"], hDRec["hashDigest"])
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testCryptMessageRoundtrip(self):
        """Test case -  message encryption roundtrip"""
        try:
            cu = CryptUtils()
            ky = cu.newKey()
            msg = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n"
            encMsg = cu.encryptMessage(msg, ky)
            dcrMsg = cu.decryptMessage(encMsg, ky)
            self.assertEqual(msg, dcrMsg)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteFileCrypt():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(CryptUtilsTests("testCrypteFileRoundtrip"))
    suiteSelect.addTest(CryptUtilsTests("testCrypteMessageRoundtrip"))
    return suiteSelect


if __name__ == "__main__":
    #
    mySuite = suiteFileCrypt()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
