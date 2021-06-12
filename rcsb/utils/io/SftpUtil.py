##
# File:    SftpUtil.py
# Author:  jdw
# Date:    5-Jun-2020
#
# Updates:
#
##
"""
Class providing essential data transfer operations for SFTP protocol.
"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

#
import logging

import paramiko

from rcsb.utils.io.FileUtil import FileUtil

logger = logging.getLogger(__name__)


class SftpUtil(object):
    """Class providing essential data transfer operations for SFTP protocol"""

    def __init__(self, *args, **kwargs):
        _ = args
        _ = kwargs
        self.__sftpClient = None
        self.__transport = None
        self.__raiseExceptions = False
        #

    # def getRootPath(self):
    #    return self._rootPath

    def connect(self, hostName, userName, pw=None, port=22, keyFilePath=None, keyFileType="RSA"):

        try:
            self.__sftpClient = self.__makeSftpClient(hostName=hostName, port=port, userName=userName, pw=pw, keyFilePath=keyFilePath, keyFileType=keyFileType)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("Failing connect for hostname %s with %s", hostName, str(e))
                return False

    def __makeSftpClient(self, hostName, port, userName, pw=None, keyFilePath=None, keyFileType="RSA"):
        """
        Make SFTP client connected to the supplied host on the supplied port authenticating as the user with
        supplied username and supplied password or with the private key in a file with the supplied path.
        If a private key is used for authentication, the type of the keyfile needs to be specified as DSA or RSA.

        :rtype: Paramiko SFTPClient object.

        """
        sftp = None
        key = None
        self.__transport = None
        try:
            if keyFilePath is not None:
                # Get private key used to authenticate user.
                if keyFileType == "DSA":
                    # The private key is a DSA type key.
                    key = paramiko.DSSKey.from_private_key_file(keyFilePath)
                else:
                    # The private key is a RSA type key.
                    key = paramiko.RSAKey.from_private_key_file(keyFilePath)

            # Create Transport object using supplied method of authentication.
            self.__transport = paramiko.Transport((hostName, port))
            if pw is not None:
                self.__transport.connect(username=userName, password=pw)
            else:
                self.__transport.connect(username=userName, pkey=key)

            sftp = paramiko.SFTPClient.from_transport(self.__transport)

            return sftp
        except Exception as e:
            logger.error("Error occurred creating SFTP client: %s: %s", e.__class__, str(e))
            if sftp is not None:
                sftp.close()
            if self.__transport is not None:
                self.__transport.close()
            if self.__raiseExceptions:
                raise e

    def mkdir(self, path, mode=511):

        try:
            self.__sftpClient.mkdir(path, mode)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("mkdir failing for path %s with %s", path, str(e))
                return False

    def stat(self, path):
        """sftp  stat attributes  = [ size=17 uid=0 gid=0 mode=040755 atime=1507723473 mtime=1506956503 ]"""
        try:
            sT = self.__sftpClient.stat(path)
            dD = {"mtime": sT.st_mtime, "size": sT.st_size, "mode": sT.st_mode, "uid": sT.st_uid, "gid": sT.st_gid, "atime": sT.st_atime}
            return dD
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("stat failing for path %s with %s", path, str(e))
                return {}

    def put(self, localPath, remotePath):
        try:
            self.__sftpClient.put(localPath, remotePath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("put failing for localPath %s  remotePath %s with %s", localPath, remotePath, str(e))
                return False

    def get(self, remotePath, localPath):
        try:
            fileU = FileUtil()
            fileU.mkdirForFile(localPath)
            self.__sftpClient.get(remotePath, localPath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("get failing for remotePath %s localPath %s with %s", remotePath, localPath, str(e))
                return False

    def listdir(self, path):
        try:
            return self.__sftpClient.listdir(path)
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("listdir failing for path %s with %s", path, str(e))
                return False

    def rmdir(self, dirPath):
        try:
            self.__sftpClient.rmdir(dirPath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("rmdir failing for path %s with %s", dirPath, str(e))
                return False

    def remove(self, filePath):
        try:
            self.__sftpClient.remove(filePath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("remove failing for path %s with %s", filePath, str(e))
                return False

    def close(self):
        try:
            if self.__sftpClient is not None:
                self.__sftpClient.close()
            if self.__transport is not None:
                self.__transport.close()

            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("Close failing with %s", str(e))
