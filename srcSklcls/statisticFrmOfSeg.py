#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle

############################
## load event segments from file
def loadEvtseg(filePath):
    unitHash = {}#segment:segmentID(count from 0)
    unitDFHash = {} # segmentID:f_st

    inFile = file(filePath)
    segStrList = inFile.readlines()
    unitID = 0
    for lineStr in segStrList:
        lineStr = re.sub(r'\n', '', lineStr)
        contentArr = lineStr.split("\t")
        #print contentArr[2]
        f_st = int(contentArr[0])
        unit = contentArr[2]
        unit = re.sub(' ', '_', unit)
        unitHash[unit] = unitID
        #unitDFHash[unitID] = f_st
        unitID += 1
    inFile.close()
    print "### " + str(len(unitHash)) + " event segs and f_st values are loaded from " + inFile.name
    return unitHash

############################
## load event frame elements from file
def loadEvtEle(filePath):
    unitInvolvedHash = {}#sid:1
    unitHash = {}#segment:segmentID(count from 0)
    unitDFHash = {} # segmentID:f_st

    inFile = file(filePath)
    segStrList = cPickle.load(inFile)
    unitInvolvedHash = cPickle.load(inFile)
    unitID = 0
    for lineStr in segStrList:
        lineStr = re.sub(r'\n', '', lineStr)
        contentArr = lineStr.split("\t")
        #print contentArr[1]
        f_st = int(contentArr[0])
        unit = contentArr[2]
        unitHash[unit] = unitID
        unitDFHash[unitID] = f_st
        unitID += 1
    inFile.close()
    print "### " + str(len(unitHash)) + " event units and f_st values are loaded from " + inFile.name + " with Involved tweet number: " + str(len(unitInvolvedHash))

    return unitHash

print "###program starts at " + str(time.asctime())
dataFilePath = r"../ni_data/"

# for version: post, postprocessing events. replace segments with their highest ranked frames
if len(sys.argv) == 3:
    btyUnitFileName = sys.argv[2]
else:
    print "Usage python statisticsFrmofEle.py day btyeleFileName"
    sys.exit()

eleHash = loadEvtEle(btyUnitFileName)
print eleHash.keys()[0:20]

UNIT = "frm"
unitHash = {} #unit:df_hash
unitAppHash = {} #unit:apphash
windowHash = {} # timeSliceIdStr:tweetNum

frmFile = file(dataFilePath + UNIT + "Ofele"+sys.argv[1], "w")
tArr = [str(i).zfill(2) for i in range(1, 16)]
filePref = "relSkl_2013-01-" + sys.argv[1]

for tStr in tArr:
    sklFile = file(dataFilePath + filePref)
    if tStr != sys.argv[1]:
        continue
    print "### Processing " + sklFile.name
    tweetNum_t = 0
    while 1:
        lineStr = sklFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        if len(contentArr) < 2:
            continue
        tweetIDstr = contentArr[0]
        tweetText = contentArr[1]
        tweetNum_t += 1
        textArr = tweetText.split(" ")

        for segment in textArr:
            unit = segment
            if len(unit) < 1:
                continue

            currEleHash = dict([(ele, 1) for ele in unit.split("|") if len(ele) > 1])
            for seg in eleHash:
                if seg not in currEleHash:
                    continue

                if seg in unitHash:
                    df_hash = unitHash[seg]
                else:
                    df_hash = {}

                if unit in df_hash:
                    df_hash[unit] += 1
                else:
                    df_hash[unit] = 1

                unitHash[seg] = df_hash

        if tweetNum_t % 100000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! units: " + str(len(unitHash))
    windowHash[tStr] = tweetNum_t
    sklFile.close()
print "### In total " + str(len(unitHash)) + " " + UNIT + "s are loaded!"

## writing to frm file
newHash = {}
unitNum = 0
for unit in sorted(unitHash.keys()):
    unitNum += 1
    df_hash = unitHash[unit]

    # for debugging
    if len(df_hash) > 10:
        frmHash = dict([(it[0], it[1]) for it in sorted(df_hash.items(), key = lambda a:a[1], reverse = True)[:10]])
    else:
        frmHash = df_hash

    freqFrm = sorted(frmHash.items(), key = lambda a:a[1], reverse = True)[0]
    print unit + str(freqFrm)

    newHash[unit] = frmHash

cPickle.dump(newHash, frmFile)
frmFile.close()
print "### " + UNIT + "OfSeg are written to " + frmFile.name

print "###program ends at " + str(time.asctime())
