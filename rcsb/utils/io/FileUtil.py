##
# File: FileUtil.py
#
# Skeleton implementation for File I/O
#
# Updates:
#  5-Jun-2018 jdw add support for local copy operations using shutil.copy
#  6-Mar-2019 jdw add previously stubbed remote access and tar file member support
# 10-Mar-2019 jdw add exists() method
#
##

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

#
import contextlib
import logging
import os
import shutil
import tarfile

from rcsb.utils.io.decorators import retry

# pylint: disable=ungrouped-imports
try:
    import urllib.request as myurl
except Exception:
    import urllib2 as myurl

try:
    from urllib.parse import urlsplit
except Exception:
    from urlparse import urlsplit


logger = logging.getLogger(__name__)


class FileUtil(object):
    """ Skeleton implementation for File I/O operations

    """

    def __init__(self, workPath=None, **kwargs):
        _ = kwargs
        self.__workPath = workPath

    #
    def get(self, remote, local, **kwargs):
        """Fetch remote file to a local path.

        Arguments:
            remote (TYPE): Description
            local (TYPE): Description
            **kwargs: Description

                tarMember(str) : target member name in a remote tarfile

        Returns:
            bool: True for success or false otherwise

        """
        try:
            ret = False
            tarMember = kwargs.get("tarMember", None)
            #
            localFlag = self.isLocal(remote)
            #
            if localFlag and not tarMember:
                rPath = self.getFilePath(remote)
                lPath = self.getFilePath(local)
                shutil.copyfile(rPath, lPath)
                ret = True
            elif localFlag and tarMember:
                # Extract a particular member from a local tar file -
                rPath = self.getFilePath(remote)
                lPath = self.getFilePath(local)
                ret = self.__extractTarMember(rPath, tarMember, lPath)
                logger.debug("Extract %r from %r to %r status %r", tarMember, rPath, lPath, ret)
            elif not localFlag and tarMember:
                # Extract a particular member from a remote tar file
                tarPath = os.path.join(self.__workPath, self.getFileName(remote))
                ret = self.__fetchUrl(remote, tarPath)
                logger.debug("Fetched %r to %r status %r", remote, tarPath, ret)
                ret = self.__extractTarMember(tarPath, tarMember, self.getFilePath(local)) if ret else False
                logger.debug("Extract %r from %r to %r status %r", tarMember, tarPath, self.getFilePath(local), ret)
            elif not localFlag and not tarMember:
                ret = self.__fetchUrl(remote, self.getFilePath(local))
            else:
                ret = False
            #
        except Exception as e:
            logger.exception("For remote %r local %r failing with %s", remote, local, str(e))

        #
        return ret

    def put(self, local, remote, **kwargs):
        """ Copy local file to remote location.
        """
        _ = kwargs
        try:
            ret = False
            localFlag = self.isLocal(remote)
            #
            if localFlag:
                rPath = self.getFilePath(remote)
                lPath = self.getFilePath(local)
                shutil.copyfile(lPath, rPath)
                ret = True
            else:
                ret = False
        except Exception as e:
            logger.exception("For remote %r local %r failing with %s", remote, local, str(e))
            ret = False
        return ret

    def getFilePath(self, locator):
        try:
            locSp = urlsplit(locator)
            return locSp.path
        except Exception as e:
            logger.exception("For locator %r failing with %s", locator, str(e))
        return None

    def getFileName(self, locator):
        try:
            locSp = urlsplit(locator)
            (_, fn) = os.path.split(locSp.path)
            return fn
        except Exception as e:
            logger.exception("For locator %r failing with %s", locator, str(e))
        return None

    def isLocal(self, locator):
        try:
            locSp = urlsplit(locator)
            return locSp.scheme in ["", "file"]
        except Exception as e:
            logger.exception("For locator %r failing with %s", locator, str(e))
        return None

    def getScheme(self, locator):
        try:
            locSp = urlsplit(locator)
            return locSp.scheme
        except Exception as e:
            logger.exception("For locator %r Failing with %s", locator, str(e))
        return None

    def exists(self, filePath, mode=os.R_OK):
        try:
            return os.access(filePath, mode)
        except Exception:
            return False

    def __unbundle(self, tarFilePath, dirPath="."):
        #   import tarfile contents into dirPath -
        with tarfile.open(tarFilePath) as tar:
            tar.extractall(path=dirPath)

    def __extractTarMember(self, tarFilePath, memberName, memberPath):
        try:
            with tarfile.open(tarFilePath) as tar:
                fIn = tar.extractfile(memberName)
                with open(memberPath, "wb") as ofh:
                    ofh.write(fIn.read())
            ret = True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ret = False
        return ret

    @retry((myurl.URLError, myurl.HTTPError), maxAttempts=3, delaySeconds=3, multiplier=2, defaultValue=False, logger=logger)
    def __fetchUrl(self, url, filePath):
        try:
            with open(filePath, "wb") as outFile:
                with contextlib.closing(myurl.urlopen(url)) as fp:
                    blockSize = 1024 * 8
                    while True:
                        block = fp.read(blockSize)  # pylint: disable=no-member
                        if not block:
                            break
                        outFile.write(block)
            return True
        except Exception as e:
            logger.error("Failing for %s with %s", filePath, str(e))
            raise e

        return False
