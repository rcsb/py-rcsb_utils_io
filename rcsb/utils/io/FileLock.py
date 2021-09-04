##
# File: FileLock.py
# Date: 3-Sep-2021
#
# A simple implementation of locking using a file system lock file.
# Adapted from a portion of the py-filelock package https://github.com/benediktschmitt/py-filelock.
##

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import threading
import time
import typing

from rcsb.utils.io.FileUtil import FileUtil

logger = logging.getLogger(__name__)


class Timeout(TimeoutError):
    pass


class AcquireProxy(object):
    """This proxy class avoids invoking the __enter__() method multiple times."""

    def __init__(self, lock):
        self.lock = lock
        return None

    def __enter__(self):
        return self.lock

    def __exit__(self, excType, excValue, traceback):
        self.lock.release()
        return None


class FileLock(object):
    """Implements a locking protocol based on the existence of a file."""

    def __init__(self, lockFilePath: str, defaultTimeout: typing.Optional[float] = 5.0):
        """Implements a locking protocol based on the existence of a file.

        Args:
            lockFilePath (str): path to lock file
            defaultTimeout (typing.Optional[float], optional): time out to acquire a lock (seconds). Defaults to 5.0.

        """

        # The path to the lock file.
        self.__lockFilePath = lockFilePath
        #
        # File descriptor for the lock file returned by os.open() and None indicates that no lock is held.
        self.__lockFileFileDescriptor = None

        # The default timeout value.
        self.__defaultTimeout = defaultTimeout

        # Protects the lock count
        self.__lockCountLock = threading.Lock()

        # Lock count to manage nested context manager instances of locking
        self.__lockCount = 0
        return None

    def getLockFilePath(self) -> str:
        """Return the path to the lock file."""
        return self.__lockFilePath

    def isLocked(self) -> bool:
        """Return the status of the file lock."""
        return self.__lockFileFileDescriptor is not None

    def acquire(self, timeout: typing.Optional[float] = None, pollInterval: typing.Optional[float] = 0.05) -> typing.Type[AcquireProxy]:
        """Acquire file lock.

        Args:
            timeout (typing.Optional[float], optional): timeout to acquire lock (seconds). Defaults to None.
            pollInterval (typing.Optional[float], optional): retry interval (seconds). Defaults to 0.05.

        Raises:
            Timeout: if acquire timeout is exceeded

        Returns:
            AcquireProxy: returns a proxy object for the file lock.
        """

        # Use the default timeout, if no timeout is provided.
        timeout = timeout if timeout else self.__defaultTimeout

        with self.__lockCountLock:
            self.__lockCount += 1

        lockId = id(self)
        lockFilePath = self.__lockFilePath
        startTime = time.time()
        try:
            while True:
                with self.__lockCountLock:
                    if not self.isLocked():
                        logger.debug("Attempting to acquire lock %s on %s", lockId, lockFilePath)
                        self.__doAquireLock()

                if self.isLocked():
                    logger.debug("Lock %s acquired on %s", lockId, lockFilePath)
                    break
                elif timeout >= 0 and time.time() - startTime > timeout:
                    logger.debug("Timeout on acquiring lock %s on %s", lockId, lockFilePath)
                    raise Timeout(self.__lockFilePath)
                else:
                    logger.debug("Lock %s not acquired on %s, waiting %s seconds ...", lockId, lockFilePath, pollInterval)
                    time.sleep(pollInterval)
        except Exception:
            with self.__lockCountLock:
                self.__lockCount = max(0, self.__lockCount - 1)

            raise
        return AcquireProxy(lock=self)

    def release(self, force: typing.Optional[bool] = False):
        """Release an acquired file lock.

        Args:
            force (typing.Optional[bool], optional): Force release even if there are lock holders. Defaults to False.
        """
        with self.__lockCountLock:
            if self.isLocked():
                self.__lockCount -= 1

                if self.__lockCount == 0 or force:
                    lockId = id(self)
                    logger.debug("Attempting to release lock %s on %s", lockId, self.__lockFilePath)
                    self.__doReleaseLock()
                    self.__lockCount = 0
                    logger.debug("Lock %s released on %s", lockId, self.__lockFilePath)
        return None

    def __doAquireLock(self):
        fU = FileUtil()
        mode = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_TRUNC
        try:
            fU.mkdir(os.path.dirname(self.__lockFilePath))
            fd = os.open(self.__lockFilePath, mode)
        except (IOError, OSError):
            pass
        else:
            self.__lockFileFileDescriptor = fd
        return None

    def __doReleaseLock(self):
        os.close(self.__lockFileFileDescriptor)
        self.__lockFileFileDescriptor = None
        try:
            os.remove(self.__lockFilePath)
        except OSError:
            pass
        return None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, excType, excValue, traceback):
        self.release()
        return None

    def __del__(self):
        self.release(force=True)
        return None
