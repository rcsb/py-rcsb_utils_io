# File:    FileUtilTests.py
# Author:  J. Westbrook
# Date:    10-Aug-2019
# Version: 0.001
#
# Update:
#
#
##
"""
Tests for file management opereations.

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
from rcsb.utils.io.FileUtil import FileUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FileUtilTests(unittest.TestCase):
    def setUp(self):
        self.__verbose = True
        self.__pathPdbxDictionaryFile = os.path.join(
            TOPDIR, "rcsb", "mock-data", "dictionaries", "mmcif_pdbx_v5_next.dic")

        self.__pathTaxonomyFile = os.path.join(
            TOPDIR, "rcsb", "mock-data", "NCBI", "names.dmp.gz")
        self.__zipFileUrl = "https://inventory.data.gov/dataset/794cd3d7-4d28-4408-8f7d-84b820dbf7f2/resource/6b78ec0c-4980-4ad8-9cbd-2d6eb9eda8e7/download/myfoodapediadata.zip"
        #
        self.__ftpFileUrl = "ftp://ftp.wwpdb.org/pub/pdb/data/component-models/complete/chem_comp_model.cif.gz"
        #
        self.__workPath = os.path.join(HERE, "test-output")
        self.__fileU = FileUtil()
        self.__startTime = time.time()
        logger.debug("Running tests on version %s", __version__)
        logger.debug("Starting %s at %s", self.id(), time.strftime(
            "%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime(
            "%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testGetFile(self):
        """ Test case for a local files and directories
        """
        try:
            remoteLocator = self.__pathPdbxDictionaryFile
            fn = self.__fileU.getFileName(remoteLocator)
            # _, fn = os.path.split(remoteLocator)
            lPath = os.path.join(self.__workPath, fn)
            ok = self.__fileU.get(remoteLocator, lPath)
            self.assertTrue(ok)
            ok = self.__fileU.exists(lPath)
            self.assertTrue(ok)
            ok = self.__fileU.isLocal(lPath)
            self.assertTrue(ok)
            tPath = self.__fileU.getFilePath(lPath)
            self.assertEqual(lPath, tPath)
            ok = self.__fileU.remove(lPath)
            self.assertTrue(ok)
            dPath = os.path.join(self.__workPath, "tdir")
            ok = self.__fileU.mkdir(dPath)
            self.assertTrue(ok)
            ok = self.__fileU.remove(dPath)
            self.assertTrue(ok)
            ok = self.__fileU.remove(";lakdjf")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testZipUrl(self):
        """ Test case for downloading remote zip file and extracting contents.
        """
        try:
            remoteLocator = self.__zipFileUrl
            # fn = self.__fileU.getFileName(remoteLocator)
            ok = self.__fileU.isLocal(remoteLocator)
            self.assertFalse(ok)
            #
            lPath = os.path.join(
                self.__workPath, self.__fileU.getFileName(self.__zipFileUrl))
            ok = self.__fileU.get(remoteLocator, lPath)
            self.assertTrue(ok)
            ok = self.__fileU.exists(lPath)
            self.assertTrue(ok)
            ok = self.__fileU.isLocal(lPath)
            self.assertTrue(ok)
            tPath = self.__fileU.getFilePath(lPath)
            self.assertEqual(lPath, tPath)
            fp = self.__fileU.uncompress(lPath, outputDir=self.__workPath)
            ok = fp.endswith("Food_Display_Table.xlsx")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testFtpUrl(self):
        """ Test case for downloading remote file ftp protocol and extracting contents.
        """
        try:
            remoteLocator = self.__ftpFileUrl
            # fn = self.__fileU.getFileName(remoteLocator)
            ok = self.__fileU.isLocal(remoteLocator)
            self.assertFalse(ok)
            #
            dirPath = os.path.join(self.__workPath, "chem_comp_models")
            lPath = os.path.join(
                dirPath, self.__fileU.getFileName(self.__ftpFileUrl))
            ok = self.__fileU.get(remoteLocator, lPath)
            self.assertTrue(ok)
            ok = self.__fileU.exists(lPath)
            self.assertTrue(ok)
            ok = self.__fileU.isLocal(lPath)
            self.assertTrue(ok)
            tPath = self.__fileU.getFilePath(lPath)
            self.assertEqual(lPath, tPath)
            fp = self.__fileU.uncompress(lPath, outputDir=dirPath)
            ok = fp.endswith("chem_comp_model.cif")
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    @unittest.skip("DrugBank example -- skipping")
    def testGetDrugBankUrl(self):
        """ Test case for downloading drugbank master xml file
        """
        try:
            remoteLocator = "https://www.drugbank.ca/releases/latest/downloads/all-full-database"
            un = "username"
            pw = "password"
            # fn = self.__fileU.getFileName(remoteLocator)
            ok = self.__fileU.isLocal(remoteLocator)
            self.assertFalse(ok)
            #
            lPath = os.path.join(self.__workPath, "db-download.zip")
            ok = self.__fileU.get(remoteLocator, lPath,
                                  username=un, password=pw)
            self.assertTrue(ok)
            ok = self.__fileU.exists(lPath)
            self.assertTrue(ok)
            ok = self.__fileU.isLocal(lPath)
            self.assertTrue(ok)
            tPath = self.__fileU.getFilePath(lPath)
            self.assertEqual(lPath, tPath)
            self.__fileU.uncompress(lPath, outputDir=self.__workPath)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def utilSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(FileUtilTests("testGetFile"))
    suiteSelect.addTest(FileUtilTests("testFtpUrls"))
    return suiteSelect


if __name__ == "__main__":
    #
    mySuite = utilSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
