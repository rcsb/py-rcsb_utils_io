##
# File:    FtpUtil.py
# Author:  dwp
# Date:    3-Aug-2021
#
# Updates:
#
##
"""
Class providing essential data transfer operations for FTP protocol.
"""

__docformat__ = "google en"
__author__ = "Dennis Piehl"
__email__ = "dennis.piehl@rcsb.org"
__license__ = "Apache 2.0"

#
import logging
import os
import ftplib

from rcsb.utils.io.FileUtil import FileUtil

logger = logging.getLogger(__name__)


class FtpUtil(object):
    """Class providing essential data transfer operations for FTP protocol"""

    def __init__(self, *args, **kwargs):
        _ = args
        _ = kwargs
        self.__ftpClient = None
        self.__context = None
        self.__raiseExceptions = False
        #

    # def getRootPath(self):
    #    return self._rootPath

    def connect(self, hostName, userName, pw=None, keyFilePath=None, certFilePath=None, certFilePw=None):

        try:
            self.__ftpClient = self.__makeFtpClient(hostName=hostName, userName=userName, pw=pw, keyFilePath=keyFilePath, certFilePath=certFilePath, certFilePw=certFilePw)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("Failing connect for hostname %s with %s", hostName, str(e))
                return False

    def __makeFtpClient(self, hostName, userName, pw=None, keyFilePath=None, certFilePath=None, certFilePw=None):
        """
        Make FTP client connected to the supplied host on the supplied port authenticating as the user with
        supplied username and supplied password or with the private key in a file with the supplied path.

        :rtype: ftplib FTP object.

        """
        ftp = None
        self.__context = None
        try:
            if certFilePath is not None:
                # Create SSLContext object
                self.__context = ftplib.ssl.SSLContext()

                # Load the certificate and key (if provided) into the context object
                self.__context.load_cert_chain(certfile=certFilePath, keyfile=keyFilePath, password=certFilePw)

                # Connect via FTP_TLS using supplied method of authentication.
                ftp = ftplib.FTP_TLS(host=hostName, user=userName, passwd=pw, context=self.__context) # For TLS with certificate, host and user may need to be set to empty '' or None
            else:
                # Connect via FTP using username and password authentication
                ftp = ftplib.FTP(host=hostName, user=userName, passwd=pw)

            return ftp
        except Exception as e:
            logger.error("Error occurred creating FTP client: %s: %s", e.__class__, str(e))
            if ftp is not None:
                ftp.close()
            if self.__raiseExceptions:
                raise e

    def mkdir(self, path):
        try:
            self.__ftpClient.mkd(path)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("mkdir failing for path %s with %s", path, str(e))
                return False

    def stat(self, path):
        """ftp stat attributes for a given file or directory path (e.g. ["type", "size", "perm"]).
        Only works if the FTP server supports MLSD (RFC 3659).
        """
        try:
            dD = {}
            for name, facts in self.__ftpClient.mlsd(path):
                dD.update({name: facts})
            return dD
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("stat failing for path %s with %s", path, str(e))
                return {}

    def put(self, localPath, remotePath):
        """Put a local file on a remote FTP server.

        Arguments:
            localPath (str): local file path
            remotePath (str): remote file path

        Returns:
            bool: True for success or false otherwise
        """
        try:
            fileU = FileUtil()
            remotePathDir = fileU.getFilePath(remotePath)
            self.mkdir(remotePathDir)
            if (os.path.exists(remotePath) and os.path.isdir(remotePath)): # If provided remotePath already exists and is a directory, put the file on the remote server using the local filename to avoid unintentionally overwriting an entire remote directory with a single file
                localFileName = FileUtil().getFileName(localPath)
                remoteFilePath = os.path.join(remotePath, localFileName)
            else:
                remoteFilePath = remotePath
            with open(localPath, 'rb') as lFP:
                self.__ftpClient.storbinary('STOR %s' % remoteFilePath, lFP)
            if remoteFilePath in self.listdir(remotePathDir):
                return True
            else:
                logger.error("put failing for localPath %s remoteFilePath %s", localPath, remoteFilePath)
                return False
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
            if (os.path.exists(localPath) and os.path.isdir(localPath)): # If provided localPath already exists and is a directory, retrieve the file using the name on the remote server to avoid unintentionally overwriting an entire local directory with a single retrieved file
                remoteFileName = FileUtil().getFileName(remotePath)
                localFilePath = os.path.join(localPath, remoteFileName)
            else:
                localFilePath = localPath
            with open(localFilePath, 'wb') as lFP:
                self.__ftpClient.retrbinary('RETR %s' % remotePath, lFP.write)
            ok = fileU.exists(localFilePath)
            if ok:
                return True
            else:
                logger.error("get failing for remotePath %s localFilePath %s", remotePath, localFilePath)
                return False
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("get failing for remotePath %s localPath %s with %s", remotePath, localPath, str(e))
                return False

    def listdir(self, path):
        """Return a flat list of all files and directories (as full path names) for a given directory.

        E.g., for path='/pub/pdb/data', returns ['/pub/pdb/data/.', '/pub/pdb/data/..', '/pub/pdb/data/biounit', '/pub/pdb/data/bird', '/pub/pdb/data/component-models', '/pub/pdb/data/monomers', '/pub/pdb/data/status', '/pub/pdb/data/structures']

        Note that not all FTP servers allow the checking of specific file existence, so must provide directory path as input.
        """
        try:
            return self.__ftpClient.nlst(path)
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("listdir failing for path %s with %s", path, str(e))
                return False

    def rmdir(self, dirPath):
        try:
            self.__ftpClient.rmd(dirPath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("rmdir failing for path %s with %s", dirPath, str(e))
                return False

    def remove(self, filePath):
        try:
            self.__ftpClient.delete(filePath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("remove failing for path %s with %s", filePath, str(e))
                return False

    def close(self):
        try:
            if self.__ftpClient is not None:
                self.__ftpClient.close()
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("Close failing with %s", str(e))
