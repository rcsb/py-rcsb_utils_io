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
    The endpoint determines the service that is actually contacted.
    Endpoint and credentials are always taken from the standard AWS environment variables:

        AWS_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY
        AWS_ENDPOINT_URL

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
            boto3.client("s3", **self.__clientArgs).upload_file(localFilePath, self.__bucketName, objectKey)
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
            boto3.client("s3", **self.__clientArgs).download_file(self.__bucketName, objectKey, localFilePath)
            logger.info("Downloaded bucket %s key %s (%d bytes) to %s", self.__bucketName, objectKey, os.path.getsize(localFilePath), localFilePath)
            return True
        except Exception as e:
            logger.error("fetchBundle failing for bucket %s key %s localPath %s with %s", self.__bucketName, objectKey, localFilePath, str(e))
            raise

    def __makeObjectKey(self, remoteDirPath, bundleFileName):
        """Assemble the object key (the full path of the object within the bucket) from the
        key prefix of this class instance and the input remote directory path and file name.

        Empty segments are dropped and stray '/' characters are trimmed, so the result never
        contains '//' and never begins with '/' -- S3 treats both as literal key characters.

        For example, with a key prefix of 'some/prefix' parsed from the input URL:

            ('dir', 'b.tar.gz')  -> 'some/prefix/dir/b.tar.gz'
            ('/dir/sub/', 'b.tar.gz') -> 'some/prefix/dir/sub/b.tar.gz'
            ('', 'b.tar.gz') -> 'some/prefix/b.tar.gz'

        Args:
            remoteDirPath (str): remote directory path used as an object key prefix
            bundleFileName (str): bundle file name

        Returns:
            (str): normalized object key
        """
        segments = []
        for tS in (self.__keyPrefix, remoteDirPath, bundleFileName):
            tS = tS.strip("/") if tS else ""
            if tS:
                segments.append(tS)
        return "/".join(segments)
