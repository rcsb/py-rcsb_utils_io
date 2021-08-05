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

    def connect(self, hostName, userName="anonymous", pw=None, keyFilePath=None, certFilePath=None, certFilePw=None):
        """Establish a connection to an FTP server, using ftplib (https://docs.python.org/3/library/ftplib.html).

        Arguments:
            hostName (str): hostname of FTP server (e.g., 'ftp.rcsb.org')
            userName (str): username to login with
            pw (str): password to login with (if required)
            keyFilePath (str): path to a file containing the private SSL key (for TLS connections)
            certFilePath (str): "path to a single file in PEM format containing the certificate as
                                well as any number of CA certificates needed to establish the
                                certificate’s authenticity" (for TLS connections)
                                (https://docs.python.org/3/library/ssl.html)
            certFilePw (str): password to access the certificate file (if required)

        Returns:
            bool: True for success or false otherwise
        """
        try:
            self.__ftpClient = self.__makeFtpClient(hostName=hostName, userName=userName, pw=pw, keyFilePath=keyFilePath, certFilePath=certFilePath, certFilePw=certFilePw)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("Failing connect for hostname %s with %s", hostName, str(e))
                return False

    def __makeFtpClient(self, hostName, userName="anonymous", pw=None, keyFilePath=None, certFilePath=None, certFilePw=None):
        """
        Make an FTP client connected to the specified host using provided authentication parameters
        (username and password for standard FTP connection, and/or certificate and private key files for FTP_TLS connection).

        Arguments:
            hostName (str): hostname of FTP server (e.g., 'ftp.rcsb.org')
            userName (str): username to login with
            pw (str): password to login with (if required)
            keyFilePath (str): path to a file containing the private SSL key (for TLS connections)
            certFilePath (str): "path to a single file in PEM format containing the certificate as
                                well as any number of CA certificates needed to establish the
                                certificate’s authenticity" (for TLS connections)
                                (https://docs.python.org/3/library/ssl.html)
            certFilePw (str): password to access the certificate file (if required)

        Returns:
            ftplib.FTP or ftplib.FTP_TLS:   ftplib FTP connection object, as either a standard FTP connection or with FTP_TLS
                                            (depending if an SSL certificate was provided for the connection or not).
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
                # For TLS with certificate, host and user may need to be set to empty string '' or None
                ftp = ftplib.FTP_TLS(host=hostName, user=userName, passwd=pw, context=self.__context)
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
        """Make a directory on a remote FTP server.

        Arguments:
            path (str): directory path

        Returns:
            bool: True for success or false otherwise
        """
        try:
            self.__ftpClient.mkd(path)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("mkdir failing for path %s with %s", path, str(e))
                return False

    def dirstat(self, path):
        """Return stat attributes for a given directory path (e.g. ["type", "size", "perm"]).

        Only works if the FTP server supports MLSD (RFC 3659), which not all servers support.
        For a guaranteed way of returning the size of a specific file, use the self.size() method instead.

        Arguments:
            path (str): remote directory path (NOT a file path)

        Returns:
            dict: Dictionary of files and their corresponding stat attributes.
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

    def size(self, filePath):
        """Return stat attributes for a given file (NOT directory) on a remote FTP server.

        Arguments:
            filePath (str): remote file path

        Returns:
            int: Size of the file in bytes, or None if unsuccessful
        """
        try:
            fSize = self.__ftpClient.size(filePath)
            return int(fSize)
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("stat failing for path %s with %s", filePath, str(e))
                return None

    def put(self, localPath, remotePath):
        """Put a local file on a remote FTP server.

        Arguments:
            localPath (str): local file path
            remotePath (str): remote file path

        Returns:
            bool: True for success or false otherwise
        """
        try:
            # First, make sure the provided localPath represents a file, not a directory
            if not os.path.isfile(localPath):
                logger.error("put failing for localPath %s - path must be to a specific file, not a directory.", localPath)
                return False

            fileU = FileUtil()
            remotePathDir = fileU.getFilePath(remotePath)
            self.mkdir(remotePathDir)
            # If provided remotePath already exists and is a directory, put the file on the remote server using the local filename
            # to avoid unintentionally overwriting an entire remote directory with a single file
            if (os.path.exists(remotePath) and os.path.isdir(remotePath)):
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
        """Get a file from a remote FTP server.

        Arguments:
            remotePath (str): remote file path
            localPath (str): local file path

        Returns:
            bool: True for success or false otherwise
        """
        try:
            fileU = FileUtil()
            fileU.mkdirForFile(localPath)
            # If provided localPath already exists and is a directory, retrieve the file using the name on the remote server
            # to avoid unintentionally overwriting an entire local directory with a single retrieved file
            if (os.path.exists(localPath) and os.path.isdir(localPath)):
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

        E.g., for path='/pub/pdb/data', returns ['/pub/pdb/data/.', '/pub/pdb/data/..', '/pub/pdb/data/biounit', '/pub/pdb/data/bird',
                                                '/pub/pdb/data/component-models', '/pub/pdb/data/monomers', '/pub/pdb/data/status', '/pub/pdb/data/structures']

        Note that not all FTP servers allow the checking of specific file existence, so must provide directory path as input.

        Arguments:
            path (str): directory path

        Returns:
            list: List of all files and directories (as full path names) for a given directory.

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
        """Remove a directory from a remote FTP server.

        Arguments:
            dirPath (str): remote directory path

        Returns:
            bool: True for success or false otherwise
        """
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
        """Remove a file from a remote FTP server.

        Arguments:
            filePath (str): remote file path

        Returns:
            bool: True for success or false otherwise
        """
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
        """Close a remote FTP connection.

        Returns:
            bool: True for success or false otherwise
        """
        try:
            if self.__ftpClient is not None:
                self.__ftpClient.close()
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            else:
                logger.error("Close failing with %s", str(e))
