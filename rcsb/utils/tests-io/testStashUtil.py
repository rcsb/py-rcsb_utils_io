##
# File:    testStashUtils.py
# Author:  jdw
# Date:    21-Jul-2020
#
# Updates:
#
##
"""
Test utilities to stash and recover a data in collection of directories to and from
remote sftp, http or local POSIX file storage resources.
"""

__docformat__ = "google en"
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
from importlib.metadata import version as get_package_version
from rcsb.utils.io.StashUtil import StashUtil

__version__ = get_package_version("rcsb.utils.io")


HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class StashUtilTests(unittest.TestCase):
    def setUp(self):
        self.__testLocalDirPath = os.path.join(HERE, "test-data", "topdir")
        self.__workPath = os.path.join(HERE, "test-output")
        #
        self.__startTime = time.time()
        logger.debug("Running tests on version %s", __version__)
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testStashOps(self):
        """Test case - create, store and recover a stash bundle"""
        try:
            url = userName = password = remoteStashPrefix = None
            remoteDirPath = os.path.join(self.__workPath, "stash")
            localRestoreDirPath = os.path.join(self.__workPath, "stash-recovered")
            stU = StashUtil(self.__workPath, "testBundleFile")
            ok = stU.makeBundle(self.__testLocalDirPath, ["subdirA", "subdirB"])
            self.assertTrue(ok)
            ok = stU.storeBundle(url, remoteDirPath, remoteStashPrefix=remoteStashPrefix, userName=userName, password=password)
            self.assertTrue(ok)
            ok = stU.fetchBundle(localRestoreDirPath, url, remoteDirPath, remoteStashPrefix=remoteStashPrefix, userName=userName, password=password)
            self.assertTrue(ok)
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteStashTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(StashUtilTests("testStashOps"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = suiteStashTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
    #
