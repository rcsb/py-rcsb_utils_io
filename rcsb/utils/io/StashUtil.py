##
# File: StashUtil.py
#
# Utilities to stash and recover a data in collection of directories to and from
# remote sftp, http or local POSIX file storage resources.
#
# Updates:
# 19-Jul-2021 jdw add git push support
#
##

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os

from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.GitUtil import GitUtil
from rcsb.utils.io.SftpUtil import SftpUtil
from rcsb.utils.io.SplitJoin import SplitJoin

logger = logging.getLogger(__name__)


class StashUtil(object):
    """Utilities to stash and recover a data in collection of (sub)directories to/from
    remote sftp, http or local POSIX file storage resources.
    """

    def __init__(self, localBundlePath, baseBundleFileName):
        """Set the bundle file name and path for class instance.

        Args:
            localBundlePath (str): writeable local path for bundle file artifact
            baseBundleFileName (str): bundle file name without file extension
        """
        #
        self.__localBundlePath = localBundlePath
        self.__baseBundleName = baseBundleFileName
        self.__baseBundleFileName = self.__baseBundleName + ".tar.gz"
        self.__localStashTarFilePath = os.path.join(localBundlePath, self.__baseBundleFileName)

    def makeBundle(self, localParentPath, subDirList):
        """Bundle the subdirectories of the input parent directory path.

        Args:
            localParentPath (str): local parent directory path containing the bundling targets
            subDirList (list, str): list of subdirectories of the parent path to be bundled

        Returns:
            (bool): True for success or False otherwise
        """
        fileU = FileUtil()
        fileU.mkdir(self.__localBundlePath)
        dirPathList = [os.path.join(localParentPath, subDir) for subDir in subDirList]
        okT = fileU.bundleTarfile(self.__localStashTarFilePath, dirPathList, mode="w:gz", recursive=True)
        return okT

    def storeBundle(self, url, remoteDirPath, remoteStashPrefix="A", userName=None, password=None):
        """Store a copy of the bundled search dependencies remotely -

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
                if fileU.exists(remotePath):
                    ok = fileU.get(remotePath, self.__localStashTarFilePath)
                else:
                    ok = False
                    logger.warning("Missing bundle file %r", remotePath)

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

    def pushBundle(self, gitRepositoryPath, accessToken, gitHost="github.com", gitBranch="master", remoteStashPrefix="A", maxSizeMB=95):
        """Push bundle to remote stash git repository.

        Args:
            gitRepositoryPath (str): git repository path (e.g., rcsb/py-rcsb_exdb_assets_stash)
            accessToken (str): git repository access token
            gitHost (str, optional): git repository host name. Defaults to github.com.
            gitBranch (str, optional): git branch name. Defaults to master.
            remoteStashPrefix (str, optional): optional label preppended to the stashed dependency bundle artifact (default='A')
            maxSizeMB (int, optional): maximum stash bundle file size that will be committed. Defaults to 95MB.

        Returns:
          bool:  True for success or False otherwise

        """
        try:
            ok = False
            gU = GitUtil(token=accessToken, repositoryHost=gitHost)
            fU = FileUtil()
            localRepositoryPath = os.path.join(self.__localBundlePath, "stash_repository")
            fn = self.__makeBundleFileName(self.__baseBundleFileName, remoteStashPrefix=remoteStashPrefix)
            #
            # Update existing local repository, otherwise clone a new copy
            if fU.exists(localRepositoryPath):
                ok = gU.pull(localRepositoryPath, branch=gitBranch)
                logger.debug("After pull status %r", gU.status(localRepositoryPath))
            else:
                ok = gU.clone(gitRepositoryPath, localRepositoryPath, branch=gitBranch)
            #
            # Split all bundles
            mbSize = float(fU.size(self.__localStashTarFilePath)) / 1000000.0
            logger.info("Splitting bundle %r (%.3f MB/Max %d MB)", fn, mbSize, maxSizeMB)
            sj = SplitJoin()
            splitDirPath = os.path.join(localRepositoryPath, "stash", fn[:-7])
            sj.split(self.__localStashTarFilePath, splitDirPath, maxSizeMB=maxSizeMB)
            fU.remove(self.__localStashTarFilePath)
            # else:
            # fU.put(self.__localStashTarFilePath, os.path.join(localRepositoryPath, "stash", fn))

            ok = gU.addAll(localRepositoryPath, branch=gitBranch)
            ok = gU.commit(localRepositoryPath, branch=gitBranch)
            logger.debug("After commit status %r", gU.status(localRepositoryPath))
            #
            if accessToken:
                ok = gU.push(localRepositoryPath, branch=gitBranch)
                logger.info("After push status %r", gU.status(localRepositoryPath))
            #
            return ok
        except Exception as e:
            logger.exception("For %r %r failing with %s", gitHost, gitRepositoryPath, str(e))
        return False

    def fetchPartitionedBundle(self, localRestoreDirPath, gitRepositoryPath, gitRawHost="raw.githubusercontent.com", gitBranch="master", remoteStashPrefix="A"):
        """Fetch bundle from a remote stash public git repository via http.

        Args:
            localRestoreDirPath (str): local restore path
            gitRepositoryPath (str): git repository path (e.g., rcsb/py-rcsb_exdb_assets_stash)
            gitHost (str, optional): git repository host name. Defaults to github.com.
            gitBranch (str, optional): git branch name. Defaults to master.
            remoteStashPrefix (str, optional): optional label preppended to the stashed dependency bundle artifact (default='A')

        Returns:
          bool:  True for success or False otherwise

            https://raw.githubusercontent.com/rcsb/py-rcsb_exdb_assets_stash/master/stash/<file_or_dir>
        """
        try:
            ok = False
            fileU = FileUtil()
            bundleFileName = self.__makeBundleFileName(self.__baseBundleFileName, remoteStashPrefix=remoteStashPrefix)
            urlBase = "https://" + gitRawHost
            rp = gitRepositoryPath[:-4] if gitRepositoryPath.endswith(".git") else gitRepositoryPath
            repoDirPath = os.path.join(urlBase, rp, gitBranch, "stash")

            # First fetch the manifest file
            remoteDirPath = os.path.join(repoDirPath, bundleFileName[:-7])
            remotePath = os.path.join(remoteDirPath, "MANIFEST")
            logger.debug("Manifest remote %r", remotePath)
            #
            localDirPath = os.path.join(self.__localBundlePath, bundleFileName[:-7])
            manifestPath = os.path.join(localDirPath, "MANIFEST")

            ok = fileU.get(remotePath, manifestPath)
            if not ok:
                logger.error("No manifest file at %r", remotePath)
                return ok
            # ---
            partFileName = "part_1"
            remotePartPath = os.path.join(repoDirPath, bundleFileName[:-7], partFileName)
            logger.debug("remotePartPath %r", remotePartPath)
            # ---
            partList = []
            with open(manifestPath, "r") as mfh:
                line = mfh.readline()
                tf, myHash = line[:-1].split("\t")
                logger.debug("Fetched manifest for %s hash %r", tf, myHash)
                for line in mfh:
                    partList.append(line[:-1])
            #
            logger.debug("Parts (%d) %r", len(partList), partList)
            for part in partList:
                localPath = os.path.join(localDirPath, part)
                remotePath = os.path.join(repoDirPath, bundleFileName[:-7], part)
                logger.debug("%r %r", remotePath, localPath)
                fileU.get(remotePath, localPath)
            #
            sj = SplitJoin()
            ok = sj.join(self.__localStashTarFilePath, localDirPath)
            if ok:
                ok = fileU.unbundleTarfile(self.__localStashTarFilePath, dirPath=localRestoreDirPath)
            return ok
        except Exception as e:
            logger.exception("Failing for %r with %s", bundleFileName, str(e))
            ok = False
        return ok

    def __makeBundleFileName(self, baseBundleFileName, remoteStashPrefix="A"):
        fn = baseBundleFileName
        try:
            fn = "%s-%s" % (remoteStashPrefix.upper(), baseBundleFileName) if remoteStashPrefix else baseBundleFileName
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return fn
