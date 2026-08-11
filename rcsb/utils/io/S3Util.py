##
# File:    S3Util.py
# Author:  Michael Trumbull
# Date:    10-Aug-2026
#
# Updates:
#
##
"""
Class providing essential data transfer operations for S3 compatible object storage (e.g. AWS S3, MinIO).
"""

__docformat__ = "google en"
__author__ = "Michael Trumbull"
__email__ = "michael.trumbull@rcsb.org"
__license__ = "Apache 2.0"

#
import logging
import os

import boto3

from rcsb.utils.io.FileUtil import FileUtil

logger = logging.getLogger(__name__)


class S3Util(object):
    """Class providing essential data transfer operations for S3 compatible object storage.

    The target bucket is provided as an s3 style URL (e.g. s3://my-bucket or s3://my-bucket/some/prefix).
    Endpoint and credentials default to the standard AWS environment variables:

        AWS_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY
        AWS_SESSION_TOKEN      (optional)
        AWS_DEFAULT_REGION     (optional)
        AWS_ENDPOINT_URL_S3 or AWS_ENDPOINT_URL  (required for MinIO and other non-AWS endpoints)
    """

    def __init__(self, url, endPointUrl=None, accessKey=None, secretKey=None, sessionToken=None, region=None, **kwargs):
        """Set the target bucket and connection details for this class instance.

        Args:
            url (str): s3 style URL (e.g. s3://my-bucket or s3://my-bucket/some/prefix)
            endPointUrl (str, optional): service endpoint (e.g. https://minio.rcsb.org). Defaults to environment setting.
            accessKey (str, optional): access key id. Defaults to environment setting.
            secretKey (str, optional): secret access key. Defaults to environment setting.
            sessionToken (str, optional): session token. Defaults to environment setting.
            region (str, optional): region name. Defaults to environment setting.
        """
        self.__raiseExceptions = kwargs.get("raiseExceptions", False)
        self.__s3Client = None
        #
        self.__bucketName, self.__keyPrefix = self._parseUrl(url)
        self.__endPointUrl = endPointUrl if endPointUrl else os.environ.get("AWS_ENDPOINT_URL_S3", os.environ.get("AWS_ENDPOINT_URL"))
        self.__accessKey = accessKey
        self.__secretKey = secretKey
        self.__sessionToken = sessionToken
        self.__region = region
        #

    @property
    def bucketName(self):
        """(str): target bucket name parsed from the input URL"""
        return self.__bucketName

    def connect(self):
        """Create an S3 client for the endpoint and credentials of this class instance.

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            self.__s3Client = boto3.client(
                "s3",
                endpoint_url=self.__endPointUrl if self.__endPointUrl else None,
                aws_access_key_id=self.__accessKey if self.__accessKey else None,
                aws_secret_access_key=self.__secretKey if self.__secretKey else None,
                aws_session_token=self.__sessionToken if self.__sessionToken else None,
                region_name=self.__region if self.__region else None,
            )
            logger.info("Connected S3 client for endPointUrl %r region %r", self.__endPointUrl, self.__region)
            return True
        except Exception as e:
            self.__s3Client = None
            if self.__raiseExceptions:
                raise e
            logger.error("Failing S3 connect for endPointUrl %r with %s", self.__endPointUrl, str(e))
            return False

    def put(self, localPath, objectKey):
        """Upload a local file to the input object key.

        Args:
            localPath (str): local source file path
            objectKey (str): target object key

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            if not self._checkClient("put", objectKey):
                return False
            logger.debug("Uploading %s to bucket %s key %s", localPath, self.__bucketName, objectKey)
            self.__s3Client.upload_file(localPath, self.__bucketName, objectKey)
            logger.info("Uploaded %s (%d bytes) to bucket %s key %s", localPath, os.path.getsize(localPath), self.__bucketName, objectKey)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("put failing for localPath %s bucket %s key %s with %s", localPath, self.__bucketName, objectKey, str(e))
            return False

    def get(self, objectKey, localPath):
        """Download the input object key to a local file path.

        Args:
            objectKey (str): source object key
            localPath (str): local destination file path

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            if not self._checkClient("get", objectKey):
                return False
            fileU = FileUtil()
            fileU.mkdirForFile(localPath)
            logger.debug("Downloading bucket %s key %s to %s", self.__bucketName, objectKey, localPath)
            self.__s3Client.download_file(self.__bucketName, objectKey, localPath)
            logger.info("Downloaded bucket %s key %s (%d bytes) to %s", self.__bucketName, objectKey, os.path.getsize(localPath), localPath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("get failing for bucket %s key %s localPath %s with %s", self.__bucketName, objectKey, localPath, str(e))
            return False

    def exists(self, objectKey):
        """Test for the existence of the input object key.

        Args:
            objectKey (str): object key

        Returns:
            (bool): True if the object exists or False otherwise
        """
        try:
            if not self._checkClient("exists", objectKey):
                return False
            self.__s3Client.head_object(Bucket=self.__bucketName, Key=objectKey)
            logger.debug("Found bucket %s key %s", self.__bucketName, objectKey)
            return True
        except Exception as e:
            logger.debug("head_object failing for bucket %s key %s with %s", self.__bucketName, objectKey, str(e))
            return False

    def listdir(self, objectKeyPrefix=""):
        """Return the list of object keys matching the input key prefix.

        Args:
            objectKeyPrefix (str, optional): object key prefix. Defaults to "" (all keys).

        Returns:
            (list): list of object keys or False on failure
        """
        try:
            if not self._checkClient("listdir", objectKeyPrefix):
                return False
            keyL = []
            paginator = self.__s3Client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.__bucketName, Prefix=objectKeyPrefix):
                keyL.extend([tD["Key"] for tD in page.get("Contents", [])])
            logger.debug("Listed %d keys in bucket %s prefix %r", len(keyL), self.__bucketName, objectKeyPrefix)
            return keyL
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("listdir failing for bucket %s prefix %s with %s", self.__bucketName, objectKeyPrefix, str(e))
            return False

    def remove(self, objectKey):
        """Delete the input object key.

        Args:
            objectKey (str): object key

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            if not self._checkClient("remove", objectKey):
                return False
            self.__s3Client.delete_object(Bucket=self.__bucketName, Key=objectKey)
            logger.info("Removed bucket %s key %s", self.__bucketName, objectKey)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("remove failing for bucket %s key %s with %s", self.__bucketName, objectKey, str(e))
            return False

    def close(self):
        """Release the S3 client.

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            if self.__s3Client is not None:
                self.__s3Client.close()
            self.__s3Client = None
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("Close failing with %s", str(e))
            return False

    def storeBundle(self, localFilePath, remoteDirPath, bundleFileName):
        """Upload a local bundle file, connecting and releasing the client in the process.

        Args:
            localFilePath (str): local source bundle file path
            remoteDirPath (str): remote directory path used as an object key prefix
            bundleFileName (str): bundle file name

        Returns:
            (bool): True for success or False otherwise
        """
        ok = False
        try:
            objectKey = self._makeObjectKey(self.__keyPrefix, remoteDirPath, bundleFileName)
            if self.connect():
                ok = self.put(localFilePath, objectKey)
                self.close()
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("storeBundle failing for bucket %r dirPath %r with %s", self.__bucketName, remoteDirPath, str(e))
        return ok

    def fetchBundle(self, localFilePath, remoteDirPath, bundleFileName):
        """Download a bundle file, connecting and releasing the client in the process.

        Args:
            localFilePath (str): local destination bundle file path
            remoteDirPath (str): remote directory path used as an object key prefix
            bundleFileName (str): bundle file name

        Returns:
            (bool): True for success or False otherwise
        """
        ok = False
        try:
            objectKey = self._makeObjectKey(self.__keyPrefix, remoteDirPath, bundleFileName)
            if self.connect():
                if self.exists(objectKey):
                    ok = self.get(objectKey, localFilePath)
                else:
                    logger.warning("Missing bundle object %r in bucket %r", objectKey, self.__bucketName)
                self.close()
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("fetchBundle failing for bucket %r dirPath %r with %s", self.__bucketName, remoteDirPath, str(e))
        return ok

    def _checkClient(self, methodName, objectKey):
        """Test that connect() has provided an S3 client.

        Args:
            methodName (str): calling method name used for logging
            objectKey (str): object key or key prefix used for logging

        Returns:
            (bool): True if a client is available or False otherwise
        """
        if self.__s3Client is None:
            logger.error("%s failing for bucket %s key %s: no S3 client (connect() not called or failed)", methodName, self.__bucketName, objectKey)
            return False
        return True

    @staticmethod
    def _makeObjectKey(*args):
        """Assemble an S3 object key from the input path segments.

        S3 keys are '/' delimited and must not begin with '/'.

        Returns:
            (str): normalized object key
        """
        return "/".join([tS.strip("/") for tS in args if tS and tS.strip("/")])

    @staticmethod
    def _parseUrl(url):
        """Split an s3:// URL into a bucket name and any leading key prefix.

        Args:
            url (str): s3 style URL (e.g. s3://my-bucket or s3://my-bucket/some/prefix)

        Returns:
            (str, str): bucket name and key prefix ("" if none)
        """
        tS = url[5:] if url.startswith("s3://") else url
        tS = tS.strip("/")
        bucketName, _, keyPrefix = tS.partition("/")
        return bucketName, keyPrefix
