##
# File: FileUtil.py
#
# Skeleton implementation of common File I/O operations.
#
# Updates:
#  5-Jun-2018 jdw add support for local copy operations using shutil.copy
#  6-Mar-2019 jdw add previously stubbed remote access and tar file member support
# 10-Mar-2019 jdw add exists() method
# 11-Aug-2019 jdw incorporate compress/uncompress and toAscii methods from IoUtil.py
#                 add __extractZipMember() method.  Add retry support for __fetchUrl().
#                 Replace urlibx version of __fetchUrl with a version that depends on
#                 requests module to better support redirection and authentication.
##

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

#
import bz2
import contextlib
import gzip
import hashlib
import io
import logging
import os
import shutil
import tarfile
import tempfile
import traceback
import zipfile
import lzma

import requests
from rcsb.utils.io.decorators import retry

# pylint: disable=ungrouped-imports
try:
    import urllib.request as myurl
except Exception:
    import urllib2 as myurl

try:
    from urllib.parse import urlsplit
except Exception:
    from urlparse import urlsplit


logger = logging.getLogger(__name__)


class FileUtil(object):
    """Skeleton implementation for File I/O operations"""

    def __init__(self, workPath=None, **kwargs):
        _ = kwargs
        self.__workPath = workPath
        self.__timeout = None
        if self.__workPath and self.__workPath != ".":
            self.mkdir(workPath)

    def exists(self, locator, mode=os.R_OK):
        """Return if the input file exists with optional mode settings

        Args:
            locator (string): local file path or url
            mode (mode, optional): local mode setting. Defaults to os.R_OK.

        Returns:
            bool: True if file exists or False otherwise
        """
        try:
            if not locator:
                logger.warning("Null locator: %s", "".join(traceback.format_stack()))
                return False
            localFlag = self.isLocal(locator)
            if localFlag:
                return os.access(locator, mode)
            else:
                if locator.startswith("ftp:"):
                    logger.warning("ftp:// protocol not supported.")
                else:
                    response = requests.head(locator, timeout=self.__timeout)
                    logger.debug("response code %r", response.status_code)
                    if response.status_code == 200 and "content-length" in response.headers and int(response.headers["content-length"]) > 0:
                        return True
        except Exception as e:
            logger.exception("Failing for %r with %s", locator, str(e))
        return False

    def size(self, locator):
        """Return the file size in bytes

        Args:
            locator (str): local file path or url

        Returns:
            int: approximate file size in bytes or zero
        """
        try:
            if not locator:
                logger.warning("Null locator: %s", "".join(traceback.format_stack()))
                return False
            localFlag = self.isLocal(locator)
            if localFlag:
                st = os.stat(locator)
                return st.st_size
            else:
                if locator.startswith("ftp:"):
                    logger.warning("ftp:// protocol not supported.")
                else:
                    response = requests.head(locator, timeout=self.__timeout)
                    if response.status_code == 200 and "content-length" in response.headers:
                        return int(response.headers["content-length"])
        except Exception:
            return 0

    def hash(self, filePath, hashType="md5"):
        try:
            localFlag = self.isLocal(filePath)
            if not localFlag:
                return None
            with open(filePath, "rb") as ifh:
                if hashType == "md5":
                    fileHash = hashlib.md5()
                elif hashType == "sha256":
                    fileHash = hashlib.sha256()
                else:
                    logger.error("Unsupported hash type %r", hashType)
                    return None
                chunk = ifh.read(8192)
                while chunk:
                    fileHash.update(chunk)
                    chunk = ifh.read(8192)
            return fileHash.hexdigest()
        except Exception:
            return None

    def mkdir(self, dirPath, mode=0o755):
        """Create the input directory.

        Args:
            dirPath (string): local directory path
            mode (mode, optional): mode setting. Defaults to os.W_OK.

        Returns:
            bool: True for success or False otherwise
        """
        try:
            logger.debug("Checking target directory %s", dirPath)
            if not os.access(dirPath, os.W_OK):
                logger.debug("Creating cache directory %s", dirPath)
                os.makedirs(dirPath, mode)
            return True
        except Exception as e:
            logger.exception("Failing for %s with %s", dirPath, str(e))
        return False

    def mkdirForFile(self, filePath, mode=0o755):
        """Create directory path for the input path if it does not exists.

        Args:
            filePath (string): local file path target
            mode (mode, optional): mode setting. Defaults to os.W_OK.

        Returns:
            bool: True for success or False otherwise
        """
        try:
            logger.debug("Checking target directory for file %s", filePath)
            dirPath, _ = os.path.split(filePath)
            if dirPath:
                return self.mkdir(dirPath, mode)
            else:
                return True
        except Exception as e:
            logger.exception("Failing for %s with %s", filePath, str(e))
        return False

    #
    def remove(self, pth):
        """Method to remove input file, link  or directory."""
        ok = False
        try:
            localFlag = self.isLocal(pth)
            if not localFlag:
                return ok
            if pth and not self.exists(pth):
                ok = True
            if os.path.isfile(pth) or os.path.islink(pth):
                os.unlink(pth)
                ok = True
            elif os.path.isdir(pth):
                shutil.rmtree(pth, True)
                ok = True
        except Exception as e:
            logger.error("Failing for %s with %s", pth, str(e))
            ok = False
        #
        return ok

    def replace(self, srcPath, dstPath):
        """Method to replace input file or directory (local only method)."""
        ok = False
        try:
            localFlag = self.isLocal(srcPath)
            if not localFlag:
                return ok
            if srcPath and dstPath and self.exists(srcPath):
                os.replace(srcPath, dstPath)
                ok = True
        except Exception as e:
            logger.error("Failing for %r -> %r with %s", srcPath, dstPath, str(e))
            ok = False
        #
        return ok

    #
    def get(self, remote, local, **kwargs):
        """Fetch remote file to a local path.

        Arguments:
            remote (TYPE): source locator (remote)
            local (TYPE): destination locator (local)
            **kwargs: Description

                tarMember(str) : target member name in a remote tarfile

        Returns:
            bool: True for success or false otherwise

        """
        try:
            ret = False
            tarMember = kwargs.get("tarMember", None)
            #
            localFlag = self.isLocal(remote)
            #
            if localFlag and not tarMember:
                rPath = self.getFilePath(remote)
                lPath = self.getFilePath(local)
                self.mkdirForFile(lPath)
                shutil.copyfile(rPath, lPath)
                ret = True
            elif localFlag and tarMember:
                # Extract a particular member from a local tar file -
                rPath = self.getFilePath(remote)
                lPath = self.getFilePath(local)
                self.mkdirForFile(lPath)
                ret = self.__extractTarMember(rPath, tarMember, lPath)
                logger.debug("Extract %r from %r to %r status %r", tarMember, rPath, lPath, ret)
            elif not localFlag and tarMember:
                # Extract a particular member from a remote tar file
                tarPath = os.path.join(self.__workPath, self.getFileName(remote))
                ret = self.__fetchUrl(remote, tarPath, **kwargs)
                logger.debug("Fetched %r to %r status %r", remote, tarPath, ret)
                #
                ret = self.__extractTarMember(tarPath, tarMember, self.getFilePath(local)) if ret else False
                logger.debug("Extract %r from %r to %r status %r", tarMember, tarPath, self.getFilePath(local), ret)
            elif not localFlag and not tarMember:
                ret = self.__fetchUrl(remote, self.getFilePath(local), **kwargs)
                logger.debug("Fetched %r localpath %r status %r", remote, self.getFilePath(local), ret)
            else:
                ret = False
            #
        except Exception as e:
            logger.exception("For remote %r local %r failing with %s", remote, local, str(e))

        #
        return ret

    def put(self, local, remote, **kwargs):
        """Copy local file to remote location."""
        _ = kwargs
        try:
            ret = False
            localFlag = self.isLocal(remote)
            #
            if localFlag:
                rPath = self.getFilePath(remote)
                self.mkdirForFile(rPath)
                lPath = self.getFilePath(local)
                shutil.copyfile(lPath, rPath)
                ret = True
            else:
                ret = False
        except Exception as e:
            logger.exception("For remote %r local %r failing with %s", remote, local, str(e))
            ret = False
        return ret

    def getFilePath(self, locator):
        try:
            locSp = urlsplit(locator)
            return locSp.path
        except Exception as e:
            logger.exception("For locator %r failing with %s", locator, str(e))
        return None

    def getFileName(self, locator):
        try:
            locSp = urlsplit(locator)
            (_, fn) = os.path.split(locSp.path)
            return fn
        except Exception as e:
            logger.exception("For locator %r failing with %s", locator, str(e))
        return None

    def isLocal(self, locator):
        try:
            locSp = urlsplit(locator)
            return locSp.scheme in ["", "file"]
        except Exception as e:
            logger.exception("For locator %r failing with %s", locator, str(e))
        return None

    def getScheme(self, locator):
        try:
            locSp = urlsplit(locator)
            return locSp.scheme
        except Exception as e:
            logger.exception("For locator %r Failing with %s", locator, str(e))
        return None

    def bundleTarfile(self, tarFilePath, dirPathList, mode="w:gz", recursive=True):
        """Create a tar file bundle of the contents of the input directory path.

        Args:
            tarFilePath (str): output tar file path
            dirPathList (list): target directory path list to store
            mode (str, optional): the file mode for the tar file. Defaults to "w:gz".
            recursive (bool, optional): include subdirectories recursively. Defaults to True.

        Returns:
            bool: True for success or False otherwise
        """
        ret = True
        curDir = os.getcwd()
        try:
            self.mkdirForFile(tarFilePath)
            with tarfile.open(tarFilePath, mode=mode) as archive:
                for dirPath in dirPathList:
                    dp, tp = os.path.split(dirPath)
                    os.chdir(dp)
                    archive.add(tp, recursive=recursive)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ret = False
        os.chdir(curDir)
        return ret

    def unbundleTarfile(self, tarFilePath, dirPath="."):
        """Unbundle input tar file.

        Args:
            tarFilePath (str): path to the input tar bundle file
            dirPath (str, optional): directory path to write extracted data. Defaults to ".".

        Returns:
            bool: True for success or False otherwise
        """
        #   import tarfile contents into dirPath -
        ret = True
        try:

            with tarfile.open(tarFilePath) as tar:
                tar.extractall(path=dirPath)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ret = False
        return ret

    def unbundleZipfile(self, zipFilePath, dirPath="."):
        """Unbundle input ZIP file.

        Args:
            zipFilePath (str): path to the input tar bundle file
            dirPath (str, optional): directory path to write extracted data. Defaults to ".".

        Returns:
            bool: True for success or False otherwise
        """
        #   import zipfile contents into dirPath -
        ret = True
        try:
            with zipfile.ZipFile(zipFilePath, mode="r") as zObj:
                zObj.extractall(path=dirPath)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ret = False
        return ret

    def __extractTarMember(self, tarFilePath, memberName, memberPath):
        ret = True
        try:
            with tarfile.open(tarFilePath) as tar:
                fIn = tar.extractfile(memberName)
                with open(memberPath, "wb") as ofh:
                    ofh.write(fIn.read())
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ret = False
        return ret

    def __extractZipMember(self, zipFilePath, memberName, memberPath):
        ret = False
        try:
            with zipfile.ZipFile(zipFilePath, mode="r") as zObj:
                memberList = zObj.namelist()
                for member in memberList:
                    if member == memberName:
                        zObj.extract(member, path=memberPath)
                        ret = True
                        break
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ret = False
        return ret

    def __fetchUrl(self, url, filePath, **kwargs):

        try:
            noRetry = kwargs.get("noRetry", False)
            scheme = self.getScheme(url)
            ok = self.mkdirForFile(filePath)
            if not ok:
                logger.error("Failing to create target directory for file %r", filePath)
                return False
            if scheme in ["ftp"]:
                return self.__fetchUrlPy(url, filePath, **kwargs)
            else:
                if noRetry:
                    return self.__fetchUrlReqNoRt(url, filePath, **kwargs)
                else:
                    return self.__fetchUrlReqRt(url, filePath, **kwargs)
        except Exception as e:
            logger.error("Failing for url %r with %s", url, str(e))
        return False

    @retry((myurl.URLError, myurl.HTTPError), maxAttempts=3, delaySeconds=5, multiplier=3, defaultValue=False, logger=logger)
    def __fetchUrlPy(self, url, filePath, **kwargs):
        """Fetch data from a remote URL and store this in input filePath.

        Args:
            url (str): target URL to fetch
            filePath (str): path to store the data from the remote url
            username (str): basic auth username
            password (str): dasic auth password
            kwargs (dict, optional): other options

        Raises:
            e: any exception

        Returns:
            bool: True for sucess or False otherwise
        """
        try:
            user = kwargs.get("username", None)
            pw = kwargs.get("password", None)
            if user and pw:
                pwMgr = myurl.HTTPPasswordMgrWithDefaultRealm()
                pwMgr.add_password(None, url, user, pw)
                handler = myurl.HTTPBasicAuthHandler(pwMgr)
                opener = myurl.build_opener(handler)
                # Install the opener.
                myurl.install_opener(opener)
            #
            ok = self.mkdirForFile(filePath)
            if not ok:
                logger.error("Failing to create target directory for file %r", filePath)
                return False
            with open(filePath, "wb") as outFile:
                with contextlib.closing(myurl.urlopen(url)) as fp:
                    blockSize = 1024 * 8
                    while True:
                        block = fp.read(blockSize)  # pylint: disable=no-member
                        if not block:
                            break
                        outFile.write(block)
            return True
        except Exception as e:
            logger.error("Failing for %s with %s", filePath, str(e))
            raise e

        return False

    @retry((requests.exceptions.RequestException), maxAttempts=3, delaySeconds=5, multiplier=3, defaultValue=False, logger=logger)
    def __fetchUrlReqRaw(self, url, filePath, **kwargs):
        """Fetch data from a remote URL and store this in input filePath.

        Args:
            url (str): target URL to fetch
            filePath (str): path to store the data from the remote url
            username (str): basic auth username
            password (str): dasic auth password
            kwargs (dict, optional): other options

        Raises:
            e: any exception

        Returns:
            bool: True for sucess or False otherwise

            with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)


        """
        user = kwargs.get("username", None)
        pw = kwargs.get("password", None)
        #
        try:
            ok = self.mkdirForFile(filePath)
            if not ok:
                logger.error("Failing to create target directory for file %r", filePath)
                return False
            if user and pw:
                with requests.get(url, stream=True, auth=(user, pw), allow_redirects=True, timeout=self.__timeout) as rIn:
                    with open(filePath, "wb") as fOut:
                        shutil.copyfileobj(rIn.raw, fOut)

            else:
                with requests.get(url, stream=True, allow_redirects=True, timeout=self.__timeout) as rIn:
                    with open(filePath, "wb") as fOut:
                        shutil.copyfileobj(rIn.raw, fOut)

            return True
        except Exception as e:
            logger.error("Failing for %s with %s", filePath, str(e))
            raise e

        return False

    @retry((requests.exceptions.RequestException), maxAttempts=3, delaySeconds=5, multiplier=3, defaultValue=False, logger=logger)
    def __fetchUrlReqRt(self, url, filePath, **kwargs):
        return self.__fetchUrlReqNoRt(url, filePath, **kwargs)

    def __fetchUrlReqNoRt(self, url, filePath, **kwargs):
        """Fetch data from a remote URL and store this in input filePath.

        Args:
            url (str): target URL to fetch
            filePath (str): path to store the data from the remote url
            username (str): basic auth username
            password (str): dasic auth password
            kwargs (dict, optional): other options

        Raises:
            e: any exception

        Returns:
            bool: True for sucess or False otherwise

        """
        user = kwargs.get("username", None)
        pw = kwargs.get("password", None)
        chunkSize = kwargs.get("chunkSize", 1024 * 1024 * 3)
        #
        try:
            ok = self.mkdirForFile(filePath)
            if not ok:
                logger.error("Failing to create target directory for file %r", filePath)
                return False
            if user and pw:
                with requests.get(url, stream=True, auth=(user, pw), allow_redirects=True, timeout=self.__timeout) as rIn:
                    if rIn.status_code == requests.codes.ok:  # pylint: disable=no-member
                        with open(filePath, "wb") as fOut:
                            for chunk in rIn.iter_content(chunk_size=chunkSize):
                                fOut.write(chunk)
                    else:
                        logger.error("Fetch %r fails with status %r", url, rIn.status_code)
                        rIn.raise_for_status()
                        return False
            else:
                with requests.get(url, stream=True, allow_redirects=True, timeout=self.__timeout) as rIn:
                    if rIn.status_code == requests.codes.ok:  # pylint: disable=no-member
                        with open(filePath, "wb") as fOut:
                            for chunk in rIn.iter_content(chunk_size=chunkSize):
                                fOut.write(chunk)
                    else:
                        logger.error("Fetch %r fails with status %r", url, rIn.status_code)
                        rIn.raise_for_status()
                        return False

            return True
        except Exception as e:
            logger.error("Failing for %s with %s", filePath, str(e))
            raise e

        return False

    def toAscii(self, inputFilePath, outputFilePath, chunkSize=5000, encodingErrors="ignore"):
        """Encode input file to Ascii and write this to the target output file.   Handle encoding
        errors according to the input settting ('ignore', 'escape', 'xmlcharrefreplace').
        """
        try:
            ok = self.mkdirForFile(outputFilePath)
            if not ok:
                logger.error("Failing to create target directory for file %r", outputFilePath)
                return False
            chunk = []
            with io.open(inputFilePath, "r", encoding="utf-8") as rIn, io.open(outputFilePath, "w", encoding="ascii") as wOut:
                for line in rIn:
                    # chunk.append(line.encode('ascii', 'xmlcharrefreplace').decode('ascii'))
                    chunk.append(line.encode("ascii", encodingErrors).decode("ascii"))
                    if len(chunk) == chunkSize:
                        wOut.writelines(chunk)
                        chunk = []
                wOut.writelines(chunk)
            return True
        except Exception as e:
            logger.error("Failing text ascii encoding for %s with %s", inputFilePath, str(e))
        #
        return False

    def uncompress(self, inputFilePath, outputDir=None):
        """Uncompress the input file if the path name has a recognized compression type file extension.

        Return the path of the uncompressed file (in outDir) or the original input file path.

        """
        try:
            outputDir = outputDir if outputDir else tempfile.gettempdir()
            _, fn = os.path.split(inputFilePath)
            bn, _ = os.path.splitext(fn)
            outputFilePath = os.path.join(outputDir, bn)
            if inputFilePath.endswith(".gz"):
                with gzip.open(inputFilePath, mode="rb") as inpF:
                    with io.open(outputFilePath, "wb") as outF:
                        shutil.copyfileobj(inpF, outF)
            elif inputFilePath.endswith(".bz2"):
                with bz2.open(inputFilePath, mode="rb") as inpF:
                    with io.open(outputFilePath, "wb") as outF:
                        shutil.copyfileobj(inpF, outF)
            elif inputFilePath.endswith(".xz"):
                with lzma.open(inputFilePath, mode="rb") as inpF:
                    with io.open(outputFilePath, "wb") as outF:
                        shutil.copyfileobj(inpF, outF)
            elif inputFilePath.endswith(".zip"):
                with zipfile.ZipFile(inputFilePath, mode="r") as zObj:
                    memberList = zObj.namelist()
                    for member in memberList[:1]:
                        zObj.extract(member, path=outputDir)
                if memberList:
                    outputFilePath = os.path.join(outputDir, memberList[0])
            else:
                outputFilePath = inputFilePath

        except Exception as e:
            logger.exception("Failing uncompress for file %s with %s", inputFilePath, str(e))
        logger.debug("Returning file path %r", outputFilePath)
        return outputFilePath

    def compress(self, inpPath, outPath, compressType="gzip"):
        try:
            if compressType == "gzip":
                with open(inpPath, "rb") as fIn:
                    with gzip.open(outPath, "wb") as fOut:
                        shutil.copyfileobj(fIn, fOut)
                return True
            else:
                logger.error("Unsupported compressType %r", compressType)
        except Exception as e:
            logger.exception("Compressing file %s failing with %s", inpPath, str(e))
        return False
