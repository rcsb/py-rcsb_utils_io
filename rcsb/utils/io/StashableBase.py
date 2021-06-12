##
# File: StashableBase.py
#
# Base class template that implements a common pattern for to backup and restore
# cache directories to stash storage.
#
# Updates:
#
##

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import time

from rcsb.utils.io.StashUtil import StashUtil

logger = logging.getLogger(__name__)


class StashableBase(object):
    """Base class implementing a backup and restore methods for cache directories to/from stash storage."""

    def __init__(self, cachePath, dirNameL):
        """Methods implementing backup and restore operations to and from stash storage. Remote stash
        storage is defined using the standard configuration options. Primary and fallback stash servers
        are supported.

        Args:
            cachePath (str): path to directory containing cached directories
            dirNameL (list): list of target directory names in the cache directory for backup and restore operations
        """
        self.__cachePath = cachePath
        self.__dirNameL = dirNameL
        #

    def restore(self, cfgOb, configName):
        """Restore the target cache directory from stash storage.

        Args:
            cfgOb (obj): configuration object (ConfigUtil())
            configName (str): configuration section name

        Returns:
            bool: True for success or False otherwise
        """
        ok = False
        try:
            startTime = time.time()
            url = cfgOb.get("STASH_SERVER_URL", sectionName=configName)
            userName = cfgOb.get("_STASH_AUTH_USERNAME", sectionName=configName)
            password = cfgOb.get("_STASH_AUTH_PASSWORD", sectionName=configName)
            basePath = cfgOb.get("_STASH_SERVER_BASE_PATH", sectionName=configName)
            ok = self.__fromStash(url, basePath, userName=userName, password=password)
            logger.info("Restored %r data file from stash (%r)", self.__dirNameL, ok)
            if not ok:
                urlFallBack = cfgOb.get("STASH_SERVER_FALLBACK_URL", sectionName=configName)
                ok = self.__fromStash(urlFallBack, basePath, userName=userName, password=password)
                logger.info("Recovered %r data file from fallback stash (%r)", self.__dirNameL, ok)
            #
            logger.info("Completed recovery (%r) at %s (%.4f seconds)", ok, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), time.time() - startTime)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        #
        return ok

    def backup(self, cfgOb, configName):
        """Backup the target cache directory to stash storage.

        Args:
            cfgOb (obj): configuration object (ConfigUtil())
            configName (str): configuration section name

        Returns:
            bool: True for success or False otherwise
        """
        ok1 = ok2 = False
        try:
            startTime = time.time()
            userName = cfgOb.get("_STASH_AUTH_USERNAME", sectionName=configName)
            password = cfgOb.get("_STASH_AUTH_PASSWORD", sectionName=configName)
            basePath = cfgOb.get("_STASH_SERVER_BASE_PATH", sectionName=configName)
            url = cfgOb.get("STASH_SERVER_URL", sectionName=configName)
            urlFallBack = cfgOb.get("STASH_SERVER_FALLBACK_URL", sectionName=configName)
            ok1 = self.__toStash(url, basePath, userName=userName, password=password)
            ok2 = self.__toStash(urlFallBack, basePath, userName=userName, password=password)
            logger.info(
                "Completed backup for %r data (%r/%r) at %s (%.4f seconds)",
                self.__dirNameL,
                ok1,
                ok2,
                time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                time.time() - startTime,
            )
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return ok1 & ok2

    def __toStash(self, url, stashRemoteDirPath, userName=None, password=None, remoteStashPrefix=None):
        """Copy tar and gzipped bundled cache data to remote server/location.

        Args:
            url (str): server URL (e.g. sftp://hostname.domain) None for local host
            stashRemoteDirPath (str): path to target directory on remote server
            userName (str, optional): server username. Defaults to None.
            password (str, optional): server password. Defaults to None.
            remoteStashPrefix (str, optional): channel prefix. Defaults to None.

        Returns:
            (bool): True for success or False otherwise
        """
        ok = False
        try:
            stU = StashUtil(os.path.join(self.__cachePath, "stash"), self.__dirNameL[0])
            ok = stU.makeBundle(self.__cachePath, self.__dirNameL)
            if ok:
                ok = stU.storeBundle(url, stashRemoteDirPath, remoteStashPrefix=remoteStashPrefix, userName=userName, password=password)
        except Exception as e:
            logger.error("Failing with url %r stashDirPath %r: %s", url, stashRemoteDirPath, str(e))
        return ok

    def __fromStash(self, url, stashRemoteDirPath, userName=None, password=None, remoteStashPrefix=None):
        """Restore local cache from a tar and gzipped bundle to fetched from a remote server/location.

        Args:
            url (str): server URL (e.g. sftp://hostname.domain) None for local host
            stashRemoteDirPath (str): path to target directory on remote server
            userName (str, optional): server username. Defaults to None.
            password (str, optional): server password. Defaults to None.
            remoteStashPrefix (str, optional): channel prefix. Defaults to None.

        Returns:
            (bool): True for success or False otherwise
        """
        ok = False
        try:
            stU = StashUtil(os.path.join(self.__cachePath, "stash"), self.__dirNameL[0])
            ok = stU.fetchBundle(self.__cachePath, url, stashRemoteDirPath, remoteStashPrefix=remoteStashPrefix, userName=userName, password=password)
        except Exception as e:
            logger.error("Failing with url %r stashDirPath %r: %s", url, stashRemoteDirPath, str(e))
        return ok
