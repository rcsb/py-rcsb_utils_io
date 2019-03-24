##
# File: UrlRequestUtil.py
#
# Simple wrapper for URL request processing
#
# Updates:
#  17-Mar-2019 jdw adjust return value to include response error code
#
##

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import contextlib
import logging
import ssl

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request


logger = logging.getLogger(__name__)


class UrlRequestUtil(object):
    """ Simple wrapper for URL request processing

    """

    def __init__(self, **kwargs):
        pass

    def post(self, url, endPoint, paramD, **kwargs):
        """
        """
        ret = None
        retCode = None
        sslCert = kwargs.get("sslCert", 'disable')
        optD = {}
        try:
            if sslCert == 'disable':
                gcontext = ssl._create_unverified_context()
                optD = {'context': gcontext}
            #
            urlPath = "%s/%s" % (url, endPoint)
            requestData = urlencode(paramD).encode("utf-8")
            logger.debug("Request %s with data %r" % (urlPath, requestData))

            with contextlib.closing(urlopen(urlPath, requestData, **optD)) as req:
                ret = req.read().decode('utf-8')
                retCode = req.getcode()

        except Exception as e:
            logger.error("Failing %s %s %r with %s" % (url, endPoint, paramD, str(e)))

        return ret, retCode

    def get(self, url, endPoint, paramD, **kwargs):
        """
        """
        ret = None
        retCode = None
        sslCert = kwargs.get("sslCert", 'disable')
        headerL = kwargs.get("headers", None)
        optD = {}
        try:
            if sslCert == 'disable':
                gcontext = ssl._create_unverified_context()
                optD = {'context': gcontext}
            #
            urlPath = "%s/%s" % (url, endPoint)
            requestData = urlencode(paramD)
            logger.debug("Request %s with data %s" % (urlPath, requestData))

            req = Request('%s?%s' % (urlPath, requestData))
            if headerL:
                for hTup in headerL:
                    req.add_header(hTup[0], hTup[1])

            with contextlib.closing(urlopen(req, **optD)) as req:
                ret = req.read().decode('utf-8')
                retCode = req.getcode()

        except Exception as e:
            logger.error("Failing %s %s %r with %s" % (url, endPoint, paramD, str(e)))

        return ret, retCode
