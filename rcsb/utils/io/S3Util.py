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
            url (str): s3 style URL (e.g. s3://my-bucket or minio://my-bucket/some/prefix)
            endPointUrl (str, optional): service endpoint (e.g. https://minio.rcsb.org). Defaults to environment setting.
            accessKey (str, optional): access key id. Defaults to environment setting.
            secretKey (str, optional): secret access key. Defaults to environment setting.
            sessionToken (str, optional): session token. Defaults to environment setting.
            region (str, optional): region name. Defaults to environment setting.
        """
        self.__raiseExceptions = kwargs.get("raiseExceptions", False)
        #
        _, _, tS = url.rpartition("://")
        self.__bucketName, _, self.__keyPrefix = tS.strip("/").partition("/")
        #
        self.__clientArgs = {
            "endpoint_url": endPointUrl if endPointUrl else os.environ.get("AWS_ENDPOINT_URL_S3", os.environ.get("AWS_ENDPOINT_URL")),
            "aws_access_key_id": accessKey,
            "aws_secret_access_key": secretKey,
            "aws_session_token": sessionToken,
            "region_name": region,
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
            (bool): True for success or False otherwise
        """
        objectKey = self.__makeObjectKey(remoteDirPath, bundleFileName)
        try:
            self.__client().upload_file(localFilePath, self.__bucketName, objectKey)
            logger.info("Uploaded %s (%d bytes) to bucket %s key %s", localFilePath, os.path.getsize(localFilePath), self.__bucketName, objectKey)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("storeBundle failing for localPath %s bucket %s key %s with %s", localFilePath, self.__bucketName, objectKey, str(e))
            return False

    def fetchBundle(self, localFilePath, remoteDirPath, bundleFileName):
        """Download a bundle file from the target bucket.

        Args:
            localFilePath (str): local destination bundle file path
            remoteDirPath (str): remote directory path used as an object key prefix
            bundleFileName (str): bundle file name

        Returns:
            (bool): True for success or False otherwise
        """
        objectKey = self.__makeObjectKey(remoteDirPath, bundleFileName)
        try:
            FileUtil().mkdirForFile(localFilePath)
            self.__client().download_file(self.__bucketName, objectKey, localFilePath)
            logger.info("Downloaded bucket %s key %s (%d bytes) to %s", self.__bucketName, objectKey, os.path.getsize(localFilePath), localFilePath)
            return True
        except Exception as e:
            if self.__raiseExceptions:
                raise e
            logger.error("fetchBundle failing for bucket %s key %s localPath %s with %s", self.__bucketName, objectKey, localFilePath, str(e))
            return False

    def __client(self):
        """(botocore client): a new S3 client for the endpoint and credentials of this class instance"""
        return boto3.client("s3", **self.__clientArgs)

    def __makeObjectKey(self, *args):
        """Assemble a '/' delimited S3 object key from the input path segments.

        Returns:
            (str): normalized object key
        """
        return "/".join([tS.strip("/") for tS in (self.__keyPrefix,) + args if tS and tS.strip("/")])
