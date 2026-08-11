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

    The target bucket is provided as an s3 style URL (e.g. s3://my-bucket or minio://my-bucket/some/prefix).
    Any URL scheme is accepted and ignored -- the endpoint determines the service that is actually contacted.
    Endpoint and credentials are always taken from the standard AWS environment variables:

        AWS_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY
        AWS_ENDPOINT_URL_S3 or AWS_ENDPOINT_URL  (required for MinIO and other non-AWS endpoints)
        AWS_REGION or AWS_DEFAULT_REGION  (optional)

    Any failure raises an exception.
    """

    def __init__(self, url):
        """Set the target bucket and connection details for this class instance.

        Args:
            url (str): s3 style URL (e.g. s3://my-bucket or minio://my-bucket/some/prefix)
        """
        _, _, tS = url.rpartition("://")
        self.__bucketName, _, self.__keyPrefix = tS.strip("/").partition("/")
        #
        self.__clientArgs = {
            "endpoint_url": os.environ.get("AWS_ENDPOINT_URL"),
            "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
            "region_name": os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION"),
        }

    @property
    def bucketName(self):
        """(str): target bucket name parsed from the input URL"""
        return self.__bucketName

    def storeBundle(self, localFilePath, remoteDirPath, bundleFileName):
        """Upload a local bundle file to the target bucket.

        Args:
            localFilePath (str): local source bundle file path
            remoteDirPath (str): remote directory path used as an object key prefix
            bundleFileName (str): bundle file name

        Returns:
            (bool): True for success

        Raises:
            Exception: on any upload failure
        """
        objectKey = self.__makeObjectKey(remoteDirPath, bundleFileName)
        try:
            self.__client().upload_file(localFilePath, self.__bucketName, objectKey)
            logger.info("Uploaded %s (%d bytes) to bucket %s key %s", localFilePath, os.path.getsize(localFilePath), self.__bucketName, objectKey)
            return True
        except Exception as e:
            logger.error("storeBundle failing for localPath %s bucket %s key %s with %s", localFilePath, self.__bucketName, objectKey, str(e))
            raise

    def fetchBundle(self, localFilePath, remoteDirPath, bundleFileName):
        """Download a bundle file from the target bucket.

        Args:
            localFilePath (str): local destination bundle file path
            remoteDirPath (str): remote directory path used as an object key prefix
            bundleFileName (str): bundle file name

        Returns:
            (bool): True for success

        Raises:
            Exception: on any download failure
        """
        objectKey = self.__makeObjectKey(remoteDirPath, bundleFileName)
        try:
            FileUtil().mkdirForFile(localFilePath)
            self.__client().download_file(self.__bucketName, objectKey, localFilePath)
            logger.info("Downloaded bucket %s key %s (%d bytes) to %s", self.__bucketName, objectKey, os.path.getsize(localFilePath), localFilePath)
            return True
        except Exception as e:
            logger.error("fetchBundle failing for bucket %s key %s localPath %s with %s", self.__bucketName, objectKey, localFilePath, str(e))
            raise

    def __client(self):
        """(botocore client): a new S3 client for the endpoint and credentials of this class instance"""
        return boto3.client("s3", **self.__clientArgs)

    def __makeObjectKey(self, *args):
        """Assemble a '/' delimited S3 object key from the input path segments.

        Returns:
            (str): normalized object key
        """
        return "/".join([tS.strip("/") for tS in (self.__keyPrefix,) + args if tS and tS.strip("/")])
