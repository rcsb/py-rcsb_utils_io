##
# File:    testGitUtils.py
# Author:  jdw
# Date:    18-Jul-2021
#
# Updates:
#
##
"""
Test utilities
"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import os.path
import time
import random
import string
import unittest
import logging

#
from rcsb.utils.io import __version__
from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.GitUtil import GitUtil


HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class GitUtilTests(unittest.TestCase):
    def setUp(self):
        self.__workPath = os.path.join(HERE, "test-output")
        self.__startTime = time.time()
        logger.debug("Running tests on version %s", __version__)
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testGitOps(self):
        """Test case - git clone"""
        try:
            branch = "test-branch"
            repositoryPath = "rcsb/py-rcsb_exdb_assets_stash.git"
            localRepositoryPath = os.path.join(self.__workPath, "test-stash")
            fU = FileUtil()
            fU.remove(localRepositoryPath)
            gitToken = None
            gU = GitUtil(gitToken)
            ok = gU.clone(repositoryPath, localRepositoryPath, branch=branch)
            self.assertTrue(ok)
            logger.info("status %r", gU.status(localRepositoryPath))
            #
            gU.pull(localRepositoryPath, branch=branch)
            self.assertTrue(ok)
            logger.info("status %r", gU.status(localRepositoryPath))
            #
            testPath = os.path.join(localRepositoryPath, "stash", "TESTFILE.txt")
            self.__makeFile(testPath, 10)
            #
            ok = gU.addAll(localRepositoryPath, branch=branch)
            self.assertTrue(ok)
            logger.info("status %r", gU.status(localRepositoryPath))
            #
            ok = gU.commit(localRepositoryPath, branch=branch)
            self.assertTrue(ok)
            logger.info("status %r", gU.status(localRepositoryPath))
            #
            if gitToken:
                gU.push(localRepositoryPath, branch=branch)
                self.assertTrue(ok)
                logger.info("status %r", gU.status(localRepositoryPath))
            #
            gU.pull(localRepositoryPath, branch=branch)
            self.assertTrue(ok)
            logger.info("status %r", gU.status(localRepositoryPath))
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def __makeFile(self, fp, count):
        sLen = 50
        with open(fp, "w") as ofh:
            for ii in range(count):
                tS = "".join(random.choices(string.ascii_uppercase + string.digits, k=sLen))
                ofh.write("%d %s\n" % (ii, tS))


def suiteGitTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(GitUtilTests("testGitOps"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = suiteGitTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
    #
