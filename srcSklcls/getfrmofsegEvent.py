#! /usr/bin/env python
#coding=utf-8
# evaluation of twevent
import os
import sys
import re
import time
import math
import cPickle

def loadFrmOfSeg(filePath):
    inFile = file(filePath)
    segHash = cPickle.load(inFile)
    for seg in segHash:
        frmHash = segHash[seg]
        if len(frmHash) == 0:
            segHash[seg] = seg
        else:
            freqFrm = sorted(frmHash.items(), key = lambda a:a[1], reverse = True)[0][0]
            segHash[seg] = freqFrm

    inFile.close()
    print "## " + str(len(segHash)) + " segment's frms are loaded."
    return segHash

##############################################################
# main function
if len(sys.argv) == 3:
    tStr = sys.argv[1]
    frmFilePath = sys.argv[2]
else:
    print "Usage python getOtherEvent.py day frmofeleFilename"
    sys.exit()

dirPath = r"/path_to_fred/201301_skl/"
fileList = os.listdir(dirPath)
fileList.sort()

for item in fileList:
    if not item.startswith("EventFile"+tStr):
        continue
    eventFile = file(dirPath + item)
    frmEventFile = file(dirPath + "frmEventFile"+tStr, "w")
    segHash = loadFrmOfSeg(frmFilePath)

    print "*********************Reading file: " + item
    lineArr = eventFile.readlines()
    lineIdx = 0
    while lineIdx < len(lineArr):
        lineStr = lineArr[lineIdx]
        if lineStr.startswith("***"):
            line1 = lineArr[lineIdx + 1]
            #segmentList = lineArr[lineIdx+4][:-1].split("||")
            segmentList = lineArr[lineIdx+4][:-1].split(" ")
            frmList = []
            for seg in segmentList:
                seg_con = re.sub(" ", "_", seg)
                if seg_con in segHash:
                    frm = segHash[seg_con]
                else:
                    frm = seg_con
                frmList.append(frm)

#            print line1
            line4 = lineArr[lineIdx + 4]
            frmEventFile.write(lineStr)
            frmEventFile.write(line1)
            frmEventFile.write(lineArr[lineIdx+2])
            frmEventFile.write(line4)
            frmEventFile.write(" ".join(frmList) + "\n")
            frmEventFile.write(lineArr[lineIdx+5])
        lineIdx += 6
    eventFile.close()
    frmEventFile.close()

print "# program ends."
