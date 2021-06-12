##
# File: CryptUtils.py
# Date: 12-Aug-2019 Jdw
#
# Updates:
#
##
"""
 Utilities supporting encrypting and decrypting flat files and messages.
"""
__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import base64
import binascii
import hashlib
import logging

from nacl.encoding import HexEncoder, RawEncoder
from nacl.secret import SecretBox
from nacl.utils import random

logger = logging.getLogger(__name__)


class CryptUtils(object):
    """Utility class for encrypting and decrypting data files and messages

    ** This class does not yet support any stream operations so resources must be
    available to load data sets in memory -

    """

    def __init__(self, *args, **kwargs):
        _ = args
        _ = kwargs

    def newKey(self):
        """Generate a new encryption key.

        Returns:
            (str): encryption key
        """
        key = random(SecretBox.KEY_SIZE)
        return binascii.hexlify(key).decode("utf-8")

    def encryptMessage(self, msg, hexKey):
        """Encrypt the input message.

        Args:
            msg (str): input message
            hexKey (str): encryption key

        Returns:
            (str):  encrypted message text
        """
        txt = None
        try:
            box = SecretBox(hexKey.encode("utf-8"), encoder=HexEncoder)
            bMsg = msg.encode("utf-8")
            encMsg = box.encrypt(bMsg, encoder=RawEncoder)
            txt = base64.b64encode(encMsg).decode("ascii")
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return txt

    def decryptMessage(self, msg, hexKey):
        """Decrypt the input message.

        Args:
            msg (str): input message
            hexKey (str): encryption key

        Returns:
            (str):  decrypted message text
        """
        txt = None
        try:
            box = SecretBox(hexKey.encode("utf-8"), encoder=HexEncoder)
            bMsg = base64.b64decode(msg)
            dcrMsg = box.decrypt(bMsg)
            logger.debug("type %r text %r", type(dcrMsg), dcrMsg)
            txt = dcrMsg.decode("utf-8")
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return txt

    def encryptFile(self, inpPath, outPath, hexKey, chunkSize=65536):
        """Encrypt the data in the input file store this in the output file.

        Args:
            inpPath (str): input file path
            outPath (str): output file path (encrypted)
            hexKey (str): encryption key
            chunkSize (int, optional): the size of incremental copy operations. Defaults to 65536.

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            box = SecretBox(hexKey.encode("utf-8"), encoder=HexEncoder)
            tL = []
            with open(inpPath, "rb") as ifh:
                while True:
                    chunk = ifh.read(chunkSize)
                    if not chunk:
                        break
                    tL.append(chunk)
            #
            txt = b"".join(tL)
            logger.debug("Read %s size %d", inpPath, len(txt))
            enctxt = box.encrypt(txt, encoder=RawEncoder)
            tL = [enctxt[i : i + chunkSize] for i in range(0, len(enctxt), chunkSize)]
            logger.debug("Chunks %d size %d", len(tL), len(enctxt))
            #
            with open(outPath, "wb") as ofh:
                for tV in tL:
                    ofh.write(tV)
            return True
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return False

    def decryptFile(self, inpPath, outPath, hexKey, chunkSize=65536):
        """Decrypt the data in the input file store the result in the output file.

        Args:
            inpPath ([type]): input file path (encrypted)
            outPath ([type]): output file path
            hexKey ([type]): encryption key
            chunkSize (int, optional): the size of incremental copy operations. Defaults to 65536.

        Returns:
            (bool): True for success or False otherwise
        """
        try:
            box = SecretBox(hexKey.encode("utf-8"), encoder=HexEncoder)
            tL = []
            with open(inpPath, "rb") as ifh:
                while True:
                    chunk = ifh.read(chunkSize)
                    if not chunk:
                        break
                    tL.append(chunk)
            #
            enctxt = b"".join(tL)
            #
            txt = box.decrypt(enctxt)
            tL = [txt[i : i + chunkSize] for i in range(0, len(txt), chunkSize)]
            logger.debug("Chunks %d size %d", len(tL), len(txt))
            #
            with open(outPath, "wb") as ofh:
                for tV in tL:
                    ofh.write(tV)
            return True
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return False

    def getFileHash(self, filePath, hashType="SHA1", blockSize=65536):
        """Return the hash (hashType) for the input file.

        Args:
            filePath (str): for input file path
            hashType (str, optional): one of MD5, SHA1, or SHA256. Defaults to "SHA1".
            blockSize (int, optional): the size of incremental read operations. Defaults to 65536.

        Returns:
            (dict): {"hashDigest": xxxx , "hashType": 'SHA1|MD5|SHA256'}
        """
        rD = {}
        if hashType not in ["MD5", "SHA1", "SHA256"]:
            return rD
        try:
            if hashType == "SHA1":
                hashObj = hashlib.sha1()
            elif hashType == "SHA256":
                hashObj = hashlib.sha256()
            elif hashType == "MD5":
                hashObj = hashlib.md5()

            with open(filePath, "rb") as ifh:
                for block in iter(lambda: ifh.read(blockSize), b""):
                    hashObj.update(block)
            rD = {"hashDigest": hashObj.hexdigest(), "hashType": hashType}
        except Exception as e:
            logger.exception("Failing with file %s %r", filePath, str(e))
        return rD
