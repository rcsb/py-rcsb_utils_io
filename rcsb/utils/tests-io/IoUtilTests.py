# File:    IoUtilTests.py
# Author:  J. Westbrook
# Date:    22-May-2013
# Version: 0.001
#
# Update:
#  23-May-2018  jdw add preliminary default and helper tests
#   5-Jun-2018  jdw update prototypes for IoUtil() methods
#  13-Jun-2018  jdw add content classes
#  25-Nov-2018  jdw add FASTA tests
#  30-Nov-2018  jdw add CSV tests
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
from rcsb.utils.io.IoUtil import IoUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class IoUtilTests(unittest.TestCase):

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
        self.__pathSavePickleFile = os.path.join(HERE, 'test-output', 'rcsb_extend_provenance_info.pic')
        self.__pathSaveTextFile = os.path.join(HERE, 'test-output', 'rcsb_extend_provenance_info.txt')
        #
        #
        self.__pathInsilicoFile = os.path.join(TOPDIR, 'rcsb', 'mock-data', 'MOCK_EXCHANGE_SANDBOX', 'status', 'theoretical_model.tsv')
        self.__pathSaveInsilicoFile = os.path.join(HERE, 'test-output', 'saved-theoretical_model.tsv')
        #
        # self.__pathVariantFastaFile = os.path.join(self.__mockTopPath, 'UniProt', 'uniprot_sprot_varsplic.fasta.gz')
        self.__pathFastaFile = os.path.join(TOPDIR, 'rcsb', 'mock-data', 'MOCK_EXCHANGE_SANDBOX', 'sequence', 'pdb_seq_prerelease.fasta')
        self.__pathSaveFastaFile = os.path.join(HERE, 'test-output', 'test-pre-release.fasta')
        #
        self.__pathTaxonomyFile = os.path.join(TOPDIR, 'rcsb', 'mock-data', 'NCBI', 'names.dmp.gz')
        self.__pathSaveTaxonomyFilePic = os.path.join(HERE, 'test-output', 'taxonomy_names.pic')
        self.__pathSaveTaxonomyFileCsv = os.path.join(HERE, 'test-output', 'taxonomy_names.csv')
        #
        self.__ioU = IoUtil()
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
            cL = self.__ioU.deserialize(self.__pathPdbxDictionaryFile, format="mmcif-dict")
            logger.debug("Dictionary container list %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadCifFile(self):
        """ Test the case read PDBx/mmCIF text file
        """
        try:
            cL = self.__ioU.deserialize(self.__pathCifFile, format="mmcif")
            logger.debug("Container list %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadListFile(self):
        """ Test the case read list text file
        """
        try:
            cL = self.__ioU.deserialize(self.__pathIndexFile, format="list")
            logger.debug("List length %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1000)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadJsonFile(self):
        """ Test the case read JSON file
        """
        try:
            rObj = self.__ioU.deserialize(self.__pathProvenanceFile, format="json")
            logger.debug("Object length %d" % len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteDictionaryFiles(self):
        """ Test the case read and write PDBx/mmCIF dictionary text file
        """
        try:
            cL = self.__ioU.deserialize(self.__pathPdbxDictionaryFile, format="mmcif-dict")
            logger.debug("Dictionary container list %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1)
            ok = self.__ioU.serialize(self.__pathSaveDictionaryFile, cL, format="mmcif-dict")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteCifFile(self):
        """ Test the case read and write PDBx/mmCIF text file
        """
        try:
            cL = self.__ioU.deserialize(self.__pathCifFile, format="mmcif")
            logger.debug("Container list %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1)
            ok = self.__ioU.serialize(self.__pathSaveCifFile, cL, format="mmcif")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteJsonFile(self):
        """ Test the case read and write JSON file
        """
        try:
            rObj = self.__ioU.deserialize(self.__pathProvenanceFile, format="json")
            logger.debug("Object length %d" % len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
            ok = self.__ioU.serialize(self.__pathSaveProvenanceFile, rObj, format="json")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteListFile(self):
        """ Test the case read and write list text file
        """
        try:
            cL = self.__ioU.deserialize(self.__pathIndexFile, format="list")
            logger.debug("List length %d" % len(cL))
            self.assertGreaterEqual(len(cL), 1000)
            ok = self.__ioU.serialize(self.__pathSaveIndexFile, cL, format="list")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWritePickleFile(self):
        """ Test the case read and write pickle file
        """
        try:
            rObj = self.__ioU.deserialize(self.__pathProvenanceFile, format="json")
            logger.debug("Object length %d" % len(rObj))
            self.assertGreaterEqual(len(rObj), 1)
            ok = self.__ioU.serialize(self.__pathSavePickleFile, rObj, format="pickle")
            self.assertTrue(ok)
            rObjP = self.__ioU.deserialize(self.__pathSavePickleFile, format="pickle")
            self.assertDictEqual(rObj, rObjP)
            ok = self.__ioU.serialize(self.__pathSaveTextFile, rObj, format="text-dump")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteListWithEncodingFile(self):
        """ Test the case read and write list text file with non-ascii encoding
        """
        try:
            cL = self.__ioU.deserialize(self.__pathInsilicoFile, format="list")
            logger.debug("Insilico List length %d" % len(cL))
            #
            self.assertGreaterEqual(len(cL), 1450)
            #
            ok = self.__ioU.serialize(self.__pathSaveInsilicoFile, cL, format="list")
            self.assertTrue(ok)
            #
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteFastaFile(self):
        """ Test the case read and write FASTA sequence file
        """
        try:
            sD = self.__ioU.deserialize(self.__pathFastaFile, format="fasta", commentStyle='prerelease')
            logger.debug("Sequence length %d" % len(sD))
            self.assertGreaterEqual(len(sD), 940)
            ok = self.__ioU.serialize(self.__pathSaveFastaFile, sD, format="fasta")
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
            self.fail()

    def testReadWriteTaxonomyFile(self):
        """ Test the case read and write taxonomy resource file
        """
        try:
            tL = self.__ioU.deserialize(self.__pathTaxonomyFile, format="tdd", rowFormat='list')
            logger.info("Taxonomy length %d" % len(tL))
            self.assertGreaterEqual(len(tL), 940)
            tD = {}
            csvL = []
            for t in tL:
                if len(t) < 7:
                    continue
                taxId = int(t[0])
                name = t[2]
                nameType = t[6]
                csvL.append({'t': taxId, 'name': name, 'type': nameType})
                #
                if nameType in ['scientific name', 'common name', 'synonym', 'genbank common name']:
                    if taxId not in tD:
                        tD[taxId] = {}
                    if nameType in ['scientific name']:
                        tD[taxId]['sn'] = name
                        continue
                    if 'cn' not in tD[taxId]:
                        tD[taxId]['cn'] = []
                    tD[taxId]['cn'].append(name)
                else:
                    pass

            ok = self.__ioU.serialize(self.__pathSaveTaxonomyFilePic, tD, format="pickle")
            self.assertTrue(ok)
            ok = self.__ioU.serialize(self.__pathSaveTaxonomyFileCsv, csvL, format="csv")
            self.assertTrue(ok)
            tL = self.__ioU.deserialize(self.__pathSaveTaxonomyFileCsv, format='csv', rowFormat='dict')
            self.assertTrue(len(tL) > 2880000)
        except Exception as e:
            logger.exception("Failing with %s" % str(e))
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
    suiteSelect.addTest(IoUtilTests("testReadWriteJsonFile"))
    suiteSelect.addTest(IoUtilTests("testReadWritePickleFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteListFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteListWithEncodingFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteFastaFile"))
    suiteSelect.addTest(IoUtilTests("testReadWriteTaxonomyFile"))

    return suiteSelect


if __name__ == '__main__':
    #
    if True:
        mySuite = utilReadSuite()
        unittest.TextTestRunner(verbosity=2).run(mySuite)
    #
    if True:
        mySuite = utilReadWriteSuite()
        unittest.TextTestRunner(verbosity=2).run(mySuite)
