##
# File: StashUtil.py
#
# Utilities to stash and recover a data in collection of directories to and from
# remote sftp, http or local POSIX file storage resources.
#
# Updates:
#
##

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os

from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.SftpUtil import SftpUtil

logger = logging.getLogger(__name__)


class StashUtil(object):
    """ Utilities to stash and recover a data in collection of (sub)directories to/from
        remote sftp, http or local POSIX file storage resources.
    """

    def __init__(self, localBundlePath, baseBundleFileName):
        """Set the bundle file name and path for class instance.

        Args:
            localBundlePath (str): writeable local path for bundle file artifact
            baseBundleFileName (str): bundle file name without file extension
        """
        #
        fn = baseBundleFileName
        self.__baseBundleFileName = fn + ".tar.gz"
        self.__localStashTarFilePath = os.path.join(localBundlePath, self.__baseBundleFileName)

    def makeBundle(self, localParentPath, subDirList):
        """ Bundle the subdirectories of the input parent directory path.

        Args:
            localParentPath (str): local parent directory path containing the bundling targets
            subDirList (list, str): list of subdirectories of the parent path to be bundled

        Returns:
            (bool): True for success or False otherwise
        """
        fileU = FileUtil()
        dirPathList = [os.path.join(localParentPath, subDir) for subDir in subDirList]
        okT = fileU.bundleTarfile(self.__localStashTarFilePath, dirPathList, mode="w:gz", recursive=True)
        return okT

    def storeBundle(self, url, remoteDirPath, remoteStashPrefix="A", userName=None, password=None):
        """ Store a copy of the bundled search dependencies remotely -

        Args:
            url (str): URL string for the destination host (e.g. sftp://myserver.net or None for a local file)
            remoteDirPath (str): remote directory path on the remote resource
            remoteStashPrefix (str, optional): optional label preppended to the stashed dependency bundle artifact (default='A')
            userName (str, optional): optional access information. Defaults to None.
            password (str, optional): optional access information. Defaults to None.

        Returns:
          bool:  True for success or False otherwise

        """
        try:
            ok = False
            fn = self.__makeBundleFileName(self.__baseBundleFileName, remoteStashPrefix=remoteStashPrefix)
            if url and url.startswith("sftp://"):
                sftpU = SftpUtil()
                hostName = url[7:]
                ok = sftpU.connect(hostName, userName, pw=password, port=22)
                if ok:
                    remotePath = os.path.join("/", remoteDirPath, fn)
                    ok = sftpU.put(self.__localStashTarFilePath, remotePath)
            elif not url:
                fileU = FileUtil()
                remotePath = os.path.join(remoteDirPath, fn)
                ok = fileU.put(self.__localStashTarFilePath, remotePath)
            else:
                logger.error("Unsupported stash protocol %r", url)
            return ok
        except Exception as e:
            logger.exception("For %r %r failing with %s", url, remoteDirPath, str(e))
        return False

    def fetchBundle(self, localRestoreDirPath, url, remoteDirPath, remoteStashPrefix="A", userName=None, password=None):
        """Restore bundled dependencies from remote storage and unbundle these in the
           current local cache directory.

        Args:
            localRestoreDirPath (str): local restore path
            url (str): remote URL
            remoteDirPath (str): remote directory path on the remote resource
            remoteStashPrefix (str, optional): optional label preppended to the stashed dependency bundle artifact (default='A')
            userName (str, optional): optional access information. Defaults to None.
            password (str, optional): optional access information. Defaults to None.
        """
        try:
            ok = False
            fileU = FileUtil()
            fn = self.__makeBundleFileName(self.__baseBundleFileName, remoteStashPrefix=remoteStashPrefix)
            if not url:
                remotePath = os.path.join(remoteDirPath, fn)
                ok = fileU.get(remotePath, self.__localStashTarFilePath)

            elif url and (url.startswith("http://") or url.startswith("https://")):
                remotePath = url + os.path.join("/", remoteDirPath, fn)
                ok = fileU.get(remotePath, self.__localStashTarFilePath)

            elif url and url.startswith("sftp://"):
                sftpU = SftpUtil()
                ok = sftpU.connect(url[7:], userName, pw=password, port=22)
                if ok:
                    remotePath = os.path.join(remoteDirPath, fn)
                    ok = sftpU.get(remotePath, self.__localStashTarFilePath)
            else:
                logger.error("Unsupported protocol %r", url)
            if ok:
                ok = fileU.unbundleTarfile(self.__localStashTarFilePath, dirPath=localRestoreDirPath)
            return ok
        except Exception as e:
            logger.exception("For %r %r Failing with %s", url, remoteDirPath, str(e))
            ok = False
        return ok

    def __makeBundleFileName(self, baseBundleFileName, remoteStashPrefix="A"):
        fn = baseBundleFileName
        try:
            fn = "%s-%s" % (remoteStashPrefix.upper(), baseBundleFileName) if remoteStashPrefix else baseBundleFileName
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return fn
