# File:    MarshalUtilTests.py
# Author:  J. Westbrook
# Date:    22-May-2013
# Version: 0.001
#
# Update:
#  23-May-2018  jdw add preliminary default and helper tests
#   5-Jun-2018  jdw update prototypes for MarshalUtil() methods
#  13-Jun-2018  jdw add content classes
#  25-Nov-2018  jdw add FASTA tests
#   5-Feb-2019  jdw add tests for validation report processing
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


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MarshalUtilTests(unittest.TestCase):
    def setUp(self):
        self.__verbose = True
        self.__pathPdbxDictionaryFile = os.path.join(TOPDIR, "rcsb", "mock-data", "dictionaries", "mmcif_pdbx_v5_next.dic")
        self.__pathProvenanceFile = os.path.join(TOPDIR, "rcsb", "mock-data", "provenance", "rcsb_extend_provenance_info.json")
        self.__pathIndexFile = os.path.join(TOPDIR, "rcsb", "mock-data", "MOCK_EXCHANGE_SANDBOX", "update-lists", "all-pdb-list")
        self.__pathCifFile = os.path.join(TOPDIR, "rcsb", "mock-data", "data_type_info", "app_data_type_mapping.cif")

        #
        self.__pathSaveDictionaryFile = os.path.join(HERE, "test-output", "mmcif_pdbx_v5_next.dic")
        self.__pathSaveProvenanceFile = os.path.join(HERE, "test-output", "rcsb_extend_provenance_info.json")
        self.__pathSaveIndexFile = os.path.join(HERE, "test-output", "all-pdb-list")
        self.__pathSaveCifFile = os.path.join(HERE, "test-output", "app_data_type_mapping.cif")
        #
        self.__pathFastaFile = os.path.join(TOPDIR, "rcsb", "mock-data", "MOCK_EXCHANGE_SANDBOX", "sequence", "pdb_seq_prerelease.fasta")
        self.__pathSaveFastaFile = os.path.join(HERE, "test-output", "test-pre-release.fasta")
        #
        self.__pathXmlVrpt = os.path.join(TOPDIR, "rcsb", "mock-data", "MOCK_VALIDATION_REPORTS", "dr", "6drg", "6drg_validation.xml.gz")
        self.__pathSaveCifVrpt = os.path.join(HERE, "test-output", "6drg_validation.cif")
        self.__pathVrptMapFile = os.path.join(TOPDIR, "rcsb", "mock-data", "dictionaries", "vrpt_dictmap.json")
        self.__workPath = os.path.join(HERE, "test-output")
        self.__urlTarget = "ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz"
        #
        self.__mU = MarshalUtil()
        self.__startTime = time.time()
        logger.debug("Running tests on version %s", __version__)
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testReadDictionaryFile(self):
        """ Test the case read PDBx/mmCIF dictionary text file
        """
        try:
            cL = self.__mU.doImport(self.__pathPdbxDictionaryFile, fmt="mmcif-dict")
            logger.debug("Dictionary container list %d", len(cL))
            self.assertGreaterEqual(len(cL), 1)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadCifFile(self):
        """ Test the case read PDBx/mmCIF text file
        """
        try:
            cL = self.__mU.doImport(self.__pathCifFile, fmt="mmcif")
            logger.debug("Container list %d", len(cL))
            self.assertGreaterEqual(len(cL), 1)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadListFile(self):
        """ Test the case read list text file
        """
        try:
            cL = self.__mU.doImport(self.__pathIndexFile, fmt="list")
            logger.debug("List length %d", len(cL))
            self.assertGreaterEqual(len(cL), 1000)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadJsonFile(self):
        """ Test the case read JSON file
        """
        try:
            rObj = self.__mU.doImport(self.__pathProvenanceFile, fmt="json")
            logger.debug("Object length %d", len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteDictionaryFiles(self):
        """ Test the case read and write PDBx/mmCIF dictionary text file
        """
        try:
            cL = self.__mU.doImport(self.__pathPdbxDictionaryFile, fmt="mmcif-dict")
            logger.debug("Dictionary container list %d", len(cL))
            self.assertGreaterEqual(len(cL), 1)
            ok = self.__mU.doExport(self.__pathSaveDictionaryFile, cL, fmt="mmcif-dict")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteCifFile(self):
        """ Test the case read and write PDBx/mmCIF text file
        """
        try:
            cL = self.__mU.doImport(self.__pathCifFile, fmt="mmcif")
            logger.debug("Container list %d", len(cL))
            self.assertGreaterEqual(len(cL), 1)
            ok = self.__mU.doExport(self.__pathSaveCifFile, cL, fmt="mmcif")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteJsonFile(self):
        """ Test the case read and write JSON file
        """
        try:
            rObj = self.__mU.doImport(self.__pathProvenanceFile, fmt="json")
            logger.debug("Object length %d", len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
            ok = self.__mU.doExport(self.__pathSaveProvenanceFile, rObj, fmt="json")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteListFile(self):
        """ Test the case read and write list text file
        """
        try:
            cL = self.__mU.doImport(self.__pathIndexFile, fmt="list")
            logger.debug("List element %r length %d", cL[0], len(cL))
            count = 0
            for c in cL:
                fields = c.split()
                count += len(fields)
            _ = count
            self.assertGreaterEqual(len(cL), 1000)
            ok = self.__mU.doExport(self.__pathSaveIndexFile, cL, fmt="list")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteFastaFile(self):
        """ Test the case read and write FASTA sequence file
        """
        try:
            sD = self.__mU.doImport(self.__pathFastaFile, fmt="fasta", commentStyle="prerelease")
            logger.debug("Sequence length %d", len(sD))
            self.assertGreaterEqual(len(sD), 940)
            ok = self.__mU.doExport(self.__pathSaveFastaFile, sD, fmt="fasta")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteVrptFile(self):
        """ Test the case read and write validation report data file
        """
        try:
            sD = self.__mU.doImport(self.__pathXmlVrpt, fmt="vrpt-xml-to-cif", dictMapPath=self.__pathVrptMapFile)
            logger.debug("Val report container length %d", len(sD))
            self.assertGreaterEqual(len(sD), 1)
            ok = self.__mU.doExport(self.__pathSaveCifVrpt, sD, fmt="mmcif")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadUrlTarfile(self):
        """ Test the case to read URL target and extract a member
        """
        try:
            mU = MarshalUtil(workPath=self.__workPath)
            _, fn = os.path.split(self.__urlTarget)
            #
            nmL = mU.doImport(self.__urlTarget, fmt="tdd", rowFormat="list", tarMember="names.dmp")
            self.assertGreater(len(nmL), 2000000)
            logger.info("Names %d", len(nmL))
            ndL = mU.doImport(os.path.join(self.__workPath, fn), fmt="tdd", rowFormat="list", tarMember="nodes.dmp")
            self.assertGreater(len(ndL), 2000000)
            logger.info("Nodes %d", len(ndL))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def utilReadSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(MarshalUtilTests("testReadDictionaryFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadCifFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadJsonFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadListFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadUrlTarfile"))
    return suiteSelect


def utilReadWriteSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(MarshalUtilTests("testReadWriteDictionaryFiles"))
    suiteSelect.addTest(MarshalUtilTests("testReadWriteCifFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadWriteJsonFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadWriteListFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadWriteFastaFile"))
    suiteSelect.addTest(MarshalUtilTests("testReadWriteVrptFile"))
    return suiteSelect


if __name__ == "__main__":
    #
    mySuite = utilReadSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)

    mySuite = utilReadWriteSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
