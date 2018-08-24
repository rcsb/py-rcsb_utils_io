# File:    MarshalUtilTests.py
# Author:  J. Westbrook
# Date:    22-May-2013
# Version: 0.001
#
# Update:
#  23-May-2018  jdw add preliminary default and helper tests
#   5-Jun-2018  jdw update prototypes for MarshalUtil() methods
#  13-Jun-2018  jdw add content classes
#
#
#
##
"""
Tests for extraction, supplementing and packaging dictionary metadata for schema construction.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import os
import time
import unittest

from rcsb.utils.io import __version__
from rcsb.utils.io.MarshalUtil import MarshalUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MarshalUtilTests(unittest.TestCase):

    def setUp(self):
        self.__verbose = True
        self.__pathPdbxDictionaryFile = os.path.join(TOPDIR, 'rcsb', 'mock-data', 'dictionaries', 'mmcif_pdbx_v5_next.dic')
        self.__pathProvenanceFile = os.path.join(TOPDIR, 'rcsb', 'mock-data', 'provenance', 'rcsb_extend_provenance_info.json')
        self.__pathIndexFile = os.path.join(TOPDIR, 'rcsb', 'mock-data', 'MOCK_EXCHANGE_SANDBOX', 'update-lists', 'all-pdb-list')
        self.__pathCifFile = os.path.join(TOPDIR, 'rcsb', 'mock-data', 'data_type_info', 'app_data_type_mapping.cif')

        #
        self.__pathSaveDictionaryFile = os.path.join(HERE, 'test-output', 'mmcif_pdbx_v5_next.dic')
        self.__pathSaveProvenanceFile = os.path.join(HERE, 'test-output', 'rcsb_extend_provenance_info.json')
        self.__pathSaveIndexFile = os.path.join(HERE, 'test-output', 'all-pdb-list')
        self.__pathSaveCifFile = os.path.join(HERE, 'test-output', 'app_data_type_mapping.cif')
        #

        self.__mU = MarshalUtil()
        self.__startTime = time.time()
        logger.debug("Running tests on version %s" % __version__)
        logger.debug("Starting %s at %s" % (self.id(),
                                            time.strftime("%Y %m %d %H:%M:%S", time.localtime())))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)" % (self.id(),
                                                            time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                            endTime - self.__startTime))

    def testReadDictionaryFile(self):
        """ Test the case read PDBx/mmCIF dictionary text file
        """
        try:
            cL = self.__mU.doImport(self.__pathPdbxDictionaryFile, format="mmcif-dict")
            logger.debug("Dictionary container list %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadCifFile(self):
        """ Test the case read PDBx/mmCIF text file
        """
        try:
            cL = self.__mU.doImport(self.__pathCifFile, format="mmcif")
            logger.debug("Container list %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadListFile(self):
        """ Test the case read list text file
        """
        try:
            cL = self.__mU.doImport(self.__pathIndexFile, format="list")
            logger.debug("List length %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1000)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadJsonFile(self):
        """ Test the case read list text file
        """
        try:
            rObj = self.__mU.doImport(self.__pathProvenanceFile, format="json")
            logger.debug("Object length %d" % len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteDictionaryFiles(self):
        """ Test the case read PDBx/mmCIF dictionary text file
        """
        try:
            cL = self.__mU.doImport(self.__pathPdbxDictionaryFile, format="mmcif-dict")
            logger.debug("Dictionary container list %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1)
            ok = self.__mU.doExport(self.__pathSaveDictionaryFile, cL, format="mmcif-dict")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteCifFile(self):
        """ Test the case read PDBx/mmCIF text file
        """
        try:
            cL = self.__mU.doImport(self.__pathCifFile, format="mmcif")
            logger.debug("Container list %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1)
            ok = self.__mU.doExport(self.__pathSaveCifFile, cL, format="mmcif")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteJsonFile(self):
        """ Test the case read list text file
        """
        try:
            rObj = self.__mU.doImport(self.__pathProvenanceFile, format="json")
            logger.debug("Object length %d" % len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
            ok = self.__mU.doExport(self.__pathSaveProvenanceFile, rObj, format="json")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteListFile(self):
        """ Test the case read list text file
        """
        try:
            cL = self.__mU.doImport(self.__pathIndexFile, format="list")
            logger.debug("List length %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1000)
            ok = self.__mU.doExport(self.__pathSaveIndexFile, cL, format="list")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()


def utilReadSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(MarshalUtilTests("testReadDictionaryFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadCifFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadJsonFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadListFile"))
    return suiteSelect


def utilReadWriteSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(MarshalUtilTests("testReadWriteDictionaryFiles"))
    suiteSelect.addTest(MarshalUtilTests("testReadWriteCifFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadWriteJsonFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadWriteListFile"))
    return suiteSelect


if __name__ == '__main__':
    #
    if True:
        mySuite = utilReadSuite()
        unittest.TextTestRunner(verbosity=2).run(mySuite)

        mySuite = utilReadWriteSuite()
        unittest.TextTestRunner(verbosity=2).run(mySuite)
