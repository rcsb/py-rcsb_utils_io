##
# File:    IndexUtils.py
# Author:  jdw
# Date:    20-June-2016
# Version: 0.001
#
# Updates:
#    22-Jun-2016 jdw add CcdcMatchIndex/Inst() classes -
#    28-Jul-2017 jdw add PdbxChemCompIndex and PdbxChemCompIndexInst classes -
#    28-Jul-2017 jdw change variant_id to target_id in the ccdc results index
#    12-Jan-2021 jdw Py39 cleanup
#    20-Jan-2021 jdw move to rcsb.utils.io and cleanup
##
"""
IndexUtils() implements a simple iterator over a linear index of objects -

"""
__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging
import sys
import os

from rcsb.utils.io.MarshalUtil import MarshalUtil

logger = logging.getLogger(__name__)


class IndexBase(object):
    """Base iterator class."""

    def __init__(self, indexFilePath, func, verbose=True):
        self._verbose = verbose
        self._debug = False
        self._rL = []
        self.__func = func
        self.__fmt = "json"
        self._indexFilePath = indexFilePath
        self._indexPath, self._indexFileName = os.path.split(self._indexFilePath)

    def get(self, index=0):
        try:
            return self._rL[index]
        except Exception:
            return []

    def __iter__(self):
        return self.forward()

    def forward(self):
        # Forward generator
        currentRow = 0
        while currentRow < len(self._rL):
            row = self._rL[currentRow]
            currentRow += 1
            yield self.__func(row)

    def reverse(self):
        # The reverse generator
        currentRow = len(self._rL)
        while currentRow > 0:
            currentRow -= 1
            yield self.__func(self._rL[currentRow])

    def clear(self):
        self._rL = []
        return True

    def writeIndex(self):
        try:
            mU = MarshalUtil()
            ok = mU.doExport(self._indexFilePath, self._rL, fmt=self.__fmt, indent=3)
            return ok
        except Exception as e:
            logger.error("Failing with %s", str(e))

        return False

    def readIndex(self):
        try:
            mU = MarshalUtil()
            if not mU.exists(self._indexFilePath):
                return False
            indexObj = mU.doImport(self._indexFilePath, fmt=self.__fmt)
            if indexObj is not None and len(indexObj) > 0:
                self._rL.extend(indexObj)
            return True
        except Exception as e:
            logger.error("Failing with %s", str(e))

        return False

    def load(self, rowList):
        self._rL.extend(rowList)

    def dump(self):
        for ii, dD in enumerate(self._rL):
            logger.info("%4d: %r", ii, dD)
        logger.info("Completed dump")

    def sort(self, atName="identifier", descending=False):
        try:
            self._rL = sorted(self._rL, key=lambda k: k[atName], reverse=descending)
            return True
        except Exception:
            pass
        return False


class CcdcMatchIndex(IndexBase):
    def __init__(self, indexFilePath=None, verbose=True):
        obj = CcdcMatchIndexInst(None, verbose=verbose)
        super(CcdcMatchIndex, self).__init__(indexFilePath, obj.set, verbose)
        #
        self.readIndex()
        if self._debug:
            self.dump()


class CcdcMatchIndexInst(object):
    """Accessor methods for CCDC match index elements."""

    def __init__(self, dObj=None, verbose=True, log=sys.stderr):
        self.__verbose = verbose
        self._lfh = log
        self.__dObj = dObj if dObj is not None else {}

    def __getAttribute(self, name):
        try:
            return self.__dObj[name]
        except Exception:
            return None

    def set(self, dObj=None):
        self.__dObj = dObj
        return self

    def get(self):
        return self.__dObj

    def getCsdVersion(self):
        return self.__getAttribute("csd_version")

    def getCsdDirectory(self):
        return self.__getAttribute("csd_directory")

    def getIdentifier(self):
        return self.__getAttribute("identifier")

    def getChemicalName(self):
        return self.__getAttribute("chemical_name")

    def getTargetId(self):
        return self.__getAttribute("target_id")

    def getTargetPath(self):
        return self.__getAttribute("target_path")

    def getTargetCcPath(self):
        return self.__getAttribute("target_cc_path")

    def getMatchType(self):
        return self.__getAttribute("match_type")

    def getMatchNumber(self):
        return self.__getAttribute("match_number")

    def getMol2Path(self):
        return self.__getAttribute("mol2_file_path")

    def getMolPath(self):
        return self.__getAttribute("mol_file_path")

    #

    def getRFactor(self):
        return self.__getAttribute("r_factor")

    def getTemperature(self):
        return self.__getAttribute("temperature")

    def getRadiationSource(self):
        return self.__getAttribute("radiation_source")

    def getCitationDOI(self):
        return self.__getAttribute("doi")

    def getMatchedAtomLength(self):
        return self.__getAttribute("match_atoms")

    def getHasDisorder(self):
        return self.__getAttribute("has_disorder")

    def getSimilarityScore(self):
        return self.__getAttribute("similarity")

    #
    def setCsdVersion(self, v):
        self.__dObj["csd_version"] = v

    def setCsdDirectory(self, v):
        self.__dObj["csd_directory"] = v

    def setIdentifier(self, v):
        self.__dObj["identifier"] = v

    def setChemicalName(self, name):
        self.__dObj["chemical_name"] = name

    def setTargetId(self, ccId):
        self.__dObj["target_id"] = ccId

    def setTargetPath(self, pth):
        self.__dObj["target_path"] = pth

    def setTargetCcPath(self, pth):
        self.__dObj["target_cc_path"] = pth

    def setMatchType(self, v):
        self.__dObj["match_type"] = v

    def setMatchNumber(self, v):
        self.__dObj["match_number"] = v

    def setMolPath(self, fp):
        self.__dObj["mol_file_path"] = fp

    def setMol2Path(self, fp):
        self.__dObj["mol2_file_path"] = fp

    def setRFactor(self, rv):
        self.__dObj["r_factor"] = rv

    def setTemperature(self, tv):
        self.__dObj["temperature"] = tv

    def setRadiationSource(self, sv):
        self.__dObj["radiation_source"] = sv

    def setSimilarityScore(self, sv):
        self.__dObj["similarity_score"] = sv

    def setMatchedAtomLength(self, lv):
        self.__dObj["match_atoms"] = lv

    def setHasDisorder(self, lv):
        self.__dObj["has_disorder"] = lv

    def setCitationDOI(self, doi):
        self.__dObj["doi"] = doi

    def __repr__(self):
        return str(self.__dObj)

    def __str__(self):
        return str(self.__dObj)
