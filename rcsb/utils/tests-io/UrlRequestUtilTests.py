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
import unittest

from rcsb.utils.io.UrlRequestUtil import UrlRequestUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class UrlRequestUtilTests(unittest.TestCase):

    def setUp(self):
        self.__mockTopPath = os.path.join(TOPDIR, 'rcsb', 'mock-data')
        self.__unpIdListV = ['P42284-1', 'P42284-3', 'P29994-2', 'P29994-3', 'P29994-4', 'P29994-5', 'P29994-6', 'P29994-7']
        self.__unpIdList2 = ['P20937', 'P21877', 'P22868', 'P23832', 'P25665', 'P26562', 'P27614']
        self.__unpIdList1 = ['P29490', 'P29496', 'P29498', 'P29499', 'P29503', 'P29506', 'P29508', 'P29509', 'P29525', 'P29533', 'P29534', 'P29547',
                             'P29549', 'P29555', 'P29557', 'P29558', 'P29559', 'P29563', 'P29588', 'P29589', 'P29590', 'P29597', 'P29599', 'P29600',
                             'P29602', 'P29603', 'P29617', 'P29678', 'P29691', 'P29715', 'P29717', 'P29723', 'P29724', 'P29736', 'P29741', 'P29745',
                             'P29748', 'P29749', 'P29752', 'P29758', 'P29768', 'P29803', 'P29808', 'P29813', 'P29827', 'P29830', 'P29837', 'P29838',
                             'P29846', 'P29848', 'P29882', 'P29894', 'P29898', 'P29899', 'P29929', 'P29946', 'P29957', 'P29960', 'P29965', 'P29966',
                             'P29972', 'P29978', 'P29986', 'P29987', 'P29988', 'P29989', 'P29990', 'P29991', 'P29994']

        self.__unpIdListV = ['P42284', 'P42284-1', 'P42284-2', 'P42284-3', 'P29994-1', 'P29994-2', 'P29994-3', 'P29994-4', 'P29994-5', 'P29994-6', 'P29994-7']

    def tearDown(self):
        pass

    def testUnpBatchFetchPost(self):
        """ UniProt batch fetch post test
        """
        baseUrl = 'https://www.ebi.ac.uk'
        endPoint = 'Tools/dbfetch/dbfetch'
        idList = self.__unpIdList1
        try:
            pD = {}
            pD['db'] = 'uniprotkb'
            pD['id'] = ','.join(idList)
            pD['format'] = 'uniprotxml'
            pD['style'] = 'raw'
            #
            ureq = UrlRequestUtil()
            ret = ureq.post(baseUrl, endPoint, pD)
            logger.debug("XML result %r" % ret)
            nm = ret.count("<entry ")
            self.assertGreaterEqual(nm, len(idList))
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testUnpBatchFetchGet1(self):
        """ UniProt batch fetch get test
        """
        baseUrl = 'https://www.ebi.ac.uk'
        endPoint = 'proteins/api/proteins'
        idList = self.__unpIdList1
        try:
            hL = [("Accept", "application/xml")]
            pD = {}
            pD['size'] = '-1'
            pD['accession'] = ','.join(idList)
            ureq = UrlRequestUtil()
            ret = ureq.get(baseUrl, endPoint, pD, headers=hL)
            logger.debug("XML result %r" % ret)
            nm = ret.count("<entry ")
            self.assertGreaterEqual(nm, len(idList) - 1)

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testUnpBatchFetchGet2(self):
        """ UniProt batch fetch get test
        """

        baseUrl = 'http://www.uniprot.org'
        endPoint = 'uploadlists'
        idList = self.__unpIdList1
        try:
            hL = [("Accept", "application/xml")]
            pD = {'from': 'ACC+ID',
                  'to': 'ACC',
                  'format': 'xml',
                  'query': ' '.join(idList)
                  }
            ureq = UrlRequestUtil()
            ret = ureq.get(baseUrl, endPoint, pD, headers=hL)
            logger.debug("XML result %r" % ret)
            nm = ret.count("<entry ")
            self.assertGreaterEqual(nm, len(idList))

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testNcbiFetchSummaryPost(self):
        """ UniProt batch fetch get test
        """
        idList = ['AP012306.1', 'U53879.1']
        database = 'Nucleotide'
        baseUrl = 'https://eutils.ncbi.nlm.nih.gov'
        endPoint = 'entrez/eutils/esummary.fcgi'
        try:
            hL = [("Accept", "application/xml")]
            pD = {}
            pD['db'] = database
            pD['id'] = ','.join(idList)
            pD['retmode'] = 'xml'
            ureq = UrlRequestUtil()
            ret = ureq.get(baseUrl, endPoint, pD, headers=hL)
            nm = ret.count("<DocSum")
            logger.debug("XML result %r" % ret)
            self.assertGreaterEqual(nm, len(idList))

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testNcbiFetchEntryPost(self):
        """ UniProt batch fetch get test
        """
        idList = ['AP012306.1', 'U53879.1']
        database = 'Nucleotide'
        baseUrl = 'https://eutils.ncbi.nlm.nih.gov'
        endPoint = 'entrez/eutils/efetch.fcgi'
        try:
            hL = [("Accept", "application/xml")]
            pD = {}
            pD['db'] = database
            pD['id'] = ','.join(idList)
            pD['retmode'] = 'xml'
            ureq = UrlRequestUtil()
            ret = ureq.get(baseUrl, endPoint, pD, headers=hL)
            nm = ret.count("<GBSeq_length>")
            logger.debug("XML result %r" % ret)
            self.assertGreaterEqual(nm, len(idList))

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()


def suiteUniProtTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(UrlRequestUtilTests("testUnpBatchFetchPost"))
    suiteSelect.addTest(UrlRequestUtilTests("testUnpBatchFetchGet1"))
    suiteSelect.addTest(UrlRequestUtilTests("testUnpBatchFetchGet2"))
    #
    return suiteSelect


def suiteNcbiTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(UrlRequestUtilTests("testNcbiFetchSummaryPost"))
    suiteSelect.addTest(UrlRequestUtilTests("testNcbiFetchEntryPost"))
    #
    return suiteSelect


if __name__ == '__main__':

    if True:
        mySuite = suiteUniProtTests()
        unittest.TextTestRunner(verbosity=2).run(mySuite)
        #
    if True:
        mySuite = suiteNcbiTests()
        unittest.TextTestRunner(verbosity=2).run(mySuite)
