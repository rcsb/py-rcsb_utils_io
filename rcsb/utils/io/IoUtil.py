##
# File: IoUtil.py
#
# Updates:
#   2-Feb-2018  jdw add default return values for deserialize ops
#   3-Feb-2018  jdw pickle -> pickle  - make default return {} if not specified
#  14-Feb-2018  jdw add fix for the new location of XmlToObj module
#  20-May-2018  jdw move to this module
#   3-Jun-2018  jdw add serializeMmCif/deserializeMmCif
#   4-Jun-2018  jdw overhaul api - provide two public methods.
#   4-Jun-2018  jdw add format for dictionaries which require special parsing
#  15-Jun-2018  jdw add textDump (pretty printer) serialization method -
#  28-Sep-2018  jdw add helper class for serializing python date/datetime types
#   8-Oct-2018  jdw add convenience function to test for file existence
#  11-Oct-2018  jdw make encoding utf-8 for lists
#  13-Oct-2018  jdw add Py27 support for explicit encoding using io.open.
#  26-Oct-2018  jdw add additional JSON encodings for yaml data types
#  25-Nov-2018  jdw add support for FASTA format sequence files
#  30-Nov-2018  jdw add support CSV file formats
#  11-Dec-2018  jdw add comment filtering on input for CSV files
#   5-Feb-2019  jdw add support for gzip compression as part of serializing mmCIF files.
#   6-Feb-2019  jdw add vrpt-xml-to-cif option and supporting method __deserializeVrptToCif()
#  24-Mar-2019  jdw suppress error message on missing validation report file.
#  25-Mar-2019  jdw expose comment processing for csv/tdd files as keyword argument
#   3-Apr-2019  jdw add comment option and compression handling to __deserializeList()
#  11-Jul-2019  jdw add explicit py2 safe file decompression to avoid encoding problems.
#  10-Aug-2019  jdw add XML/ElementTree reader
#  13-Aug-2019  jdw add serialization/deserialization in parts
#  18-Sep-2019  jdw add method deserializeCsvIter()
#  17-Sep-2021  jdw add an explicit file test for gzip compression to avoid problems with uncompressed files.
#  28-Mar-2022  dwp remove deprecated xml.etree.cElementTree module
##

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import csv
import datetime
import glob
import gzip
import io
import itertools
import json
import logging
import os
import pickle
import pprint
import random
import string
import sys
import time
from collections import OrderedDict

import numpy
import requests
import ruamel.yaml
import xml.etree.ElementTree as ET

from mmcif.io.IoAdapterPy import IoAdapterPy
from rcsb.utils.io.decorators import retry
from rcsb.utils.io.FastaUtil import FastaUtil
from rcsb.utils.io.FileUtil import FileUtil


try:
    from mmcif.io.IoAdapterCore import IoAdapterCore as IoAdapter  # pylint: disable=ungrouped-imports
except Exception:
    from mmcif.io.IoAdapterPy import IoAdapterPy as IoAdapter  # pylint: disable=reimported,ungrouped-imports


logger = logging.getLogger(__name__)


def uncommentFilter(csvfile):
    for row in csvfile:
        raw = row.split("#")[0].strip()
        if raw:
            yield raw


def getObjSize(obj, seen=None):
    """Report the size of the input object"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    objId = id(obj)
    if objId in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(objId)
    if isinstance(obj, dict):
        size += sum([getObjSize(v, seen) for v in obj.values()])
        size += sum([getObjSize(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += getObjSize(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([getObjSize(i, seen) for i in obj])
    return size


class JsonTypeEncoder(json.JSONEncoder):
    """Helper class to handle serializing date and time objects"""

    # pylint: disable=method-hidden,protected-access
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        if isinstance(o, datetime.date):
            return o.isoformat()

        # if isinstance(o, tuple):
        #    return list(o)

        if isinstance(o, ruamel.yaml.comments.CommentedMap):
            return o._od

        if isinstance(o, ruamel.yaml.comments.CommentedSeq):
            return o._lst

        if isinstance(o, numpy.integer):
            return int(o)

        if isinstance(o, numpy.floating):
            return float(o)

        if isinstance(o, numpy.ndarray):
            return o.tolist()

        return json.JSONEncoder.default(self, o)


class IoUtil(object):
    def __init__(self, **kwargs):
        self.__fileU = FileUtil(**kwargs)

    def serialize(self, filePath, myObj, fmt="pickle", **kwargs):
        """Public method to serialize format appropriate objects

        Args:
            filePath (str): local file path'
            myObj (object): format appropriate object to be serialized
            format (str, optional): one of ['mmcif', mmcif-dict', json', 'list', 'text-dump', pickle' (default)]
            **kwargs: additional keyword arguments passed to worker methods -

        Returns:
            bool: status of serialization operation; true for success or false otherwise

        """
        ret = False
        fmt = str(fmt).lower()
        ret = self.__fileU.mkdirForFile(filePath)
        if not ret:
            return ret
        if fmt in ["mmcif"]:
            ret = self.__serializeMmCif(filePath, myObj, **kwargs)
        elif fmt in ["json"]:
            ret = self.__serializeJson(filePath, myObj, **kwargs)
        elif fmt in ["pickle"]:
            ret = self.__serializePickle(filePath, myObj, **kwargs)
        elif fmt in ["list"]:
            ret = self.__serializeList(filePath, myObj, enforceAscii=True, **kwargs)
        elif fmt in ["mmcif-dict"]:
            ret = self.__serializeMmCifDict(filePath, myObj, **kwargs)
        elif fmt in ["text-dump"]:
            ret = self.__textDump(filePath, myObj, **kwargs)
        elif fmt in ["fasta"]:
            ret = self.__serializeFasta(filePath, myObj, **kwargs)
        elif fmt in ["csv"]:
            ret = self.__serializeCsv(filePath, myObj, **kwargs)
        else:
            pass

        return ret

    def deserialize(self, filePath, fmt="pickle", **kwargs):
        """Public method to deserialize objects in supported formats.

        Args:
            filePath (str): local file path
            format (str, optional): one of ['mmcif', 'json', 'list', ..., 'pickle' (default)]
            **kwargs:  additional keyword arguments passed to worker methods -

        Returns:
            object: deserialized object data

        """
        fmt = str(fmt).lower()
        if fmt in ["mmcif"]:
            ret = self.__deserializeMmCif(filePath, **kwargs)  # type: ignore
        elif fmt in ["json"]:
            ret = self.__deserializeJson(filePath, **kwargs)  # type: ignore
        elif fmt in ["pickle"]:
            ret = self.__deserializePickle(filePath, **kwargs)  # type: ignore
        elif fmt in ["list"]:
            ret = self.__deserializeList(filePath, enforceAscii=True, **kwargs)  # type: ignore
        elif fmt in ["mmcif-dict"]:
            ret = self.__deserializeMmCifDict(filePath, **kwargs)  # type: ignore
        elif fmt in ["fasta"]:
            ret = self.__deserializeFasta(filePath, **kwargs)  # type: ignore
        # elif fmt in ["vrpt-xml-to-cif"]:
        #    ret = self.__deserializeVrptToCif(filePath, **kwargs)  # type: ignore
        elif fmt in ["csv", "tdd"]:
            delimiter = kwargs.get("csvDelimiter", "," if fmt == "csv" else "\t")
            ret = self.__deserializeCsv(filePath, delimiter=delimiter, **kwargs)  # type: ignore
        elif fmt in ["xml"]:
            ret = self.__deserializeXml(filePath, **kwargs)  # type: ignore
        else:
            ret = None  # type: ignore

        return ret

    def __sliceInChunks(self, myList, numChunks):
        mc = min(len(myList), numChunks)
        chunkSize = int(len(myList) / mc)
        if len(myList) % mc:
            chunkSize += 1
        for i in range(0, len(myList), chunkSize):
            yield myList[i:i + chunkSize]

    def serializeInParts(self, filePath, myObj, numParts, fmt="json", **kwargs):
        """Public method to serialize format appropriate (json, pickle) objects in multiple parts

        Args:
            filePath (str): local file path
            myObj (object): format appropriate object to be serialized
            numParts (int): divide the data into numParts segments
            format (str, optional): one of ['json' or 'pickle']. Defaults to json
            **kwargs: additional keyword arguments passed to worker methods -

        Returns:
            bool: True for success or False otherwise
        """
        if fmt not in ["json", "pickle"]:
            logger.error("Unsupported format for %s", fmt)
            return False
        pth, fn = os.path.split(filePath)
        self.__fileU.mkdirForFile(pth)
        bn, ext = os.path.splitext(fn)
        ret = True
        if isinstance(myObj, list):
            for ii, subList in enumerate(self.__sliceInChunks(myObj, numParts)):
                fp = os.path.join(pth, bn + "_part_%d" % (ii + 1) + ext)
                ok = self.serialize(fp, subList, fmt=fmt, **kwargs)
                ret = ret and ok
        elif isinstance(myObj, dict):
            for ii, keyList in enumerate(self.__sliceInChunks(list(myObj.keys()), numParts)):
                fp = os.path.join(pth, bn + "_part_%d" % (ii + 1) + ext)
                ok = self.serialize(fp, OrderedDict([(k, myObj[k]) for k in keyList]), fmt=fmt, **kwargs)
                ret = ret and ok
        else:
            logger.error("Unsupported data type for serialization in parts")
            ret = False
        #
        return ret

    def deserializeInParts(self, filePath, numParts, fmt="json", **kwargs):
        """Public method to deserialize objects in supported formats from multiple parts

        Args:
            filePath (str): local file path
            numParts (int): reconstruct the data object from numParts segments
            format (str, optional): one of ['json' or 'pickle']. Defaults to json
            **kwargs: additional keyword arguments passed to worker methods -

        Returns:
            object: deserialized object data
        """
        rObj = None
        if fmt not in ["json", "pickle"]:
            logger.error("Unsupported format for %s", fmt)
            return rObj
        #
        pth, fn = os.path.split(filePath)
        bn, ext = os.path.splitext(fn)
        if not numParts:
            fp = os.path.join(pth, bn + "_part_*" + ext)
            numParts = len(glob.glob(fp))
        #
        for ii in range(numParts):
            fp = os.path.join(pth, bn + "_part_%d" % (ii + 1) + ext)
            tObj = self.deserialize(fp, fmt=fmt, **kwargs)
            if isinstance(tObj, list):
                if not rObj:
                    rObj = []
                rObj.extend(tObj)
            elif isinstance(tObj, dict):
                if not rObj:
                    rObj = OrderedDict()
                rObj.update(tObj)
            else:
                logger.error("Unsupported data type for deserialization in parts")
        return rObj

    def exists(self, filePath, mode=os.R_OK):
        return self.__fileU.exists(filePath, mode=mode)

    def mkdir(self, dirPath, mode=0o755):
        return self.__fileU.mkdir(dirPath, mode=mode)

    def remove(self, pth):
        return self.__fileU.remove(pth)

    def __deserializeFasta(self, filePath, **kwargs):
        try:
            commentStyle = kwargs.get("commentStyle", "uniprot")
            fau = FastaUtil()
            return fau.readFasta(filePath, commentStyle=commentStyle)
        except Exception as e:
            logger.error("Unable to deserialize %r %r ", filePath, str(e))
        return {}

    def __serializeFasta(self, filePath, myObj, **kwargs):
        try:
            maxLineLength = int(kwargs.get("maxLineLength", 70))
            makeComment = kwargs.get("makeComment", False)
            fau = FastaUtil()
            ok = fau.writeFasta(filePath, myObj, maxLineLength=maxLineLength, makeComment=makeComment)
            return ok
        except Exception as e:
            logger.error("Unable to serialize FASTA file %r  %r", filePath, str(e))
        return False

    def __textDump(self, filePath, myObj, **kwargs):
        try:
            indent = kwargs.get("indent", 1)
            width = kwargs.get("width", 120)
            sOut = pprint.pformat(myObj, indent=indent, width=width)
            with open(filePath, "w") as ofh:
                ofh.write("\n%s\n" % sOut)
            return True
        except Exception as e:
            logger.error("Unable to dump to %r  %r", filePath, str(e))
        return False

    def __serializePickle(self, filePath, myObj, **kwargs):
        try:
            pickleProtocol = kwargs.get("pickleProtocol", pickle.DEFAULT_PROTOCOL)

            with open(filePath, "wb") as outfile:
                pickle.dump(myObj, outfile, pickleProtocol)
            return True
        except Exception as e:
            logger.error("Unable to serialize %r  %r", filePath, str(e))
        return False

    def __deserializePickle(self, filePath, **kwargs):
        myDefault = kwargs.get("default", {})
        try:
            if sys.version_info[0] > 2:
                encoding = kwargs.get("encoding", "ASCII")
                errors = kwargs.get("errors", "strict")
                with open(filePath, "rb") as outfile:
                    return pickle.load(outfile, encoding=encoding, errors=errors)
            else:
                with open(filePath, "rb") as outfile:
                    return pickle.load(outfile)
        except Exception as e:
            logger.warning("Unable to deserialize %r %r", filePath, str(e))
        return myDefault

    def __serializeJson(self, filePath, myObj, **kwargs):
        """Internal method to serialize the input object as JSON.  An encoding
        helper class is included to handle selected python data types (e.g., datetime)
        """
        indent = kwargs.get("indent", 0)
        enforceAscii = kwargs.get("enforceAscii", True)
        try:
            if enforceAscii:
                with open(filePath, "w") as outfile:
                    json.dump(myObj, outfile, indent=indent, cls=JsonTypeEncoder, ensure_ascii=enforceAscii)
            else:
                with io.open(filePath, "w", encoding="utf-8") as outfile:
                    json.dump(myObj, outfile, indent=indent, cls=JsonTypeEncoder, ensure_ascii=enforceAscii)
            return True
        except Exception as e:
            logger.error("Unable to serialize %r  %r", filePath, str(e))
        return False

    def __deserializeJson(self, filePath, **kwargs):
        myDefault = kwargs.get("default", {})
        encoding = kwargs.get("encoding", "utf-8-sig")
        encodingErrors = kwargs.get("encodingErrors", "ignore")
        try:
            if filePath[-3:] == ".gz":
                if sys.version_info[0] > 2:
                    with gzip.open(filePath, "rt", encoding=encoding, errors=encodingErrors) as inpFile:
                        return json.load(inpFile, object_pairs_hook=OrderedDict)
                else:
                    # Py2 situation non-ascii encodings is problematic
                    # with gzip.open(filePath, "rb") as csvFile:
                    #    oL = self.__csvReader(csvFile, rowFormat, delimiter)
                    tPath = self.__fileU.uncompress(filePath, outputDir=None)
                    with io.open(tPath, newline="", encoding=encoding, errors="ignore") as inpFile:
                        return json.load(inpFile, object_pairs_hook=OrderedDict)
            else:
                with open(filePath, "r") as inpFile:
                    return json.load(inpFile, object_pairs_hook=OrderedDict)
        except Exception as e:
            logger.warning("Unable to deserialize %r %r", filePath, str(e))
        return myDefault

    def __hasMinSize(self, pth, minSize):
        try:
            return os.path.getsize(pth) >= minSize
        except Exception:
            return False

    def __deserializeMmCif(self, locator, **kwargs):
        """ """
        try:
            containerList = []
            workPath = kwargs.get("workPath", None)
            enforceAscii = kwargs.get("enforceAscii", True)
            raiseExceptions = kwargs.get("raiseExceptions", True)
            useCharRefs = kwargs.get("useCharRefs", True)
            minSize = kwargs.get("minSize", 5)
            #
            if self.__fileU.isLocal(locator):
                if minSize >= 0 and not self.__hasMinSize(locator, minSize):
                    logger.warning("Minimum file size not satisfied for: %r", locator)
                myIo = IoAdapter(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
                containerList = myIo.readFile(locator, enforceAscii=enforceAscii, outDirPath=workPath)  # type: ignore
            else:
                # myIo = IoAdapterPy(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
                # containerList = myIo.readFile(locator, enforceAscii=enforceAscii, outDirPath=workPath)
                containerList = self.__deserializeMmCifRemote(locator, useCharRefs, enforceAscii, workPath)

        except Exception as e:
            logger.error("Failing for %s with %s", locator, str(e))
        return containerList

    @retry((requests.exceptions.RequestException), maxAttempts=3, delaySeconds=1, multiplier=2, defaultValue=[], logger=logger)
    def __deserializeMmCifRemote(self, locator, useCharRefs, enforceAscii, workPath):
        containerList = []
        try:
            myIo = IoAdapterPy(raiseExceptions=True, useCharRefs=useCharRefs)
            containerList = myIo.readFile(locator, enforceAscii=enforceAscii, outDirPath=workPath)
        except Exception as e:
            raise e
        return containerList

    def __serializeMmCif(self, filePath, containerList, **kwargs):
        """ """
        try:
            ret = False
            workPath = kwargs.get("workPath", None)
            enforceAscii = kwargs.get("enforceAscii", True)
            raiseExceptions = kwargs.get("raiseExceptions", True)
            useCharRefs = kwargs.get("useCharRefs", True)
            #
            myIo = IoAdapter(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
            if filePath.endswith(".gz") and workPath:
                rfn = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                tPath = os.path.join(workPath, rfn)
                ret = myIo.writeFile(tPath, containerList=containerList, enforceAscii=enforceAscii)
                ret = self.__fileU.compress(tPath, filePath, compressType="gzip")
            else:
                ret = myIo.writeFile(filePath, containerList=containerList, enforceAscii=enforceAscii)
        except Exception as e:
            logger.error("Failing for %s with %s", filePath, str(e))
        return ret

    def __deserializeMmCifDict(self, filePath, **kwargs):
        """ """
        try:
            containerList = []
            workPath = kwargs.get("workPath", None)
            enforceAscii = kwargs.get("enforceAscii", True)
            raiseExceptions = kwargs.get("raiseExceptions", True)
            useCharRefs = kwargs.get("useCharRefs", True)
            #
            myIo = IoAdapterPy(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
            containerList = myIo.readFile(filePath, enforceAscii=enforceAscii, outDirPath=workPath)
        except Exception as e:
            logger.error("Failing for %s with %s", filePath, str(e))
        return containerList

    def __serializeMmCifDict(self, filePath, containerList, **kwargs):
        """ """
        try:
            ret = False
            # workPath = kwargs.get('workPath', None)
            enforceAscii = kwargs.get("enforceAscii", True)
            raiseExceptions = kwargs.get("raiseExceptions", True)
            useCharRefs = kwargs.get("useCharRefs", True)
            #
            myIo = IoAdapterPy(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
            ret = myIo.writeFile(filePath, containerList=containerList, enforceAscii=enforceAscii)
        except Exception as e:
            logger.error("Failing for %s with %s", filePath, str(e))
        return ret

    def __serializeList(self, filePath, aList, enforceAscii=True, **kwargs):
        """ """

        try:
            _ = kwargs
            if enforceAscii:
                encoding = "ascii"
            else:
                encoding = "utf-8"
            #
            if sys.version_info[0] > 2:
                with open(filePath, "w") as ofh:
                    if enforceAscii:
                        for st in aList:
                            ofh.write("%s\n" % st.encode("ascii", "xmlcharrefreplace").decode("ascii"))
                    else:
                        for st in aList:
                            ofh.write("%s\n" % st)
            else:
                if enforceAscii:
                    with io.open(filePath, "w", encoding=encoding) as ofh:
                        for st in aList:
                            ofh.write("%s\n" % st.encode("ascii", "xmlcharrefreplace").decode("ascii"))
                else:
                    with open(filePath, "wb") as ofh:
                        for st in aList:
                            ofh.write("%s\n" % st)
            return True
        except Exception as e:
            logger.error("Unable to serialize %r %r", filePath, str(e))
        return False

    def __processList(self, ifh, enforceAscii=True, **kwargs):
        uncomment = kwargs.get("uncomment", True)
        aList = []
        for line in ifh:
            if enforceAscii:
                pth = line[:-1].encode("ascii", "xmlcharrefreplace").decode("ascii")
            else:
                pth = line[:-1]
            if not pth or (uncomment and pth.startswith("#")):
                continue
            aList.append(pth)
        return aList

    def __deserializeList(self, filePath, enforceAscii=True, encodingErrors="ignore", **kwargs):
        aList = []
        _ = kwargs
        try:
            if filePath[-3:] == ".gz":
                if sys.version_info[0] > 2:
                    with gzip.open(filePath, "rt", encoding="utf-8-sig", errors=encodingErrors) as ifh:
                        aList = self.__processList(ifh, enforceAscii=enforceAscii, **kwargs)
                else:
                    tPath = self.__fileU.uncompress(filePath, outputDir=None)
                    # for py2 this commented code is problematic for non-ascii data
                    # with gzip.open(filePath, "rb") as ifh:
                    #    aList = self.__processList(ifh, enforceAscii=enforceAscii)
                    with io.open(tPath, encoding="utf-8-sig", errors="ignore") as ifh:
                        aList = self.__processList(ifh, enforceAscii=enforceAscii)
            else:
                with io.open(filePath, encoding="utf-8-sig", errors="ignore") as ifh:
                    aList = self.__processList(ifh, enforceAscii=enforceAscii, **kwargs)
        except Exception as e:
            logger.error("Unable to deserialize %r %s", filePath, str(e))
        #
        logger.debug("Reading list length %d", len(aList))
        return aList

    def __csvReader(self, csvFile, rowFormat, delimiter, uncomment=True):
        oL = []

        maxInt = sys.maxsize
        csv.field_size_limit(maxInt)
        if rowFormat == "dict":
            if uncomment:
                reader = csv.DictReader(uncommentFilter(csvFile), delimiter=delimiter)
            else:
                reader = csv.DictReader(csvFile, delimiter=delimiter)
            for rowD in reader:
                oL.append(rowD)
        elif rowFormat == "list":
            if uncomment:
                reader = csv.reader(uncommentFilter(csvFile), delimiter=delimiter)
            else:
                reader = csv.reader(csvFile, delimiter=delimiter)
            for rowL in reader:
                oL.append(rowL)
        return oL

    def deserializeCsvIter(self, filePath, delimiter=",", rowFormat="dict", encodingErrors="ignore", uncomment=True, **kwargs):
        """Return an iterator to input CSV format file.

        Args:
            filePath (str): input file path
            delimiter (str, optional): CSV delimiter. Defaults to ",".
            rowFormat (str, optional): format for each process row (list or dict). Defaults to "dict".
            encodingErrors (str, optional): treatment of encoding errors. Defaults to "ignore".
            uncomment (bool, optional): flag to ignore leading comments. Defaults to True.

        Returns:
            (iterator): iterator for rowwise access to processed CSV data
        """
        encoding = kwargs.get("encoding", "utf-8-sig")
        maxInt = sys.maxsize
        csv.field_size_limit(maxInt)
        try:
            if filePath[-3:] == ".gz":
                with gzip.open(filePath, "rt", encoding=encoding, errors=encodingErrors) as csvFile:
                    startIt = itertools.dropwhile(lambda x: x.startswith("#"), csvFile) if uncomment else csvFile
                    if rowFormat == "dict":
                        reader = csv.DictReader(startIt, delimiter=delimiter)
                    elif rowFormat == "list":
                        reader = csv.reader(startIt, delimiter=delimiter)
                    for row in reader:
                        yield row
            else:
                with io.open(filePath, newline="", encoding=encoding, errors="ignore") as csvFile:
                    startIt = itertools.dropwhile(lambda x: x.startswith("#"), csvFile) if uncomment else csvFile
                    if rowFormat == "dict":
                        reader = csv.DictReader(startIt, delimiter=delimiter)
                    elif rowFormat == "list":
                        reader = csv.reader(startIt, delimiter=delimiter)
                    for row in reader:
                        # if uncomment and row.startswith("#"):
                        #    continue
                        yield row
        except Exception as e:
            logger.error("Unable to deserialize %r %s", filePath, str(e))

    def __deserializeCsv(self, filePath, delimiter=",", rowFormat="dict", encodingErrors="ignore", uncomment=True, **kwargs):
        oL = []
        encoding = kwargs.get("encoding", "utf-8-sig")
        try:
            if filePath[-3:] == ".gz":
                if sys.version_info[0] > 2:
                    with gzip.open(filePath, "rt", encoding=encoding, errors=encodingErrors) as csvFile:
                        oL = self.__csvReader(csvFile, rowFormat, delimiter, uncomment=uncomment)
                else:
                    # Py2 situation non-ascii encodings is problematic
                    # with gzip.open(filePath, "rb") as csvFile:
                    #    oL = self.__csvReader(csvFile, rowFormat, delimiter)
                    tPath = self.__fileU.uncompress(filePath, outputDir=None)
                    with io.open(tPath, newline="", encoding=encoding, errors="ignore") as csvFile:
                        oL = self.__csvReader(csvFile, rowFormat, delimiter, uncomment=uncomment)
            else:
                with io.open(filePath, newline="", encoding=encoding, errors="ignore") as csvFile:
                    oL = self.__csvReader(csvFile, rowFormat, delimiter, uncomment=uncomment)

            return oL
        except Exception as e:
            logger.error("Unable to deserialize %r %s", filePath, str(e))
        #
        logger.debug("Reading list length %d", len(oL))
        return oL

    def __serializeCsv(self, filePath, rowDictList, fieldNames=None, **kwargs):
        """ """
        _ = kwargs
        try:
            wD = {}
            ret = False
            fNames = fieldNames if fieldNames else list(rowDictList[0].keys())
            # with io.open(filePath, 'w', newline='') as csvFile:
            with open(filePath, "w") as csvFile:
                writer = csv.DictWriter(csvFile, fieldnames=fNames)
                writer.writeheader()
                for ii, rowDict in enumerate(rowDictList):
                    try:
                        wD = {k: v for k, v in rowDict.items() if k in fNames}
                        writer.writerow(wD)
                    except Exception as e:
                        logger.error("Skipping bad CSV record %d wD %r rowDict %r with %s", ii + 1, wD, rowDict, str(e))
                        continue

            ret = True
        except Exception as e:
            logger.error("Failing for %s : %r with %s", filePath, wD, str(e))
        return ret

    def __csvEncoder(self, csvData, encoding="utf-8-sig", encodingErrors="ignore"):
        """Handle encoding issues for gzipped data in Py2. (beware of the BOM chars)

        Args:
            csvData (text lines): uncompressed data from gzip open
            encoding (str, optional): character encoding. Defaults to "utf-8-sig".
            encodingErrors (str, optional): error treatment. Defaults to "ignore".
        """
        for line in csvData:
            yield line.decode("utf-8-sig", errors=encodingErrors).encode(encoding, errors=encodingErrors)

    def __deserializeXmlPrev(self, filePath, **kwargs):
        """Read the input XML file path and return an ElementTree data object instance.

        Args:
            filePath (sting): input XML file path

        Returns:
            object: instance of an ElementTree tree object
        """
        _ = kwargs
        tree = None
        try:
            logger.debug("Parsing XML path %s", filePath)
            if filePath[-3:] == ".gz":
                with gzip.open(filePath, mode="rb") as ifh:
                    tV = time.time()
                    tree = ET.parse(ifh)
            else:
                with open(filePath, mode="rb") as ifh:
                    tV = time.time()
                    tree = ET.parse(ifh)
            logger.debug("Parsed %s in %.2f seconds", filePath, time.time() - tV)
        except Exception as e:
            logger.error("Unable to deserialize %r %s", filePath, str(e))
        #
        return tree

    def __testGzip(self, filePath):
        ok = True
        with gzip.open(filePath, "r") as fh:
            try:
                fh.read(1)
            except gzip.BadGzipFile:
                ok = False
            except Exception:
                ok = False
        logger.debug("Gzip file check %r", ok)
        return ok

    def __deserializeXml(self, filePath, **kwargs):
        """Read the input XML file path and return an ElementTree data object instance.

        Args:
            filePath (sting): input XML file path

        Returns:
            object: instance of an ElementTree tree object
        """
        _ = kwargs
        tree = None
        encoding = kwargs.get("encoding", "utf-8-sig")
        encodingErrors = kwargs.get("encodingErrors", "ignore")
        #
        try:
            logger.debug("Parsing XML path %s", filePath)
            if filePath[-3:] == ".gz" and self.__testGzip(filePath):
                if sys.version_info[0] > 2:
                    with gzip.open(filePath, "rt", encoding=encoding, errors=encodingErrors) as ifh:
                        tV = time.time()
                        tree = ET.parse(ifh)
                else:
                    tPath = self.__fileU.uncompress(filePath, outputDir=None)
                    with io.open(tPath, encoding=encoding, errors=encodingErrors) as ifh:
                        tV = time.time()
                        tree = ET.parse(ifh)
            else:
                with io.open(filePath, encoding=encoding, errors=encodingErrors) as ifh:
                    tV = time.time()
                    tree = ET.parse(ifh)
            logger.debug("Parsed %s in %.2f seconds", filePath, time.time() - tV)
        except Exception as e:
            logger.error("Unable to deserialize %r %s", filePath, str(e))
        #
        return tree
