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
#
##

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import datetime
import io
import json
import logging
import os
import pickle
import pprint
import sys

from mmcif.io.IoAdapterPy import IoAdapterPy

try:
    from mmcif.io.IoAdapterCore import IoAdapterCore as IoAdapter
except Exception:
    from mmcif.io.IoAdapterPy import IoAdapterPy as IoAdapter


logger = logging.getLogger(__name__)


class JsonTypeEncoder(json.JSONEncoder):
    """ Helper class to handle serializing date and time objects
    """

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        if isinstance(o, datetime.date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class IoUtil(object):

    def __init__(self):
        pass

    def serialize(self, filePath, myObj, format="pickle", **kwargs):
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
        fmt = str(format).lower()
        if fmt in ['mmcif']:
            ret = self.__serializeMmCif(filePath, myObj, **kwargs)
        elif fmt in ['json']:
            ret = self.__serializeJson(filePath, myObj, **kwargs)
        elif fmt in ['pickle']:
            ret = self.__serializePickle(filePath, myObj, **kwargs)
        elif fmt in ['list']:
            ret = self.__serializeList(filePath, myObj, enforceAscii=True, **kwargs)
        elif fmt in ['mmcif-dict']:
            ret = self.__serializeMmCifDict(filePath, myObj, **kwargs)
        elif fmt in ['text-dump']:
            ret = self.__textDump(filePath, myObj, **kwargs)
        else:
            pass

        return ret

    def deserialize(self, filePath, format="pickle", **kwargs):
        """Public method to deserialize objects in supported formats.

        Args:
            filePath (str): local file path
            format (str, optional): one of ['mmcif', 'json', 'list', 'pickle' (default)]
            **kwargs:  additional keyword arguments passed to worker methods -

        Returns:
            object: deserializerd object data

        """
        ret = None
        fmt = str(format).lower()
        if fmt in ['mmcif']:
            ret = self.__deserializeMmCif(filePath, **kwargs)
        elif fmt in ['json']:
            ret = self.__deserializeJson(filePath, **kwargs)
        elif fmt in ['pickle']:
            ret = self.__deserializePickle(filePath, **kwargs)
        elif fmt in ['list']:
            ret = self.__deserializeList(filePath, enforceAscii=True, **kwargs)
        elif fmt in ['mmcif-dict']:
            ret = self.__deserializeMmCifDict(filePath, **kwargs)
        else:
            pass

        return ret

    def exists(self, filePath, mode=os.R_OK):
        try:
            return os.access(filePath, os.R_OK)
        except Exception:
            return False

    def __textDump(self, filePath, myObj, **kwargs):
        try:
            indent = kwargs.get('indent', 1)
            width = kwargs.get('width', 120)
            sOut = pprint.pformat(myObj, indent=indent, width=width)
            with open(filePath, 'w') as ofh:
                ofh.write("\n%s\n" % sOut)
            return True
        except Exception as e:
            logger.error("Unable to dump to %r  %r" % (filePath, str(e)))
        return False

    def __serializePickle(self, filePath, myObj, **kwargs):
        try:
            pickleProtocol = kwargs.get('pickleProtocol', pickle.HIGHEST_PROTOCOL)

            with open(filePath, 'wb') as outfile:
                pickle.dump(myObj, outfile, pickleProtocol)
            return True
        except Exception as e:
            logger.error("Unable to serialize %r  %r" % (filePath, str(e)))
        return False

    def __deserializePickle(self, filePath, **kwargs):
        myDefault = kwargs.get('default', {})
        try:
            with open(filePath, 'rb') as outfile:
                return pickle.load(outfile)
        except Exception as e:
            logger.warning("Unable to deserialize %r %r " % (filePath, str(e)))
        return myDefault

    def __serializeJson(self, filePath, myObj, **kwargs):
        """ Internal method to serialize the input object as JSON.  An encoding
            helper class is included to handle selected python data types (e.g., datetime)
        """
        indent = kwargs.get('indent', 0)
        try:
            with open(filePath, "w") as outfile:
                json.dump(myObj, outfile, indent=indent, cls=JsonTypeEncoder)
            return True
        except Exception as e:
            logger.error("Unable to serialize %r  %r" % (filePath, str(e)))
        return False

    def __deserializeJson(self, filePath, **kwargs):
        myDefault = kwargs.get('default', {})
        try:
            with open(filePath, "r") as infile:
                return json.load(infile)
        except Exception as e:
            logger.warning("Unable to deserialize %r %r " % (filePath, str(e)))
        return myDefault

    def __deserializeMmCif(self, filePath, **kwargs):
        """
        """
        try:
            containerList = []
            workPath = kwargs.get('workPath', None)
            enforceAscii = kwargs.get('enforceAscii', True)
            raiseExceptions = kwargs.get('raiseExceptions', True)
            useCharRefs = kwargs.get('useCharRefs', True)
            #
            myIo = IoAdapter(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
            containerList = myIo.readFile(filePath, enforceAscii=enforceAscii, outDirPath=workPath)
        except Exception as e:
            logger.error("Failing for %s with %s" % (filePath, str(e)))
        return containerList

    def __serializeMmCif(self, filePath, containerList, **kwargs):
        """
        """
        try:
            ret = False
            # workPath = kwargs.get('workPath', None)
            enforceAscii = kwargs.get('enforceAscii', True)
            raiseExceptions = kwargs.get('raiseExceptions', True)
            useCharRefs = kwargs.get('useCharRefs', True)
            #
            myIo = IoAdapter(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
            ret = myIo.writeFile(filePath, containerList=containerList, enforceAscii=enforceAscii)
        except Exception as e:
            logger.error("Failing for %s with %s" % (filePath, str(e)))
        return ret

    def __deserializeMmCifDict(self, filePath, **kwargs):
        """
        """
        try:
            containerList = []
            workPath = kwargs.get('workPath', None)
            enforceAscii = kwargs.get('enforceAscii', True)
            raiseExceptions = kwargs.get('raiseExceptions', True)
            useCharRefs = kwargs.get('useCharRefs', True)
            #
            myIo = IoAdapterPy(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
            containerList = myIo.readFile(filePath, enforceAscii=enforceAscii, outDirPath=workPath)
        except Exception as e:
            logger.error("Failing for %s with %s" % (filePath, str(e)))
        return containerList

    def __serializeMmCifDict(self, filePath, containerList, **kwargs):
        """
        """
        try:
            ret = False
            # workPath = kwargs.get('workPath', None)
            enforceAscii = kwargs.get('enforceAscii', True)
            raiseExceptions = kwargs.get('raiseExceptions', True)
            useCharRefs = kwargs.get('useCharRefs', True)
            #
            myIo = IoAdapterPy(raiseExceptions=raiseExceptions, useCharRefs=useCharRefs)
            ret = myIo.writeFile(filePath, containerList=containerList, enforceAscii=enforceAscii)
        except Exception as e:
            logger.error("Failing for %s with %s" % (filePath, str(e)))
        return ret

    def __serializeList(self, filePath, aList, enforceAscii=True, **kwargs):
        """
        """

        try:
            if enforceAscii:
                encoding = 'ascii'
            else:
                encoding = 'utf-8'
            #
            if sys.version_info[0] > 2:
                with open(filePath, 'w') as ofh:
                    if enforceAscii:
                        for st in aList:
                            ofh.write("%s\n" % st.encode('ascii', 'xmlcharrefreplace').decode('ascii'))
                    else:
                        for st in aList:
                            ofh.write("%s\n" % st)
            else:
                if enforceAscii:
                    with io.open(filePath, 'w', encoding=encoding) as ofh:
                        for st in aList:
                            ofh.write("%s\n" % st.encode('ascii', 'xmlcharrefreplace').decode('ascii'))
                else:
                    with open(filePath, "wb") as ofh:
                        for st in aList:
                            ofh.write("%s\n" % st)
            return True
        except Exception as e:
            logger.error("Unable to serialize %r %r" % (filePath, str(e)))
        return False

    def __deserializeList(self, filePath, enforceAscii=True, **kwargs):
        aList = []
        try:
            with io.open(filePath, 'r', encoding="utf-8") as ifh:
                for line in ifh:
                    if enforceAscii:
                        pth = line[:-1].encode('ascii', 'xmlcharrefreplace').decode('ascii')
                    else:
                        pth = line[:-1]
                    if len(pth) and not pth.startswith("#"):
                        aList.append(pth)
        except Exception as e:
            logger.error("Unable to deserialize %r %s" % (filePath, str(e)))
        #
        logger.debug("Reading list length %d" % len(aList))
        return aList

    def __toAscii(self, inputFilePath, outputFilePath, chunkSize=5000, encodingErrors='ignore'):
        """ Encode input file to Ascii and write this to the target output file.   Handle encoding
            errors according to the input settting ('ignore', 'escape', 'xmlcharrefreplace').
        """
        try:
            chunk = []
            with io.open(inputFilePath, "r", encoding="utf-8") as r, io.open(outputFilePath, "w", encoding='ascii') as w:
                for line in r:
                    # chunk.append(line.encode('ascii', 'xmlcharrefreplace').decode('ascii'))
                    chunk.append(line.encode('ascii', encodingErrors).decode('ascii'))
                    if len(chunk) == chunkSize:
                        w.writelines(chunk)
                        chunk = []
                w.writelines(chunk)
            return True
        except Exception as e:
            logger.error("Failing text ascii encoding for %s with %s" % (inputFilePath, str(e)))
        #
        return False
