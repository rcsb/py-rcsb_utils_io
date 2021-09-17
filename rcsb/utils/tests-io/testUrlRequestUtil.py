##
# File:    UrlRequestUtilTests.py
# Author:  J. westbrook
# Date:    16-Mar-2019
#
# Update:
##
"""
Test cases for selected get and post requests using UrlRequestUtil wrappers -

"""

import logging
import os
import time
import unittest

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote

from rcsb.utils.io import __version__
from rcsb.utils.io.UrlRequestUtil import UrlRequestUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class UrlRequestUtilTests(unittest.TestCase):
    doTroubleshooting = False

    def setUp(self):
        self.__mockTopPath = os.path.join(TOPDIR, "rcsb", "mock-data")
        self.__unpIdListV = ["P42284-1", "P42284-3", "P29994-2", "P29994-3", "P29994-4", "P29994-5", "P29994-6", "P29994-7"]
        self.__unpIdList2 = ["P20937", "P21877", "P22868", "P23832", "P25665", "P26562", "P27614"]
        self.__unpIdList1 = [
            "P29490",
            "P29496",
            "P29498",
            "P29499",
            "P29503",
            "P29506",
            "P29508",
            "P29509",
            "P29525",
            "P29533",
            "P29534",
            "P29547",
            "P29549",
            "P29555",
            "P29557",
            "P29558",
            "P29559",
            "P29563",
            "P29588",
            "P29589",
            "P29590",
            "P29597",
            "P29599",
            "P29600",
            "P29602",
            "P29603",
            "P29617",
            "P29678",
            "P29691",
            "P29715",
            "P29717",
            "P29723",
            "P29724",
            "P29736",
            "P29741",
            "P29745",
            "P29748",
            "P29749",
            "P29752",
            "P29758",
            "P29768",
            "P29803",
            "P29808",
            "P29813",
            "P29827",
            "P29830",
            "P29837",
            "P29838",
            "P29846",
            "P29848",
            "P29882",
            "P29894",
            "P29898",
            "P29899",
            "P29929",
            "P29946",
            "P29957",
            "P29960",
            "P29965",
            "P29966",
            "P29972",
            "P29978",
            "P29986",
            "P29987",
            "P29988",
            "P29989",
            "P29990",
            "P29991",
            "P29994",
        ]

        self.__unpIdListV = ["P42284", "P42284-1", "P42284-2", "P42284-3", "P29994-1", "P29994-2", "P29994-3", "P29994-4", "P29994-5", "P29994-6", "P29994-7"]
        logger.debug("Running tests on version %s", __version__)
        self.__startTime = time.time()
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testUnpBatchFetchPost(self):
        """UniProt batch fetch (ebi dbfetch) post test"""
        baseUrl = "https://www.ebi.ac.uk"
        endPoint = "Tools/dbfetch/dbfetch"
        idList = self.__unpIdList1[:10]
        try:
            pD = {}
            pD["db"] = "uniprotkb"
            pD["id"] = ",".join(idList)
            pD["format"] = "uniprotxml"
            pD["style"] = "raw"
            #
            ureq = UrlRequestUtil()
            ret, retCode = ureq.post(baseUrl, endPoint, pD)
            logger.debug("XML result %r", ret)
            nm = ret.count("<entry ")
            logger.info("Result count %d status code %r", nm, retCode)
            self.assertGreaterEqual(nm, len(idList))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testUnpBatchFetchGetEbi(self):
        """UniProt batch fetch (proteins) get test (EBI endpoint)"""
        baseUrl = "https://www.ebi.ac.uk"
        endPoint = "proteins/api/proteins"
        idList = self.__unpIdList1[:10]
        try:
            hL = [("Accept", "application/xml")]
            pD = {}
            pD["size"] = "-1"
            pD["accession"] = ",".join(idList)
            ureq = UrlRequestUtil()
            ret, retCode = ureq.get(baseUrl, endPoint, pD, headers=hL)
            logger.debug("XML result %r", ret)
            nm = ret.count("<entry ")
            logger.info("Result count %d status code %r", nm, retCode)
            self.assertGreaterEqual(nm, len(idList) - 1)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testUnpBatchFetchFail(self):
        """UniProt batch fetch (proteins) get test (expected failure)"""
        baseUrl = "https://www0.ebi.ac.uk"
        endPoint = "proteins/api/proteins"
        idList = self.__unpIdList1[:10]
        try:
            hL = [("Accept", "application/xml")]
            pD = {}
            pD["size"] = "-1"
            pD["accession"] = ",".join(idList)
            ureq = UrlRequestUtil()
            ret, retCode = ureq.get(baseUrl, endPoint, pD, headers=hL)
            logger.debug("XML result %r", ret)
            logger.debug("Result status code %r", retCode)
            self.assertEqual(ret, None)
            self.assertEqual(retCode, None)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    @unittest.skip("Skip - This service is currently not reliable on unbuntu 20.04")
    def testUnpBatchFetchGetUrllib(self):
        """UniProt batch fetch (uploadlists) get test (urllib)"""

        baseUrl = "https://www.uniprot.org"
        # baseUrl = "https://pir3.uniprot.org"

        endPoint = "uploadlists"
        idList = self.__unpIdList1[:10]
        try:
            # hD = {"Accept": "application/xml"}
            hL = [("Accept", "application/xml")]
            pD = {"from": "ACC+ID", "to": "ACC", "format": "xml", "query": " ".join(idList)}
            ureq = UrlRequestUtil()
            # using wrapped version
            ret, retCode = ureq.get(baseUrl, endPoint, pD, headers=hL, sslCert="enable")
            logger.debug("XML result %r", ret)
            nm = ret.count("<entry ")
            logger.info("Result count %d status code %r", nm, retCode)
            self.assertGreaterEqual(nm, len(idList))

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    @unittest.skip("Skip - This service is currently not reliable on unbuntu 20.04")
    def testUnpBatchFetchGetRequests(self):
        """UniProt batch fetch (uploadlists) get test (requests)"""

        baseUrl = "https://www.uniprot.org"
        # baseUrl = "https://pir3.uniprot.org"

        endPoint = "uploadlists"
        idList = self.__unpIdList1[:10]
        try:
            hD = {"Accept": "application/xml"}
            # hL = [("Accept", "application/xml")]
            pD = {"from": "ACC+ID", "to": "ACC", "format": "xml", "query": " ".join(idList)}
            ureq = UrlRequestUtil()
            # using unwrapped (requests) version
            ret, retCode = ureq.getUnWrapped(baseUrl, endPoint, pD, headers=hD, sslCert="enable")
            logger.debug("XML result %r", ret)
            nm = ret.count("<entry ")
            logger.info("Result count %d status code %r", nm, retCode)
            self.assertGreaterEqual(nm, len(idList))

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testNcbiFetchSummaryPost(self):
        """NCBI batch fetch (esummary) get test"""
        idList = ["AP012306.1", "U53879.1"]
        database = "Nucleotide"
        baseUrl = "https://eutils.ncbi.nlm.nih.gov"
        endPoint = "entrez/eutils/esummary.fcgi"
        try:
            hL = [("Accept", "application/xml")]
            pD = {}
            pD["db"] = database
            pD["id"] = ",".join(idList)
            pD["retmode"] = "xml"
            ureq = UrlRequestUtil()
            ret, retCode = ureq.get(baseUrl, endPoint, pD, headers=hL)
            nm = ret.count("<DocSum")
            logger.debug("XML result %r", ret)
            logger.info("Result count %d status code %r", nm, retCode)
            self.assertGreaterEqual(nm, len(idList))

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testNcbiFetchEntryPost(self):
        """NCBI batch fetch (efetch) get test"""
        idList = ["AP012306.1", "U53879.1"]
        database = "Nucleotide"
        baseUrl = "https://eutils.ncbi.nlm.nih.gov"
        endPoint = "entrez/eutils/efetch.fcgi"
        try:
            hL = [("Accept", "application/xml")]
            pD = {}
            pD["db"] = database
            pD["id"] = ",".join(idList)
            pD["retmode"] = "xml"
            ureq = UrlRequestUtil()
            ret, retCode = ureq.get(baseUrl, endPoint, pD, headers=hL)
            nm = ret.count("<GBSeq_length>")
            logger.debug("XML result %r", ret)
            logger.info("Result count %d status code %r", nm, retCode)
            self.assertGreaterEqual(nm, len(idList))

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testPubChemFetch(self):
        """PubChem fetch test"""
        idTupList = [("JTOKYIBTLUQVQV-FGHQGBLESA-N", 404, None), ("CXHHBNMLPJOKQD-UHFFFAOYSA-N", 200, 78579)]
        nameSpace = "inchikey"
        domain = "compound"
        searchType = "lookup"
        returnType = "record"
        requestType = "GET"
        outputType = "JSON"
        baseUrl = "https://pubchem.ncbi.nlm.nih.gov"
        httpCodesCatch = [404]

        try:
            for (identifier, testRetCode, testPcId) in idTupList:
                for requestType in ["GET", "POST"]:
                    ret, retCode = None, None
                    pD = {}
                    hL = {}
                    ureq = UrlRequestUtil()
                    if nameSpace in ["cid", "name", "inchikey"] and returnType in ["record"] and searchType in ["lookup"] and requestType == "GET":
                        uId = quote(identifier.encode("utf8"))
                        endPoint = "/".join(["rest", "pug", domain, nameSpace, uId, outputType])
                        ret, retCode = ureq.getUnWrapped(baseUrl, endPoint, pD, headers=hL, httpCodesCatch=httpCodesCatch, returnContentType="JSON", sslCert="enable")
                    elif nameSpace in ["cid", "name", "inchikey"] and returnType in ["record"] and searchType in ["lookup"] and requestType == "POST":
                        endPoint = "/".join(["rest", "pug", domain, nameSpace, outputType])
                        pD = {nameSpace: identifier}
                        ret, retCode = ureq.postUnWrapped(baseUrl, endPoint, pD, headers=hL, httpCodesCatch=httpCodesCatch, returnContentType="JSON", sslCert="enable")
                    #
                    elif nameSpace in ["cid"] and returnType in ["classification"] and searchType in ["lookup"] and requestType == "GET":
                        # Needs to be specifically targeted on a particular compound ...
                        uId = quote(identifier.encode("utf8"))
                        endPoint = "/".join(["rest", "pug", domain, nameSpace, uId, returnType, outputType])
                        pD = {"classification_type": "simple"}
                        # pD = {nameSpace: identifier}
                        ret, retCode = ureq.getUnWrapped(baseUrl, endPoint, pD, headers=hL, httpCodesCatch=httpCodesCatch, returnContentType="JSON", sslCert="enable")
                    #
                    elif nameSpace in ["cid"] and returnType in ["classification"] and searchType in ["lookup"] and requestType == "POST":
                        # Needs to be specifically targeted on a particular compound ...
                        endPoint = "/".join(["rest", "pug", domain, nameSpace, returnType, outputType])
                        # This is a long request return server codes may be observed 500
                        pD = {nameSpace: identifier, "classification_type": "simple"}
                        # pD = {nameSpace: identifier}
                        ret, retCode = ureq.postUnWrapped(baseUrl, endPoint, pD, headers=hL, httpCodesCatch=httpCodesCatch, returnContentType="JSON", sslCert="enable")
                    #
                    #
                    logger.debug("Result status code %r", retCode)
                    self.assertEqual(retCode, testRetCode)
                    if retCode == 200:
                        pcId = ret["PC_Compounds"][0]["id"]["id"]["cid"]
                        self.assertEqual(pcId, testPcId)

            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    @unittest.skip("Skip - This service is currently not reliable")
    def testPubChemFetchClassification(self):
        """PubChem fetch classification test - can timeout"""
        idTupList = [("2244", 200, "2244", "record"), ("123631", 200, "123631", "record"), ("2244", 200, "2244", "classification"), ("123631", 200, "123631", "classification")]
        nameSpace = "cid"
        domain = "compound"
        searchType = "lookup"
        # returnType = "record"
        requestType = "GET"
        outputType = "JSON"
        baseUrl = "https://pubchem.ncbi.nlm.nih.gov"
        httpCodesCatch = [404]

        try:
            for (identifier, testRetCode, testPcId, returnType) in idTupList:
                for requestType in ["GET", "POST"]:
                    logger.info("namespace %r identifier %r returnType %r requestType %r", nameSpace, identifier, returnType, requestType)
                    ret, retCode = None, None
                    pD = {}
                    hL = []
                    ureq = UrlRequestUtil()
                    if nameSpace in ["cid", "name", "inchikey"] and returnType in ["record"] and searchType in ["lookup"] and requestType == "GET":
                        uId = quote(identifier.encode("utf8"))
                        endPoint = "/".join(["rest", "pug", domain, nameSpace, uId, outputType])
                        ret, retCode = ureq.get(baseUrl, endPoint, pD, headers=hL, httpCodesCatch=httpCodesCatch, returnContentType="JSON")
                    elif nameSpace in ["cid", "name", "inchikey"] and returnType in ["record"] and searchType in ["lookup"] and requestType == "POST":
                        endPoint = "/".join(["rest", "pug", domain, nameSpace, outputType])
                        pD = {nameSpace: identifier}
                        ret, retCode = ureq.post(baseUrl, endPoint, pD, headers=hL, httpCodesCatch=httpCodesCatch, returnContentType="JSON")
                    #
                    elif nameSpace in ["cid"] and returnType in ["classification"] and searchType in ["lookup"] and requestType == "GET":
                        # Needs to be specifically targeted on a particular compound ...
                        uId = quote(identifier.encode("utf8"))
                        endPoint = "/".join(["rest", "pug", domain, nameSpace, uId, returnType, outputType])
                        # pD = {"classification_type": "simple"}
                        pD = {}
                        # pD = {nameSpace: identifier}
                        ret, retCode = ureq.getUnWrapped(baseUrl, endPoint, pD, headers={}, httpCodesCatch=httpCodesCatch, returnContentType="JSON")
                    #
                    elif nameSpace in ["cid"] and returnType in ["classification"] and searchType in ["lookup"] and requestType == "POST":
                        # Needs to be specifically targeted on a particular compound ...
                        endPoint = "/".join(["rest", "pug", domain, nameSpace, returnType, outputType])
                        # This is a long request return server codes may be observed 500
                        # pD = {nameSpace: identifier, "classification_type": "simple"}
                        pD = {nameSpace: identifier}
                        ret, retCode = ureq.postUnWrapped(baseUrl, endPoint, pD, headers={}, httpCodesCatch=httpCodesCatch, returnContentType="JSON")
                    #
                    #
                    logger.debug("Result status code %r", retCode)
                    self.assertEqual(retCode, testRetCode)
                    if retCode == 200 and returnType == "record":
                        pcId = str(ret["PC_Compounds"][0]["id"]["id"]["cid"])
                        self.assertEqual(pcId, testPcId)

            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    @unittest.skipUnless(doTroubleshooting, "Skip - troubleshooting test")
    def testGetChemSearchRequests(self):
        """ChemSearch repetition GET protocol test (using requests module)"""
        # dev instances east
        # baseUrl = ["http://128.6.159.86"]
        #
        # Production west instances
        # baseUrlList = ["http://132.249.213.210", "http://132.249.213.110", "https://chemsearch-west.rcsb.org"]
        # baseUrlList = ["http://128.6.158.85", "http://128.6.158.158", "https://chemsearch-east.rcsb.org"]
        baseUrlList = ["https://chemsearch-west.rcsb.org", "https://chemsearch-east.rcsb.org"]
        #
        endPoint = "chem-match-v1/InChI"
        resultLen = 13
        descr = "InChI=1S/C9H15N5O3/c1-3(15)6(16)4-2-11-7-5(12-4)8(17)14-9(10)13-7/h3-4,6,12,15-16H,2H2,1H3,(H4,10,11,13,14,17)/t3-,4-,6-/m1/s1"
        try:
            for baseUrl in baseUrlList:
                pD = {"query": descr, "matchType": "fingerprint-similarity"}
                for ii in range(100):
                    ureq = UrlRequestUtil()
                    ret, retCode = ureq.getUnWrapped(baseUrl, endPoint, pD, headers={}, sslCert="enable", returnContentType="JSON")
                    if len(ret["matchedIdList"]) != resultLen:
                        logger.info(">>> %3d (%r) (%r) result length %r", ii, baseUrl, retCode, len(ret["matchedIdList"]))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteUniProtTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(UrlRequestUtilTests("testUnpBatchFetchPost"))
    suiteSelect.addTest(UrlRequestUtilTests("testUnpBatchFetchGetEbi"))
    suiteSelect.addTest(UrlRequestUtilTests("testUnpBatchFetchGetRequests"))
    suiteSelect.addTest(UrlRequestUtilTests("testUnpBatchFetchGetUrllib"))
    #
    return suiteSelect


def suiteNcbiTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(UrlRequestUtilTests("testNcbiFetchSummaryPost"))
    suiteSelect.addTest(UrlRequestUtilTests("testNcbiFetchEntryPost"))
    suiteSelect.addTest(UrlRequestUtilTests("testPubChemFetch"))
    suiteSelect.addTest(UrlRequestUtilTests("testPubChemFetchClassification"))
    #
    return suiteSelect


if __name__ == "__main__":

    mySuite = suiteUniProtTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
    #

    mySuite = suiteNcbiTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
