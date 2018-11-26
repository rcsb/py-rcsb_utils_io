##
# File: FastaUtil.py
# Date:  24-Nov-2018 Jdw
#

import logging
from gzip import GzipFile

logger = logging.getLogger(__name__)


class FastaUtil(object):
    """  Simple FASTA reader and writer with options to parse application
         specific common lines (e.g. Uniprot and PDB)
    """

    def __init__(self, **kwargs):
        pass

    def readFasta(self, filePath, **kwargs):
        """
        """
        try:
            commentStyle = kwargs.get('commentStyle', 'uniprot').lower()
            if commentStyle == 'uniprot':
                commentParser = self.__parseCommentUniProt
            elif commentStyle == 'prerelease':
                commentParser = self.__parseCommentPreRelease

            if filePath[-3:] == '.gz':
                sD = self.__readFastaGz(filePath, commentParser)
            else:
                sD = self.__readFasta(filePath, commentParser)

            return sD

        except Exception as e:
            logger.exception("Failing for filePath %r with %s" % (filePath, str(e)))

        return {}

    def writeFasta(self, filePath, seqDict, **kwargs):
        """
        """
        maxLineLength = int(kwargs.get('maxLineLength', 70))
        with open(filePath, 'w') as ofh:
            ok = self.__writeFasta(ofh, seqDict, maxLineLength=maxLineLength)
        return ok

    def __readFastaGz(self, filePath, commentParser):
        seqD = {}
        with GzipFile(filePath, 'rb') as ifh:
            for cmtLine, sequence in self.__read_record_fasta(ifh):
                seqId, cD = commentParser(cmtLine)
                cD['sequence'] = sequence.upper()
                if seqId:
                    seqD[seqId] = cD
        return seqD

    def __readFasta(self, filePath, commentParser):
        seqD = {}
        with open(filePath, 'r') as ifh:
            for cmtLine, sequence in self.__read_record_fasta(ifh):
                seqId, cD = commentParser(cmtLine)
                cD['sequence'] = sequence.upper()
                if seqId:
                    seqD[seqId] = cD
        return seqD

    def __parseCommentUniProt(self, cmtLine):
        try:
            org = ''
            geneName = ''
            dbName = ''
            dbAccession = ''
            dbIsoform = ''
            seqId = ''
            description = ''
            #
            ff = cmtLine[1:].split('|')
            dbName = ff[0].upper()
            seqId = ff[1]
            tS = ff[2]
            #
            tt = seqId.split('-')
            dbAccession = seqId
            dbIsoform = ''
            if len(tt) > 1:
                dbAccession = tt[0]
                dbIsoform = tt[1]
            #
            idx = tS.find("OS=")
            if idx > 0:
                description = tS[:idx - 1]
                ff = tS[idx:].split('=')
                if len(ff) == 3:
                    if ff[0] == 'OS':
                        org = ff[1][:-2]
                        geneName = ff[2]
                elif len(ff) > 1:
                    if ff[0] == 'OS':
                        org = ff[1]
            #
            cD = {'description': description, 'org': org,
                  'gene_name': geneName, 'db_accession': dbAccession, 'db_name': dbName, 'db_isoform': dbIsoform}
            return seqId, cD
            #
        except Exception as e:
            logger.exception("Failed to parse comment %s with %s" % (cmtLine, str(e)))
        return None, {}

    def __parseCommentPreRelease(self, cmtLine):
        try:
            #
            ff = cmtLine[1:].split(' ')
            entryId = ff[0].upper()
            entityId = ff[2]
            seqId = entryId + '_' + entityId
            return seqId, {}
            #
        except Exception as e:
            logger.exception("Failed to parse comment %s with %s" % (cmtLine, str(e)))
        return None, {}

    def __read_record_fasta(self, ifh):
        """ Return the next FASTA record in the input file handle.
        """
        comment, sequence = None, []
        for line in ifh:
            # handle the variety of types accross versions and open/gzipfile classes
            if isinstance(line, str):
                line = line[:-1].encode('ascii', 'xmlcharrefreplace').decode('ascii')
            else:
                line = line[:-1].decode('ascii', 'xmlcharrefreplace')

            line = line.rstrip()
            if line.startswith(">"):
                if comment:
                    yield (comment, ''.join(sequence))
                comment, sequence = line, []
            else:
                sequence.append(line)
        if comment:
            yield (comment, ''.join(sequence))

    def __writeFasta(self, ofh, seqDict, maxLineLength=70):
        """
            seqDict[seqId] = 'one-letter-code sequence'
            >seqId
            MTVEDR....

        """
        try:
            lCount = 0
            for seqId, sD in seqDict.items():
                sequence = sD['sequence']
                sA = []
                sA.append(">%s\n" % seqId)
                lCount += 1
                for i in range(0, len(sequence), maxLineLength):
                    sA.append(sequence[i:i + maxLineLength] + '\n')
                    result = ''.join(sA)
                    lCount += 1
                ofh.write(result)
            return True
        except Exception as e:
            logger.exception("Failing with %s" % str(e))

        return False

    def __readFastaX(self, filePath):
        try:
            rD = {}
            with open(filePath, 'r') as fb:
                for line in fb:
                    if str(line[:-1]).startswith('>'):
                        fields = str(line[:-1]).strip().split()
                        ky = str(fields[0][1:]).strip()
                        length = int(str(fields[2][7:]))
                        rD[ky] = length
                return rD
        except Exception as e:
            logger.exception("Error '{0}' occured. Arguments {1}.".format(str(e), e.args))
        return rD
