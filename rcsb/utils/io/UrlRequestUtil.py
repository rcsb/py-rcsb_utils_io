##
# File: UrlRequestUtil.py
#
# Simple wrapper for URL request processing
#
# Updates:
#  17-Mar-2019 jdw adjust return value to include response error code
#  16-Dec-2019 jdw add HTTPException to retry()
#  28-May-2029 jdw unwrapped methods now using requests module library.
#
##

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import contextlib
import json
import logging
import ssl

import requests
from rcsb.utils.io.decorators import retry

try:
    from http.client import HTTPException
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request, URLError, HTTPError

    # from http.client import HTTPException, RemoteDisconnected
except ImportError:
    # pylint: disable=ungrouped-imports
    from httplib import HTTPException
    from urllib import urlencode
    from urllib2 import urlopen, Request, URLError, HTTPError

logger = logging.getLogger(__name__)


class UrlRequestUtil(object):
    """ Simple wrapper for URL request processing

    """

    def __init__(self, **kwargs):
        pass

    def postUnWrapped(self, url, endPoint, paramD, **kwargs):
        return self.__postRequests(url, endPoint, paramD, **kwargs)

    @retry((URLError, HTTPError, HTTPException), maxAttempts=3, delaySeconds=5, multiplier=3, defaultValue=(None, None), logger=logger)
    def post(self, url, endPoint, paramD, **kwargs):
        return self.__post(url, endPoint, paramD, **kwargs)

    def __post(self, url, endPoint, paramD, **kwargs):
        """
        """
        ret = None
        retCode = None
        headerL = kwargs.get("headers", [])
        sslCert = kwargs.get("sslCert", "disable")
        exceptionsCatch = kwargs.get("exceptionsCatch", (HTTPError))
        httpCodesCatch = kwargs.get("httpCodesCatch", [])
        encoding = kwargs.get("encoding", "utf-8")
        #
        returnContentType = kwargs.get("returnContentType", None)
        if returnContentType == "JSON":
            if ("Accept", "application/json") not in headerL:
                headerL.append(("Accept", "application/json"))
        #
        optD = {"timeout": 5}
        try:
            if sslCert == "disable":
                gcontext = ssl._create_unverified_context()  # pylint: disable=protected-access
                optD = {"context": gcontext}
            #
            urlPath = "%s/%s" % (url, endPoint)
            requestData = urlencode(paramD).encode(encoding)
            logger.debug("Request %s with data %r", urlPath, requestData)

            with contextlib.closing(urlopen(urlPath, requestData, **optD)) as req:
                # pylint: disable=no-member
                #
                # for hTup in headerL:
                #    req.add_header(hTup[0], hTup[1])
                ret = req.read()
                retCode = req.getcode()
        #
        except exceptionsCatch as e:
            logger.debug("status code %r", e.code)
            retCode = e.code
            if retCode not in httpCodesCatch:
                raise e
        except Exception as e:
            logger.error("Failing %s %s %r with %s", url, endPoint, paramD, str(e))
            raise e
        #
        try:
            if returnContentType == "JSON":
                return json.loads(ret.decode(encoding)), retCode
            else:
                return ret.decode(encoding), retCode
        except Exception as e:
            if ret:
                logger.error("Decode failing %s %s %r with %s", url, endPoint, paramD, str(e))
                logger.debug("End of return is %r", ret[-1000:])

        return None, retCode

    def getUnWrapped(self, url, endPoint, paramD, **kwargs):
        return self.__getRequests(url, endPoint, paramD, **kwargs)

    @retry((URLError, HTTPError, HTTPException), maxAttempts=3, delaySeconds=5, multiplier=3, defaultValue=(None, None), logger=logger)
    def get(self, url, endPoint, paramD, **kwargs):
        return self.__get(url, endPoint, paramD, **kwargs)

    def __get(self, url, endPoint, paramD, **kwargs):
        """
        """
        ret = None
        retCode = None
        sslCert = kwargs.get("sslCert", "disable")
        encoding = kwargs.get("encoding", "utf-8")
        headerL = kwargs.get("headers", [])
        exceptionsCatch = kwargs.get("exceptionsCatch", (HTTPError))
        httpCodesCatch = kwargs.get("httpCodesCatch", [])
        returnContentType = kwargs.get("returnContentType", None)
        if returnContentType == "JSON":
            if ("Accept", "application/json") not in headerL:
                headerL.append(("Accept", "application/json"))
        #
        headerL.append(("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"))
        #
        optD = {"timeout": 5}
        try:
            if sslCert == "disable":
                gcontext = ssl._create_unverified_context()  # pylint: disable=protected-access
                optD = {"context": gcontext}
            #
            urlPath = "%s/%s" % (url, endPoint)
            requestData = urlencode(paramD)
            logger.debug("Request %s with parameters %s", urlPath, requestData)

            req = Request("%s?%s" % (urlPath, requestData))
            if headerL:
                for hTup in headerL:
                    req.add_header(hTup[0], hTup[1])
            #
            with contextlib.closing(urlopen(req, **optD)) as req:
                # pylint: disable=no-member
                ret = req.read()
                retCode = req.getcode()
            #
            #    req = urlopen(req, **optD)
            #    ret = req.read()
            #    retCode = req.getcode()

            if ret is None:
                logger.error("Return is empty - return code is %r", retCode)
            else:
                logger.debug("Return length %d return code %r", len(ret), retCode)
            #
        except exceptionsCatch as e:
            retCode = e.code
            if retCode not in httpCodesCatch:
                raise e
        except Exception as e:
            logger.error("Failing %s %s %r with %s", url, endPoint, paramD, str(e))
            raise e

        try:
            if returnContentType == "JSON":
                return json.loads(ret.decode(encoding)), retCode
            else:
                return ret.decode(encoding), retCode
        except Exception as e:
            if ret:
                logger.error("Decode failing %s %s %r with %s", url, endPoint, paramD, str(e))
                logger.debug("End of return is %r", ret[-1000:])

        return None, retCode

    def __getRequests(self, url, endPoint, paramD, **kwargs):
        """
        """
        ret = None
        retCode = None
        # sslCert = kwargs.get("sslCert", "disable")
        # encoding = kwargs.get("encoding", "utf-8")
        headerD = kwargs.get("headers", {})
        exceptionsCatch = kwargs.get("exceptionsCatch", (HTTPError))
        httpCodesCatch = kwargs.get("httpCodesCatch", [])
        returnContentType = kwargs.get("returnContentType", None)
        timeOutSeconds = kwargs.get("timeOut", 5)
        if returnContentType == "JSON":
            if "Accept" not in headerD:
                headerD["Accept"] = "application/json"
        #
        headerD.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"})
        #
        optD = {"timeout": timeOutSeconds, "allow_redirects": True}
        try:
            # if sslCert == "disable":
            #    gcontext = ssl._create_unverified_context()  # pylint: disable=protected-access
            #    optD = {"context": gcontext}
            #
            urlPath = "%s/%s" % (url, endPoint)
            req = requests.get(urlPath, params=paramD, headers=headerD, **optD)
            retCode = req.status_code
            if retCode == 200:
                if returnContentType == "JSON":
                    ret = req.json()
                else:
                    ret = req.text
            #
            if ret is None:
                logger.debug("Return is empty - return code is %r", retCode)
            else:
                logger.debug("Return length %d return code %r", len(ret), retCode)
            #
            return ret, retCode
        except exceptionsCatch as e:
            retCode = e.code
            if retCode not in httpCodesCatch:
                raise e
        except Exception as e:
            logger.error("Failing %s %s %r with %s", url, endPoint, paramD, str(e))
            raise e

        return None, retCode

    def __postRequests(self, url, endPoint, paramD, **kwargs):
        """
        """
        ret = None
        retCode = None
        # sslCert = kwargs.get("sslCert", "disable")
        # encoding = kwargs.get("encoding", "utf-8")
        headerD = kwargs.get("headers", {})
        exceptionsCatch = kwargs.get("exceptionsCatch", (HTTPError))
        httpCodesCatch = kwargs.get("httpCodesCatch", [])
        returnContentType = kwargs.get("returnContentType", None)
        timeOutSeconds = kwargs.get("timeOut", 5)
        if returnContentType == "JSON":
            if "Accept" not in headerD:
                headerD["Accept"] = "application/json"
        #
        headerD.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"})
        #
        optD = {"timeout": timeOutSeconds, "allow_redirects": True}
        try:
            # if sslCert == "disable":
            #    gcontext = ssl._create_unverified_context()  # pylint: disable=protected-access
            #    optD = {"context": gcontext}
            #
            urlPath = "%s/%s" % (url, endPoint)
            req = requests.post(urlPath, data=paramD, headers=headerD, **optD)
            retCode = req.status_code
            if retCode == 200:
                if returnContentType == "JSON":
                    ret = req.json()
                else:
                    ret = req.text
            #
            if ret is None:
                logger.debug("Return is empty - return code is %r", retCode)
            else:
                logger.debug("Return length %d return code %r", len(ret), retCode)
            #
            return ret, retCode
        except exceptionsCatch as e:
            retCode = e.code
            if retCode not in httpCodesCatch:
                raise e
        except Exception as e:
            logger.error("Failing %s %s %r with %s", url, endPoint, paramD, str(e))
            raise e

        return None, retCode
