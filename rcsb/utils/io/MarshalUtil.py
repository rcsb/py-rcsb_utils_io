##
# File: MarshalUtil.py
# Date: 4-Jun-2018
#
# Updates:
#      19-Jun-2018 jdw propagate the class workpath to serialize/deserialize methods explicitly
#       6-Mar-2019 jdw add previously stubbed remote access and tar file member support
#       9-Mar-2019 jdw add exists()
#
# For py 27 pip install backports.tempfile
##
# pylint: disable=all
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import sys

from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.IoUtil import IoUtil

if sys.version_info[0] == 2:
    from backports import tempfile
else:
    import tempfile


logger = logging.getLogger(__name__)


class MarshalUtil(object):
    """
    """

    def __init__(self, **kwargs):
        self.__workPath = kwargs.get("workPath", ".")
        self.__workDirSuffix = kwargs.get("workDirSuffix", "marshall_")
        self.__workDirPrefix = kwargs.get("workDirSuffix", "_tempdir")
        #
        self.__fileU = FileUtil(workPath=self.__workPath)
        self.__ioU = IoUtil()

    def doExport(self, locator, obj, fmt="list", marshalHelper=None, **kwargs):
        """
        """
        try:
            ret = False
            cacheLocalFlag = kwargs.get("cacheLocal", False)
            localFlag = self.__fileU.isLocal(locator)
            if marshalHelper:
                myObj = marshalHelper(obj, **kwargs)
            else:
                myObj = obj
            #
            if localFlag and not cacheLocalFlag:
                localFilePath = self.__fileU.getFilePath(locator)
                ret = self.__ioU.serialize(localFilePath, myObj, fmt=fmt, workPath=self.__workPath, **kwargs)
            else:
                with tempfile.TemporaryDirectory(suffix=self.__workDirSuffix, prefix=self.__workDirPrefix, dir=self.__workPath) as tmpDirName:
                    # write a local copy then copy to destination -
                    #
                    localFilePath = os.path.join(self.__workPath, tmpDirName, self.__fileU.getFileName(locator))
                    ok1 = self.__ioU.serialize(localFilePath, myObj, fmt=fmt, workPath=self.__workPath, **kwargs)
                    ok2 = True
                    if ok1:
                        ok2 = self.__fileU.put(localFilePath, locator, **kwargs)
                ret = ok1 and ok2
        except Exception as e:
            logger.exception("Exporting locator %r failing with %s", locator, str(e))

        return ret

    def doImport(self, locator, fmt="list", marshalHelper=None, **kwargs):
        """[summary]

        Args:
            locator (str): [description]
            fmt (str, optional): [description]. Defaults to "list".
            marshalHelper (object, optional): [description]. Defaults to None.

        Returns:
            Any: format specific return type
        """
        try:
            cacheLocalFlag = kwargs.get("cacheLocal", False)
            tarMember = kwargs.get("tarMember", None)
            localFlag = self.__fileU.isLocal(locator) and not tarMember
            #
            if localFlag and not cacheLocalFlag:
                filePath = self.__fileU.getFilePath(locator)
                ret = self.__ioU.deserialize(filePath, fmt=fmt, workPath=self.__workPath, **kwargs)
            else:
                #
                with tempfile.TemporaryDirectory(suffix=self.__workDirSuffix, prefix=self.__workDirPrefix, dir=self.__workPath) as tmpDirName:
                    #
                    # Fetch first then read a local copy -
                    #
                    if tarMember:
                        localFilePath = os.path.join(self.__workPath, tmpDirName, tarMember)
                    else:
                        localFilePath = os.path.join(self.__workPath, tmpDirName, self.__fileU.getFileName(locator))
                    #
                    self.__fileU.get(locator, localFilePath, **kwargs)
                    ret = self.__ioU.deserialize(localFilePath, fmt=fmt, workPath=self.__workPath, **kwargs)

            if marshalHelper:
                ret = marshalHelper(ret, **kwargs)
        except Exception as e:
            logger.exception("Importing locator %r failing with %s", locator, str(e))
            ret = None
        return ret

    def exists(self, filePath, mode=os.R_OK):
        return self.__ioU.exists(filePath, mode=mode)
