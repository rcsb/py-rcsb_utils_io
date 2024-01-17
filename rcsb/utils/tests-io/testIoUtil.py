# File:    IoUtilTests.py
# Author:  J. Westbrook
# Date:    22-May-2018
# Version: 0.001
#
# Update:
#  23-May-2018  jdw add preliminary default and helper tests
#   5-Jun-2018  jdw update prototypes for IoUtil() methods
#  13-Jun-2018  jdw add content classes
#  25-Nov-2018  jdw add FASTA tests
#  30-Nov-2018  jdw add CSV tests
#  13-Aug-2019  jdw add tests for multipart json/pickle
#  18-Sep-2019  jdw add tests for method deserializeCsvIter()
#
#
#
##
"""
Tests for core serialization and deserialization utilities.

"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import os
import sys
import time
import unittest
from collections import OrderedDict

from rcsb.utils.io import __version__
from rcsb.utils.io.IoUtil import IoUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class IoUtilTests(unittest.TestCase):
    def setUp(self):
        self.__verbose = True
        self.__pathPdbxDictionaryFile = os.path.join(TOPDIR, "rcsb", "mock-data", "dictionaries", "mmcif_pdbx_v5_next.dic")
        self.__pathJsonTestFile = os.path.join(TOPDIR, "rcsb", "mock-data", "dictionaries", "vrpt_dictmap.json")
        self.__pathIndexFile = os.path.join(TOPDIR, "rcsb", "mock-data", "MOCK_EXCHANGE_SANDBOX", "update-lists", "all-pdb-list")
        self.__pathCifFile = os.path.join(TOPDIR, "rcsb", "mock-data", "MOCK_BIRD_CC_REPO", "0", "PRDCC_000010.cif")
        self.__pathPdbxCifFile = os.path.join(TOPDIR, "rcsb", "mock-data", "MOCK_PDBX_SANDBOX", "du", "1dul", "1dul.cif.gz")
        #
        self.__workPath = os.path.join(HERE, "test-output")
        self.__pathSaveDictionaryFile = os.path.join(self.__workPath, "mmcif_pdbx_v5_next.dic")
        self.__pathSaveJsonTestFile = os.path.join(self.__workPath, "json-content.json")
        self.__pathSaveIndexFile = os.path.join(self.__workPath, "all-pdb-list")
        self.__pathSaveCifFile = os.path.join(self.__workPath, "cif-content.cif")
        self.__pathSaveBcifFile = os.path.join(self.__workPath, "bcif-content.bcif")
        self.__pathSaveBcifFileGz = os.path.join(self.__workPath, "bcif-content.bcif.gz")
        self.__pathSavePickleFile = os.path.join(self.__workPath, "json-content.pic")
        self.__pathSaveTextFile = os.path.join(self.__workPath, "json-content.txt")
        #
        #
        self.__pathInsilicoFile = os.path.join(TOPDIR, "rcsb", "mock-data", "MOCK_EXCHANGE_SANDBOX", "status", "theoretical_model.tsv")
        self.__pathSaveInsilicoFile = os.path.join(self.__workPath, "saved-theoretical_model.tsv")
        #
        # self.__pathVariantFastaFile = os.path.join(self.__mockTopPath, 'UniProt', 'uniprot_sprot_varsplic.fasta.gz')
        self.__pathFastaFile = os.path.join(TOPDIR, "rcsb", "mock-data", "MOCK_EXCHANGE_SANDBOX", "sequence", "pdb_seq_prerelease.fasta")
        self.__pathSaveFastaFile = os.path.join(self.__workPath, "test-pre-release.fasta")
        #
        self.__pathTaxonomyFile = os.path.join(TOPDIR, "rcsb", "mock-data", "NCBI", "names.dmp.gz")
        self.__pathSaveTaxonomyFilePic = os.path.join(self.__workPath, "taxonomy_names.pic")
        self.__pathSaveTaxonomyFileCsv = os.path.join(self.__workPath, "taxonomy_names.csv")
        #
        self.__pathSiftsFile = os.path.join(TOPDIR, "rcsb", "mock-data", "sifts-summary", "pdb_chain_go.csv.gz")
        #
        self.__ioU = IoUtil()
        self.__startTime = time.time()
        logger.debug("Running tests on version %s", __version__)
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    @unittest.skipIf(sys.version_info[0] < 3, "not compatible with Python 2")
    def testReadCsvIter(self):
        """Test returning an iterator for a large CSV file with leading comments"""
        try:
            iCount = 0
            for row in self.__ioU.deserializeCsvIter(self.__pathSiftsFile, delimiter=",", rowFormat="list", encodingErrors="ignore"):
                if len(row) < 6:
                    logger.error("Failing with row %r", row)
                iCount += 1
            self.assertGreater(iCount, 25000000)

            logger.info("Row count is %d", iCount)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteInParts(self):
        """Test the case reading and writing in parts."""
        try:
            self.maxDiff = None
            lenL = 12483
            aL = [100, 200, 300, 400, 500]
            dL = [aL for ii in range(lenL)]
            numParts = 4
            sPath = os.path.join(self.__workPath, "list-data.json")
            ok = self.__ioU.serializeInParts(sPath, dL, numParts, fmt="json", indent=3)
            self.assertTrue(ok)
            rL = self.__ioU.deserializeInParts(sPath, numParts, fmt="json")
            logger.info("Reading %d parts with total length %d", numParts, len(rL))
            self.assertEqual(dL, rL)
            #
            lenD = 20341
            qD = OrderedDict([("a", 100), ("b", 100), ("c", 100)])
            dD = OrderedDict([(str(ii), qD) for ii in range(lenD)])
            numParts = 4
            sPath = os.path.join(self.__workPath, "dict-data.json")
            ok = self.__ioU.serializeInParts(sPath, dD, numParts, fmt="json", indent=3)
            self.assertTrue(ok)
            rD = self.__ioU.deserializeInParts(sPath, numParts, fmt="json")
            logger.info("Reading %d parts with total length %d", numParts, len(rD))
            self.assertDictEqual(dD, rD)
            #
            rD = self.__ioU.deserializeInParts(sPath, None, fmt="json")
            logger.info("Reading %d globbed parts with total length %d", numParts, len(rD))
            self.assertDictEqual(dD, rD)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadDictionaryFile(self):
        """Test the case read PDBx/mmCIF dictionary text file"""
        try:
            cL = self.__ioU.deserialize(self.__pathPdbxDictionaryFile, fmt="mmcif-dict")
            logger.debug("Dictionary container list %d", len(cL))
            self.assertGreaterEqual(len(cL), 1)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadCifFile(self):
        """Test the case read PDBx/mmCIF text file"""
        try:
            cL = self.__ioU.deserialize(self.__pathCifFile, fmt="mmcif")
            logger.debug("Container list %d", len(cL))
            self.assertGreaterEqual(len(cL), 1)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadListFile(self):
        """Test the case read list text file"""
        try:
            cL = self.__ioU.deserialize(self.__pathIndexFile, fmt="list")
            logger.debug("List length %d", len(cL))
            self.assertGreaterEqual(len(cL), 1000)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadJsonFile(self):
        """Test the case read JSON file"""
        try:
            rObj = self.__ioU.deserialize(self.__pathJsonTestFile, fmt="json")
            logger.debug("Object length %d", len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteDictionaryFiles(self):
        """Test the case read and write PDBx/mmCIF dictionary text file"""
        try:
            cL = self.__ioU.deserialize(self.__pathPdbxDictionaryFile, fmt="mmcif-dict")
            logger.debug("Dictionary container list %d", len(cL))
            self.assertGreaterEqual(len(cL), 1)
            ok = self.__ioU.serialize(self.__pathSaveDictionaryFile, cL, fmt="mmcif-dict")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteCifFile(self):
        """Test the case read and write PDBx/mmCIF text file"""
        try:
            cL = self.__ioU.deserialize(self.__pathCifFile, fmt="mmcif")
            logger.debug("Container list %d", len(cL))
            self.assertGreaterEqual(len(cL), 1)
            ok = self.__ioU.serialize(self.__pathSaveCifFile, cL, fmt="mmcif")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteBcifFile(self):
        """Test the case read and write binary PDBx/mmCIF (BCIF) file"""
        try:
            # First read in a normal mmCIF file
            cL1 = self.__ioU.deserialize(self.__pathPdbxCifFile, fmt="mmcif")
            cName1 = cL1[0].getName()
            logger.info("Container list length %d and name %s", len(cL1), cName1)
            self.assertGreaterEqual(len(cL1), 1)
            #
            # Now write it out as a BCIF and BCIF.gz files
            ok = self.__ioU.serialize(self.__pathSaveBcifFile, cL1, fmt="bcif")
            self.assertTrue(ok)
            ok = self.__ioU.serialize(self.__pathSaveBcifFileGz, cL1, fmt="bcif", workPath=self.__workPath)
            self.assertTrue(ok)
            #
            # Now try reading them back in
            cL2 = self.__ioU.deserialize(self.__pathSaveBcifFile, fmt="bcif")
            cName2 = cL2[0].getName()
            logger.info("Container list length %d and name %s", len(cL2), cName2)
            cL3 = self.__ioU.deserialize(self.__pathSaveBcifFileGz, fmt="bcif")
            cName3 = cL3[0].getName()
            logger.info("Container list length %d and name %s", len(cL3), cName3)
            self.assertGreaterEqual(len(cL3), 1)
            #
            # Confirm data all there and retained
            ok = cName1 == cName2 == cName3
            self.assertTrue(ok)
            ok = cL1[0].getObjNameList() == cL2[0].getObjNameList() == cL3[0].getObjNameList()
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteJsonFile(self):
        """Test the case read and write JSON file"""
        try:
            rObj = self.__ioU.deserialize(self.__pathJsonTestFile, fmt="json")
            logger.debug("Object length %d", len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
            ok = self.__ioU.serialize(self.__pathSaveJsonTestFile, rObj, fmt="json")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteListFile(self):
        """Test the case read and write list text file"""
        try:
            cL = self.__ioU.deserialize(self.__pathIndexFile, fmt="list")
            logger.debug("List element %r length %d", cL[0], len(cL))
            self.assertGreaterEqual(len(cL), 1000)
            ok = self.__ioU.serialize(self.__pathSaveIndexFile, cL, fmt="list")
            self.assertTrue(ok)
            count = 0
            for cV in cL:
                fields = cV.split()
                count += len(fields)
            _ = count
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWritePickleFile(self):
        """Test the case read and write pickle file"""
        try:
            rObj = self.__ioU.deserialize(self.__pathJsonTestFile, fmt="json")
            logger.debug("Object length %d", len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
            ok = self.__ioU.serialize(self.__pathSavePickleFile, rObj, fmt="pickle")
            self.assertTrue(ok)
            rObjP = self.__ioU.deserialize(self.__pathSavePickleFile, fmt="pickle")
            self.assertDictEqual(rObj, rObjP)
            ok = self.__ioU.serialize(self.__pathSaveTextFile, rObj, fmt="text-dump")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteListWithEncodingFile(self):
        """Test the case read and write list text file with non-ascii encoding"""
        try:
            cL = self.__ioU.deserialize(self.__pathInsilicoFile, fmt="list")
            logger.debug("Insilico List length %d", len(cL))
            #
            self.assertGreaterEqual(len(cL), 1450)
            #
            ok = self.__ioU.serialize(self.__pathSaveInsilicoFile, cL, fmt="list")
            self.assertTrue(ok)
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteFastaFile(self):
        """Test the case read and write FASTA sequence file"""
        try:
            sD = self.__ioU.deserialize(self.__pathFastaFile, fmt="fasta", commentStyle="prerelease")
            logger.debug("Sequence length %d", len(sD.keys()))
            self.assertGreaterEqual(len(sD), 500)
            ok = self.__ioU.serialize(self.__pathSaveFastaFile, sD, fmt="fasta")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWriteTaxonomyFile(self):
        """Test the case read and write taxonomy resource file"""
        try:
            tL = self.__ioU.deserialize(self.__pathTaxonomyFile, fmt="tdd", rowFormat="list")
            logger.info("Taxonomy length %d", len(tL))
            self.assertGreaterEqual(len(tL), 500)
            tD = {}
            csvL = []
            for tV in tL:
                if len(tV) < 7:
                    continue
                taxId = int(tV[0])
                name = tV[2]
                nameType = tV[6]
                csvL.append({"t": taxId, "name": name, "type": nameType})
                #
                if nameType in ["scientific name", "common name", "synonym", "genbank common name"]:
                    if taxId not in tD:
                        tD[taxId] = {}
                    if nameType in ["scientific name"]:
                        tD[taxId]["sn"] = name
                        continue
                    if "cn" not in tD[taxId]:
                        tD[taxId]["cn"] = []
                    tD[taxId]["cn"].append(name)
                else:
                    pass

            ok = self.__ioU.serialize(self.__pathSaveTaxonomyFilePic, tD, fmt="pickle")
            self.assertTrue(ok)
            ok = self.__ioU.serialize(self.__pathSaveTaxonomyFileCsv, csvL, fmt="csv")
            self.assertTrue(ok)
            tL = self.__ioU.deserialize(self.__pathSaveTaxonomyFileCsv, fmt="csv", rowFormat="dict")
            self.assertTrue(len(tL) > 2880000)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def utilReadSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(IoUtilTests("testReadDictionaryFile"))
    suiteSelect.addTest(IoUtilTests("testReadCifFile"))
    suiteSelect.addTest(IoUtilTests("testReadJsonFile"))
    suiteSelect.addTest(IoUtilTests("testReadListFile"))
    return suiteSelect


def utilReadWriteSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(IoUtilTests("testReadWriteDictionaryFiles"))
    suiteSelect.addTest(IoUtilTests("testReadWriteCifFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteBcifFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteJsonFile"))
    suiteSelect.addTest(IoUtilTests("testReadWritePickleFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteListFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteListWithEncodingFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteFastaFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteTaxonomyFile"))

    return suiteSelect


if __name__ == "__main__":
    #
    mySuite = utilReadSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)

    mySuite = utilReadWriteSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
