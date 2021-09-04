# File:    FileLockTests.py
# Author:  J. Westbrook
# Date:    3-Aug-2021
# Version: 0.001
#
# Update:
#
#
##
"""
Tests for file locking methods.
"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import os
import sys
import threading
import time
import unittest

import multiprocess as multiprocessing

from rcsb.utils.io import __version__
from rcsb.utils.io.CryptUtils import CryptUtils
from rcsb.utils.io.FileLock import FileLock, Timeout

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ExecuteThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.ex = None
        return None

    def run(self):
        try:
            threading.Thread.run(self)
        except Exception:
            self.ex = sys.exc_info()
        return None

    def join(self, *arg):
        _ = arg
        threading.Thread.join(self)
        if self.ex is not None:
            raise self.ex[0].with_traceback(self.ex[1], self.ex[2])
        return None


class FileLockTests(unittest.TestCase):
    def setUp(self):
        self.__workPath = os.path.join(HERE, "test-output")
        self.__lockPath = os.path.join(self.__workPath, "shared-locks")
        self.__testFilePath = os.path.join(HERE, "test-data", "TEST-FILE.DAT")
        self.__startTime = time.time()
        logger.debug("Running tests on version %s", __version__)
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testSimpleLock(self):
        """Test case - context manager acquire and release lock"""
        try:
            lock = FileLock(os.path.join(self.__lockPath, "simple.lock"))
            with lock as l1:
                time.sleep(4)
                self.assertTrue(lock.isLocked())
                self.assertTrue(lock is l1)
            self.assertFalse(lock.isLocked())
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testNestedLock(self):
        """Test case - nested context managers acquire and release lock"""
        try:
            lock = FileLock(os.path.join(self.__lockPath, "simple.lock"))
            with lock as l1:
                self.assertTrue(lock.isLocked())
                self.assertTrue(lock is l1)

                with lock as l2:
                    self.assertTrue(lock.isLocked())
                    self.assertTrue(lock is l2)

                    with lock as l3:
                        self.assertTrue(lock.isLocked())
                        self.assertTrue(lock is l3)

                    self.assertTrue(lock.isLocked())
                self.assertTrue(lock.isLocked())
            self.assertFalse(lock.isLocked())
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testContextException(self):
        """Test case - context manager exceptions"""
        lock = FileLock(os.path.join(self.__lockPath, "simple.lock"))
        try:
            with lock as lock1:
                self.assertIs(lock, lock1)
                self.assertTrue(lock.isLocked())
                raise Exception()
        except Exception:
            self.assertFalse(lock.isLocked())

    def testLockTimeout(self):
        """Test case - file lock timeout"""
        try:
            lock1 = FileLock(os.path.join(self.__lockPath, "simple.lock"))
            lock2 = FileLock(os.path.join(self.__lockPath, "simple.lock"))

            # Acquire lock 1.
            lock1.acquire()
            self.assertTrue(lock1.isLocked())
            self.assertFalse(lock2.isLocked())

            # Try to acquire lock 2.
            self.assertRaises(Timeout, lock2.acquire, timeout=1)
            self.assertFalse(lock2.isLocked())
            self.assertTrue(lock1.isLocked())

            # Release lock 1.
            lock1.release()
            self.assertFalse(lock1.isLocked())
            self.assertFalse(lock2.isLocked())

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testThreadedLocking(self):
        """Test case:  locking in multiple threads"""

        def thread1():
            """
            Require lock1.
            """
            for _ in range(1000):
                with lock1:
                    self.assertTrue(lock1.isLocked())
                    self.assertFalse(lock2.isLocked())
            return None

        def thread2():
            """
            Require lock2.
            """
            for _ in range(1000):
                with lock2:
                    self.assertFalse(lock1.isLocked())
                    self.assertTrue(lock2.isLocked())
            return None

        numThreads = 10

        lock1 = FileLock(os.path.join(self.__lockPath, "simple.lock"))
        lock2 = FileLock(os.path.join(self.__lockPath, "simple.lock"))

        threads1 = [ExecuteThread(target=thread1) for i in range(numThreads)]
        threads2 = [ExecuteThread(target=thread2) for i in range(numThreads)]

        for i in range(numThreads):
            threads1[i].start()
            threads2[i].start()
        for i in range(numThreads):
            threads1[i].join()
            threads2[i].join()

        self.assertFalse(lock1.isLocked())
        self.assertFalse(lock2.isLocked())
        return None

    def proc1(self, numTimes):
        """ """
        hD = CryptUtils().getFileHash(self.__testFilePath, "MD5")
        lock1 = FileLock(os.path.join(self.__lockPath, "simple.lock"))
        fp1 = os.path.join(self.__lockPath, "simple")
        ok = True
        for _ in range(numTimes):
            with lock1:
                self.assertTrue(lock1.isLocked())
                with open(fp1, "wb") as ofh:
                    with open(self.__testFilePath, "rb") as ifh:
                        ofh.write(ifh.read())
                thD = CryptUtils().getFileHash(fp1, "MD5")
                ok = ok and hD == thD
        return ok

    def testMultiprocessLocking(self):
        """Test case:  locking accross multiple processors"""
        ok = self.proc1(2)
        self.assertTrue(ok)
        numProc = 8

        with multiprocessing.Pool(processes=numProc) as pool:  # pylint: disable=not-callable
            ret = list(pool.imap_unordered(self.proc1, range(numProc * numProc)))
            # ret = list(pool.map(self.proc1, range(numProc*numProc)))
        for ok in ret:
            self.assertTrue(ok)
        return None


#
def lockSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(FileLockTests("testSimpleLock"))
    suiteSelect.addTest(FileLockTests("testContextException"))
    suiteSelect.addTest(FileLockTests("testLockTimeout"))
    suiteSelect.addTest(FileLockTests("testThreadedLocking"))
    suiteSelect.addTest(FileLockTests("testMultiprocessLocking"))
    return suiteSelect


if __name__ == "__main__":
    #
    mySuite = lockSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
