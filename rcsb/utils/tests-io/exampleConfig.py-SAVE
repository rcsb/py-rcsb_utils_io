import logging
import os

from rcsb.utils.io.CryptUtils import CryptUtils

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def doCrypt1():
    """[summary]
     #
    MONGO_DB_HOST: 128.6.244.57
    # MONGO_DB_HOST: 132.249.213.189
    MONGO_DB_PORT: 27017
    MONGO_DB_USER_NAME: exchuser
    MONGO_DB_PASSWORD: expdb00000
    MONGO_DB_ADMIN_DB_NAME: admin
    #
    MYSQL_DB_HOST_NAME: localhost
    MYSQL_DB_PORT_NUMBER: '3306'
    MYSQL_DB_USER_NAME: root
    MYSQL_DB_PASSWORD: ChangeMeSoon
    MYSQL_DB_DATABASE_NAME: mysql

    """
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
            logger.info("mysql un:%s", encMsg)

        msg = "ChangeMeSoon"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("mysql pw:%s", encMsg)

        msg = "exchuser"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("mongo remote us:%s", encMsg)
        #
        msg = "expdb00000"
        encMsg = cu.encryptMessage(msg, ky)
        dcrMsg = cu.decryptMessage(encMsg, ky)
        if dcrMsg == msg:
            logger.info("mongo remote pw:%s", encMsg)

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
