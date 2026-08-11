##
# File:    S3Util.py
# Author:  mjt
# Date:    10-Aug-2026
#
# Updates:
#
##
"""
Class providing essential data transfer operations for S3 compatible object storage (e.g. AWS S3, MinIO).

Credentials and endpoint are taken from the standard AWS environment variables unless supplied explicitly:

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_SESSION_TOKEN      (optional)
    AWS_DEFAULT_REGION     (optional)
    AWS_ENDPOINT_URL_S3 or AWS_ENDPOINT_URL  (required for MinIO and other non-AWS endpoints)

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
    """Class providing essential data transfer operations for S3 compatible object storage"""

    def __init__(self, *args, **kwargs):
        _ = args
        self.__raiseExceptions = kwargs.get("raiseExceptions", False)
        self.__s3Client = None
        #

    def connect(self, endPointUrl, accessKey=None, secretKey=None, sessionToken=None, region=None):
        """Create an S3 client for the input (or environment provided) endpoint and credentials.

        Args:
            endPointUrl (str, optional): service endpoint (e.g. https://minio.rcsb.org). Defaults to environment setting.
            accessKey (str, optional): access key id. Defaults to environment setting.
            secretKey (str, optional): secret access key. Defaults to environment setting.
            sessionToken (str, optional): session token. Defaults to environment setting.
            region (str, optional): region name. Defaults to environment setting.

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            self.__s3Client = boto3.client(
                "s3",
                endpoint_url=endPointUrl,
                aws_access_key_id=accessKey if accessKey else None,
                aws_secret_access_key=secretKey if secretKey else None,
                aws_session_token=sessionToken if sessionToken else None,
                region_name=region if region else None,
            )
            logger.info("Connected S3 client for endPointUrl %r region %r", endPointUrl, region)
            return True
        except Exception as e:
            self.__s3Client = None
            if self.__raiseExceptions:
                raise e
            logger.error("Failing S3 connect for endPointUrl %r with %s", endPointUrl, str(e))
            return False

    def put(self, localPath, bucketName, objectKey):
        """Upload a local file to the input bucket and object key.

        Args:
            localPath (str): local source file path
            bucketName (str): target bucket name
            objectKey (str): target object key

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            if self.__s3Client is None:
                logger.error("put failing for bucket %s key %s: no S3 client (connect() not called or failed)", bucketName, objectKey)
                return False
            logger.debug("Uploading %s to bucket %s key %s", localPath, bucketName, objectKey)
            self.__s3Client.upload_file(localPath, bucketName, objectKey)
            logger.info("Uploaded %s (%d bytes) to bucket %s key %s", localPath, os.path.getsize(localPath), bucketName, objectKey)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("put failing for localPath %s bucket %s key %s with %s", localPath, bucketName, objectKey, str(e))
            return False

    def get(self, bucketName, objectKey, localPath):
        """Download the input bucket object key to a local file path.

        Args:
            bucketName (str): source bucket name
            objectKey (str): source object key
            localPath (str): local destination file path

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            if self.__s3Client is None:
                logger.error("get failing for bucket %s key %s: no S3 client (connect() not called or failed)", bucketName, objectKey)
                return False
            fileU = FileUtil()
            fileU.mkdirForFile(localPath)
            logger.debug("Downloading bucket %s key %s to %s", bucketName, objectKey, localPath)
            self.__s3Client.download_file(bucketName, objectKey, localPath)
            logger.info("Downloaded bucket %s key %s (%d bytes) to %s", bucketName, objectKey, os.path.getsize(localPath), localPath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("get failing for bucket %s key %s localPath %s with %s", bucketName, objectKey, localPath, str(e))
            return False

    def exists(self, bucketName, objectKey):
        """Test for the existence of the input bucket object key.

        Args:
            bucketName (str): bucket name
            objectKey (str): object key

        Returns:
            (bool): True if the object exists or False otherwise
        """
        try:
            self.__s3Client.head_object(Bucket=bucketName, Key=objectKey)
            logger.debug("Found bucket %s key %s", bucketName, objectKey)
            return True
        except Exception as e:
            logger.debug("head_object failing for bucket %s key %s with %s", bucketName, objectKey, str(e))
            return False

    def listdir(self, bucketName, objectKeyPrefix=""):
        """Return the list of object keys in the input bucket matching the input key prefix.

        Args:
            bucketName (str): bucket name
            objectKeyPrefix (str, optional): object key prefix. Defaults to "" (all keys).

        Returns:
            (list): list of object keys or False on failure
        """
        try:
            keyL = []
            paginator = self.__s3Client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucketName, Prefix=objectKeyPrefix):
                keyL.extend([tD["Key"] for tD in page.get("Contents", [])])
            logger.debug("Listed %d keys in bucket %s prefix %r", len(keyL), bucketName, objectKeyPrefix)
            return keyL
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("listdir failing for bucket %s prefix %s with %s", bucketName, objectKeyPrefix, str(e))
            return False

    def remove(self, bucketName, objectKey):
        """Delete the input bucket object key.

        Args:
            bucketName (str): bucket name
            objectKey (str): object key

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            self.__s3Client.delete_object(Bucket=bucketName, Key=objectKey)
            logger.info("Removed bucket %s key %s", bucketName, objectKey)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("remove failing for bucket %s key %s with %s", bucketName, objectKey, str(e))
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

    def storeBundle(self, url, localFilePath, remoteDirPath, bundleFileName, accessKey=None, secretKey=None):
        """Upload a local bundle file to the s3 URL, connecting and releasing the client in the process.

        Args:
            url (str): s3 style URL (e.g. s3://my-bucket or s3://my-bucket/some/prefix)
            localFilePath (str): local source bundle file path
            remoteDirPath (str): remote directory path used as an object key prefix
            bundleFileName (str): bundle file name
            accessKey (str, optional): access key id. Defaults to environment setting.
            secretKey (str, optional): secret access key. Defaults to environment setting.

        Returns:
            (bool): True for success or False otherwise
        """
        ok = False
        try:
            bucketName, keyPrefix = self.parseUrl(url)
            objectKey = self.makeObjectKey(keyPrefix, remoteDirPath, bundleFileName)
            if self.connect(self.getEndPointUrl(), accessKey=accessKey, secretKey=secretKey):
                ok = self.put(localFilePath, bucketName, objectKey)
                self.close()
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("storeBundle failing for url %r dirPath %r with %s", url, remoteDirPath, str(e))
        return ok

    def fetchBundle(self, url, localFilePath, remoteDirPath, bundleFileName, accessKey=None, secretKey=None):
        """Download a bundle file from the s3 URL, connecting and releasing the client in the process.

        Args:
            url (str): s3 style URL (e.g. s3://my-bucket or s3://my-bucket/some/prefix)
            localFilePath (str): local destination bundle file path
            remoteDirPath (str): remote directory path used as an object key prefix
            bundleFileName (str): bundle file name
            accessKey (str, optional): access key id. Defaults to environment setting.
            secretKey (str, optional): secret access key. Defaults to environment setting.

        Returns:
            (bool): True for success or False otherwise
        """
        ok = False
        try:
            bucketName, keyPrefix = self.parseUrl(url)
            objectKey = self.makeObjectKey(keyPrefix, remoteDirPath, bundleFileName)
            if self.connect(self.getEndPointUrl(), accessKey=accessKey, secretKey=secretKey):
                if self.exists(bucketName, objectKey):
                    ok = self.get(bucketName, objectKey, localFilePath)
                else:
                    logger.warning("Missing bundle object %r in bucket %r", objectKey, bucketName)
                self.close()
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("fetchBundle failing for url %r dirPath %r with %s", url, remoteDirPath, str(e))
        return ok

    @staticmethod
    def getEndPointUrl():
        """Return the service endpoint from the standard AWS environment variables (None if unset)."""
        return os.environ.get("AWS_ENDPOINT_URL_S3", os.environ.get("AWS_ENDPOINT_URL"))

    @staticmethod
    def makeObjectKey(*args):
        """Assemble an S3 object key from the input path segments.

        S3 keys are '/' delimited and must not begin with '/'.

        Returns:
            (str): normalized object key
        """
        return "/".join([tS.strip("/") for tS in args if tS and tS.strip("/")])

    @staticmethod
    def parseUrl(url):
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
