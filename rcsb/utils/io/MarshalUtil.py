##
# File: MarshalUtil.py
# Date: 4-Jun-2018
#
# Updates:
#      19-Jun-2018 jdw propagate the class workpath to serialize/deserialize methods explicitly
#       6-Mar-2019 jdw add previously stubbed remote access and tar file member support
#       9-Mar-2019 jdw add exists()
#      13-Aug-2019 jdw add multipart support for json/pickle
#       5-Dec-2023 dwp add support for BCIF import and export
#
##
# pylint: disable=all
__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import tempfile

from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.IoUtil import IoUtil


logger = logging.getLogger(__name__)


class MarshalUtil(object):
    """Wrapper for serialization and deserialization methods."""

    def __init__(self, workPath=None, dictionaryApi=None, dictFilePathL=None, **kwargs):
        """Initialize MarshalUtil object.

        Args:
            workPath (str, optional): Directory to work in. Defaults to current working directory.
            dictionaryApi (obj, optional): DictionaryApi instance to use for BCIF encoding (when trying to export BCIF files).
                                           Defaults to None, in which case it will try to create one using 'dictFilePathL'.
            dictFilePathL (str, optional): List of dictionary files to use for BCIF encoding. Not needed if 'dictionaryApi' object is provided.
                                           Defaults to latest version of 'mmcif_pdbx_v5_next.dic'.
        """
        self.__workPath = workPath if workPath else "."
        self.__workDirSuffix = kwargs.get("workDirSuffix", "marshall_")
        self.__workDirPrefix = kwargs.get("workDirSuffix", "_tempdir")
        self.__dictionaryApi = dictionaryApi
        self.__dictFilePathL = dictFilePathL if dictFilePathL else ["https://raw.githubusercontent.com/wwpdb-dictionaries/mmcif_pdbx/master/dist/mmcif_pdbx_v5_next.dic"]
        #
        self.__fileU = FileUtil(workPath=self.__workPath)
        self.__ioU = IoUtil(dictFilePathL=self.__dictFilePathL, dictionaryApi=self.__dictionaryApi)

    def doExport(self, locator, obj, fmt="list", marshalHelper=None, numParts=None, **kwargs):
        """Serialize the input object at locator path in specified format.  The
        input object is optionally preprocessed by the helper method.

        Args:
            locator (str): target path or URI
            obj (object): data to be serialized
            fmt (str, optional): format for serialization (mmcif, bcif, tdd, csv, list). Defaults to "list".
            marshalHelper (method, optional): pre-processor method applied to input data object. Defaults to None.
            numParts (int, optional): serialize the data in parts. Defaults to None. (json and pickle formats)
        Returns:
            bool: True for sucess or False otherwise
        """
        try:
            ret = False
            localFlag = self.__fileU.isLocal(locator)
            if marshalHelper:
                myObj = marshalHelper(obj, **kwargs)
            else:
                myObj = obj
            #
            if localFlag and numParts and fmt in ["json", "pickle"]:
                localFilePath = self.__fileU.getFilePath(locator)
                ret = self.__ioU.serializeInParts(localFilePath, myObj, numParts, fmt=fmt, **kwargs)
            elif localFlag:
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

    def doImport(self, locator, fmt="list", marshalHelper=None, numParts=None, **kwargs):
        """Deserialize data at the target locator in specified format. The deserialized
        data is optionally post-processed by the input helper method.

        Args:
            locator (str): path or URI to input data
            fmt (str, optional): format for deserialization (mmcif, bcif, tdd, csv, list). Defaults to "list".
            marshalHelper (method, optional): post-processor method applied to deserialized data object. Defaults to None.
            numParts (int, optional): deserialize the data in parts. Defaults to None. (json and pickle formats)
            tarMember (str, optional): name of a member of tar file bundle. Defaults to None. (tar file format)

        Returns:
            Any: format specific return type
        """
        try:
            tarMember = kwargs.get("tarMember", None)
            localFlag = self.__fileU.isLocal(locator) and not tarMember
            #
            if localFlag and numParts and fmt in ["json", "pickle"]:
                filePath = self.__fileU.getFilePath(locator)
                ret = self.__ioU.deserializeInParts(filePath, numParts, fmt=fmt, **kwargs)
            elif localFlag:
                filePath = self.__fileU.getFilePath(locator)
                ret = self.__ioU.deserialize(filePath, fmt=fmt, workPath=self.__workPath, **kwargs)
            else:
                #
                if fmt in ["mmcif", "bcif"]:
                    ret = self.__ioU.deserialize(locator, fmt=fmt, workPath=self.__workPath, **kwargs)
                else:
                    with tempfile.TemporaryDirectory(suffix=self.__workDirSuffix, prefix=self.__workDirPrefix, dir=self.__workPath) as tmpDirName:
                        #
                        # Fetch first then read a local copy -
                        #
                        if tarMember:
                            localFilePath = os.path.join(self.__workPath, tmpDirName, tarMember)
                        else:
                            localFilePath = os.path.join(self.__workPath, tmpDirName, self.__fileU.getFileName(locator))

                        # ---  Local copy approach ---
                        self.__fileU.get(locator, localFilePath, **kwargs)
                        ret = self.__ioU.deserialize(localFilePath, fmt=fmt, workPath=self.__workPath, **kwargs)

            if marshalHelper:
                ret = marshalHelper(ret, **kwargs)
        except Exception as e:
            logger.exception("Importing locator %r failing with %s", locator, str(e))
            ret = None
        return ret

    def exists(self, filePath, mode=os.R_OK):
        return self.__fileU.exists(filePath, mode=mode)

    def mkdir(self, dirPath, mode=0o755):
        return self.__fileU.mkdir(dirPath, mode=mode)

    def remove(self, pth):
        return self.__fileU.remove(pth)
