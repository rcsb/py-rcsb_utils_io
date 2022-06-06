##
# File: FastaUtil.py
# Date:  24-Nov-2018 Jdw
#

import logging
import re
from gzip import GzipFile

logger = logging.getLogger(__name__)


class FastaUtil(object):
    """Simple FASTA reader and writer with options to parse application
    specific common lines (e.g. Uniprot and PDB)
    """

    aaDict3 = {
        "ALA": "A",
        "ARG": "R",
        "ASN": "N",
        "ASP": "D",
        "ASX": "B",
        "CYS": "C",
        "GLN": "Q",
        "GLU": "E",
        "GLX": "Z",
        "GLY": "G",
        "HIS": "H",
        "ILE": "I",
        "LEU": "L",
        "LYS": "K",
        "MET": "M",
        "PHE": "F",
        "PRO": "P",
        "SER": "S",
        "THR": "T",
        "TRP": "W",
        "TYR": "Y",
        "VAL": "V",
        "PYL": "O",
        "SEC": "U",
    }
    # aaValidCodes = "".join(sorted(FastaUtil.aaDict3.values()))
    aaValidCodes = "ABCDEFGHIKLMNOPQRSTUVWYZX"
    naValidCodes = "AGCTURYNWSMKBHDV"

    def __init__(self, **kwargs):
        self.__uniProtCommentRegex = re.compile(r"\>(\w+)\|(\w+)\|(\w+)\s(.*)\sOS=(.*)\sOX=(\d+)\s(GN=(.*)\s)?PE=(\d+)\sSV=(\d+)")
        _ = kwargs

    def __removeWhiteSpace(self, string):
        pattern = re.compile(r"\s+")
        return re.sub(pattern, "", string)

    def cleanSequence(self, sequence, seqType="protein"):
        """[summary]

        Args:
            sequence ([type]): raw one-letter code sequence
            seqType (str, optional): sequence type protein or na ... Defaults to "protein".

        Returns:
            (bool, str): status, cleaned sequence (upper case w/o white space)
        """
        try:
            tS = self.__removeWhiteSpace(sequence.upper())
            if seqType == "protein":
                allowedChars = set(FastaUtil.aaValidCodes)
            else:
                allowedChars = set(FastaUtil.naValidCodes)

            if set(sequence).issubset(allowedChars):
                return True, tS
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False, sequence

    def parseComment(self, cmtLine, commentStyle):
        if commentStyle == "uniprot":
            seqId, cD = self.__parseCommentUniProt(cmtLine)
        elif commentStyle == "uniprot_regex":
            seqId, cD = self.__parseCommentUniProtRe(cmtLine)
        elif commentStyle == "prerelease":
            seqId, cD = self.__parseCommentPreRelease(cmtLine)
        elif commentStyle == "tagged":
            seqId, cD = self.__parseCommentTagged(cmtLine)
        else:
            seqId, cD = self.__parseCommentDefault(cmtLine)
        return seqId, cD

    def readFasta(self, filePath, **kwargs):
        """"""
        try:
            commentStyle = kwargs.get("commentStyle", "uniprot").lower()
            if commentStyle == "uniprot":
                commentParser = self.__parseCommentUniProt
            elif commentStyle == "uniprot_regex":
                commentParser = self.__parseCommentUniProtRe
            elif commentStyle == "prerelease":
                commentParser = self.__parseCommentPreRelease
            elif commentStyle == "tagged":
                commentParser = self.__parseCommentTagged
            else:
                commentParser = self.__parseCommentDefault

            if filePath[-3:] == ".gz":
                sD = self.__readFastaGz(filePath, commentParser)
            else:
                sD = self.__readFasta(filePath, commentParser)

            return sD

        except Exception as e:
            logger.exception("Failing for filePath %r with %s", filePath, str(e))

        return {}

    def writeFasta(self, filePath, seqDict, **kwargs):
        """"""
        maxLineLength = int(kwargs.get("maxLineLength", 70))
        makeComment = kwargs.get("makeComment", False)
        with open(filePath, "w") as ofh:
            ok = self.__writeFasta(ofh, seqDict, maxLineLength=maxLineLength, makeComment=makeComment)
        return ok

    def __readFastaGz(self, filePath, commentParser):
        seqD = {}
        with GzipFile(filePath, "rb") as ifh:
            for cmtLine, sequence in self.__readRecordFasta(ifh):
                seqId, cD = commentParser(cmtLine)
                cD["sequence"] = sequence.upper()
                if seqId:
                    seqD[seqId] = cD
        return seqD

    def __readFasta(self, filePath, commentParser):
        seqD = {}
        with open(filePath, "r") as ifh:
            for cmtLine, sequence in self.__readRecordFasta(ifh):
                seqId, cD = commentParser(cmtLine)
                cD["sequence"] = sequence.upper()
                if seqId:
                    seqD[seqId] = cD
        return seqD

    def __parseCommentUniProt(self, cmtLine):
        """
        >sp|O00141|SGK1_HUMAN Serine/threonine-protein kinase Sgk1 OS=Homo sapiens OX=9606 GN=SGK1 PE=1 SV=2
        """
        try:
            org = ""
            geneName = ""
            dbName = ""
            dbAccession = ""
            dbIsoform = ""
            seqId = ""
            description = ""
            #
            ff = cmtLine[1:].split("|")
            dbName = ff[0].upper()
            seqId = ff[1]
            tS = ff[2]
            #
            tt = seqId.split("-")
            dbAccession = seqId
            dbIsoform = ""
            if len(tt) > 1:
                dbAccession = tt[0]
                dbIsoform = tt[1]
            #
            idx = tS.find("OS=")
            if idx > 0:
                description = tS[: idx - 1]
                ff = tS[idx:].split("=")
                if len(ff) == 3:
                    if ff[0] == "OS":
                        org = ff[1][:-2]
                        geneName = ff[2]
                elif len(ff) > 1:
                    if ff[0] == "OS":
                        org = ff[1]
            #
            cD = {"description": description, "org": org, "gene_name": geneName, "db_accession": dbAccession, "db_name": dbName, "db_isoform": dbIsoform}
            return seqId, cD
            #
        except Exception as e:
            logger.exception("Failed to parse comment %s with %s", cmtLine, str(e))
        return None, {}

    def __parseCommentUniProtRe(self, cmtLine):
        """
        '>sp|O00141|SGK1_HUMAN Serine/threonine-protein kinase Sgk1 OS=Homo sapiens OX=9606 GN=SGK1 PE=1 SV=2
        """
        try:
            org = ""
            geneName = ""
            dbName = ""
            dbAccession = ""
            dbIsoform = ""
            seqId = ""
            description = ""
            taxId = ""
            # proteinExistence = ""
            # seqVersion = ""
            #
            match = self.__uniProtCommentRegex.match(cmtLine)
            if match:
                groups = match.groups()
                dbName = groups[0]
                seqId = groups[1]
                tt = seqId.split("-")
                dbAccession = seqId
                dbIsoform = ""
                if len(tt) > 1:
                    dbAccession = tt[0]
                    dbIsoform = tt[1]
                entryName = groups[2]
                description = groups[3]
                org = groups[4]
                taxId = groups[5]
                geneName = groups[7]
                # proteinExistence = groups[8]
                # seqVersion = groups[9]
            #
            cD = {
                "seqId": seqId,
                "description": description,
                "org": org,
                "taxonomy_id": taxId,
                "gene_name": geneName,
                "db_accession": dbAccession,
                "entry_name": entryName,
                "db_name": dbName,
                "db_isoform": dbIsoform,
                # "protein_existence": proteinExistence,
                # "seq_version": seqVersion,
            }
            return seqId, cD
            #
        except Exception as e:
            logger.exception("Failed to parse comment %s with %s", cmtLine, str(e))
        return None, {}

    def __parseCommentTagged(self, cmtLine):
        try:
            cD = {}
            fL = cmtLine[1:].split("|")
            for v, k in zip(fL[0::2], fL[1::2]):
                cD[k] = v
            seqId = cD["seqId"]
            return seqId, cD
            #
        except Exception as e:
            logger.exception("Failed to parse comment %s with %s", cmtLine, str(e))
        return None, {}

    def __parseCommentPreRelease(self, cmtLine):
        try:
            #
            ff = cmtLine[1:].split(" ")
            entryId = ff[0].upper()
            entityId = ff[2]
            seqId = entryId + "_" + entityId
            return seqId, {}
            #
        except Exception as e:
            logger.exception("Failed to parse comment %s with %s", cmtLine, str(e))
        return None, {}

    def __parseCommentDefault(self, cmtLine):
        try:
            #
            seqId = cmtLine[1:]
            return seqId, {}
            #
        except Exception as e:
            logger.exception("Failed to parse comment %s with %s", cmtLine, str(e))
        return None, {}

    def __readRecordFasta(self, ifh):
        """Return the next FASTA record in the input file handle."""
        comment, sequence = None, []
        for line in ifh:
            # handle the variety of types accross versions and open/gzipfile classes
            if isinstance(line, str):
                line = line[:-1].encode("ascii", "xmlcharrefreplace").decode("ascii")
            else:
                line = line[:-1].decode("ascii", "xmlcharrefreplace")

            line = line.rstrip()
            if line.startswith(">"):
                if comment:
                    yield (comment, "".join(sequence))
                comment, sequence = line, []
            else:
                sequence.append(line)
        if comment:
            yield (comment, "".join(sequence))

    def __writeFasta(self, ofh, seqDict, maxLineLength=70, makeComment=False):
        """
        seqDict[seqId] = {sequence: 'one-letter-code sequence', ...}

        With makeComment = False:

            >seqId
            MTVEDR....

        or makeComment= True :

            >{v|k|v'|k' ... for k,v in seqD.items()}
            MTVEDR....

        """
        try:
            lCount = 0
            for seqId, sD in seqDict.items():
                sA = []
                if makeComment:
                    comment = ""
                    cL = []
                    if "seqId" in sD:
                        cL.append(str(sD["seqId"]))
                        cL.append("seqId")
                    for k, v in sD.items():
                        if k in ["sequence", "seqId"]:
                            continue
                        cL.append(str(v))
                        cL.append(str(k))
                    comment = "|".join(cL)
                else:
                    comment = seqId
                #
                sA.append(">%s\n" % comment)
                lCount += 1
                sequence = sD["sequence"]
                for i in range(0, len(sequence), maxLineLength):
                    sA.append(sequence[i: i + maxLineLength] + "\n")
                    result = "".join(sA)
                    lCount += 1
                ofh.write(result)
            return True
        except Exception as e:
            logger.info("seqId %r sD %r", seqId, sD)
            logger.exception("Failing with %s", str(e))

        return False

    def __readFastaX(self, filePath):
        try:
            rD = {}
            with open(filePath, "r") as fb:
                for line in fb:
                    if str(line[:-1]).startswith(">"):
                        fields = str(line[:-1]).strip().split()
                        ky = str(fields[0][1:]).strip()
                        length = int(str(fields[2][7:]))
                        rD[ky] = length
                return rD
        except Exception as e:
            logger.exception("Failing wiht %s", str(e))
        return rD
