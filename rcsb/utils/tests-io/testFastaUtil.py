##
# File:    FastaUtilTests.py
# Author:  J. westbrook
# Date:    24-Nov-2018
#
# Update:
##
"""
Test cases for reading various Fasta format sequence data files -

"""

import logging
import os
import string
import unittest

from rcsb.utils.io.FastaUtil import FastaUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FastaUtilTests(unittest.TestCase):
    def setUp(self):
        self.__mockTopPath = os.path.join(TOPDIR, "rcsb", "mock-data")
        self.__variantFastaFilePath = os.path.join(self.__mockTopPath, "UniProt", "uniprot_sprot_varsplic.fasta.gz")
        self.__preReleaseFastaFilePath = os.path.join(self.__mockTopPath, "MOCK_EXCHANGE_SANDBOX", "sequence", "pdb_seq_prerelease.fasta")
        self.__outputFastaFilePath = os.path.join(HERE, "test-output", "test-pre-release.fasta")
        #
        self.__unpIdListV = ["P42284-1", "P42284-3", "P29994-2", "P29994-3", "P29994-4", "P29994-5", "P29994-6", "P29994-7"]

    def tearDown(self):
        pass

    def __cleanString(self, strIn):
        sL = []
        for ss in strIn:
            if ss in string.whitespace:
                continue
            sL.append(ss)
        return "".join(sL)

    def testReadUniProtFasta(self):
        """
        """
        try:
            iMiss = 0
            fau = FastaUtil()
            sD = fau.readFasta(self.__variantFastaFilePath, commentStyle="uniprot")
            for uid in self.__unpIdListV:
                if uid in sD:
                    logger.debug(
                        "id %s accession %s isoform %s description %s gene %s org %s length sequence %d",
                        uid,
                        sD[uid]["db_accession"],
                        sD[uid]["db_isoform"],
                        sD[uid]["description"],
                        sD[uid]["gene_name"],
                        sD[uid]["org"],
                        len(self.__cleanString(sD[uid]["sequence"])),
                    )

                    # logger.info("%r\n" % self.__cleanString(sD[uid]['sequence']))
                    logger.debug("%r", sD[uid]["sequence"])
                else:
                    iMiss += 1
                    logger.error("Miss %r", uid)

            self.assertEqual(iMiss, 0)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testReadWritePreReleaseFasta(self):
        """
        """
        try:
            fau = FastaUtil()
            sD = fau.readFasta(self.__preReleaseFastaFilePath, commentStyle="prerelease")
            for uid, d in sD.items():
                # logger.info("%r\n" % self.__cleanString(sD[uid]['sequence']))
                logger.debug("%r %r", uid, d["sequence"])
            logger.debug("length is %d", len(sD))
            self.assertGreaterEqual(len(sD), 940)
            ##
            ok = fau.writeFasta(self.__outputFastaFilePath, sD)
            self.assertTrue(ok)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def suiteReadTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(FastaUtilTests("testReadUniProtFasta"))
    suiteSelect.addTest(FastaUtilTests("testReadWritePreReleaseFasta"))
    #
    return suiteSelect


if __name__ == "__main__":

    mySuite = suiteReadTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
    #
