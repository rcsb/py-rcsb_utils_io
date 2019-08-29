import logging
import os

from rcsb.utils.io.CryptUtils import CryptUtils

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def doCrypt1():
    try:
        ky = os.environ["CONFIG_SUPPORT_TOKEN_ENV"]
        logger.info("---------------")
        cu = CryptUtils()
        # ky = cu.newKey()
        logger.info("ky:%s", ky)
        #
        msg = "jdwestbrook@gmail.com"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("un:%s", encMsg)

        msg = "JsItEOd3;BxAQ"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("pw:%s", encMsg)

        msg = "root"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("un:%s", encMsg)

        msg = "ChangeMeSoon"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("pw:%s", encMsg)

    except Exception as e:
        logger.exception("Failing with %s", str(e))


def doCrypt2():
    try:
        logger.info("-------TEST--------")
        cu = CryptUtils()
        ky = cu.newKey()
        logger.info("ky:%s", ky)
        #
        msg = "testuser"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("un:%s", encMsg)

        msg = "testuserpassword"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("pw:%s", encMsg)

    except Exception as e:
        logger.exception("Failing with %s", str(e))


if __name__ == "__main__":
    doCrypt1()
    # doCrypt2()
