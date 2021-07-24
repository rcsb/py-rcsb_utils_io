import os

from rcsb.utils.io.FileUtil import FileUtil


class SplitJoin(object):
    def __init__(self, *kwargs):
        pass

    def split(self, inputFilePath, splitDirPath, prefixName="part_", maxSizeMB=50):
        chunkSize = maxSizeMB * 1000000
        partNumber = 0
        fU = FileUtil()
        fU.mkdir(splitDirPath)
        manifestPath = os.path.join(splitDirPath, "MANIFEST")
        myHash = fU.hash(inputFilePath, hashType="md5")
        with open(manifestPath, "w") as mfh:
            mfh.write("%s\t%s\n" % (inputFilePath, myHash))
            with open(inputFilePath, "rb") as ifh:
                chunk = ifh.read(chunkSize)
                while chunk:
                    partNumber += 1
                    partName = prefixName + str(partNumber)
                    fp = os.path.join(splitDirPath, partName)
                    with open(fp, "wb") as ofh:
                        ofh.write(chunk)
                    mfh.write("%s\n" % partName)
                    #
                    chunk = ifh.read(chunkSize)
        return partNumber

    def join(self, outputFilePath, splitDirPath):
        manifestPath = os.path.join(splitDirPath, "MANIFEST")
        with open(outputFilePath, "wb") as ofh:
            with open(manifestPath, "r") as mfh:
                line = mfh.readline()
                fp, priorHash = line[:-1].split("\t")
                for line in mfh:
                    fp = os.path.join(splitDirPath, line[:-1])
                    with open(fp, "rb") as ifh:
                        data = ifh.read()
                        ofh.write(data)
        fU = FileUtil()
        newHash = fU.hash(outputFilePath, hashType="md5")
        return newHash == priorHash
