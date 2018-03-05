#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle

sys.path.append("../Scripts")
from hashOperation import *

sys.path.append("../srcPreprocess/")
from preProcessTweetText import *


def statisticDF_fromFile(dataFilename, predefinedUnitHash):
    unitAppHash = {} #unit:df_t_hash

    inFile = file(dataFilename)

    tweetNum_t = 0
    while 1:
        lineStr = inFile.readline()
        if not lineStr:
            print "##End of reading file. [statisticDF from text file] ", time.asctime(), inFile.name , " units: ", len(unitAppHash), " tweets:", tweetNum_t
            break

        contentArr = lineStr[:-1].split("\t")
        # lineStr frame format: tweetIDstr[\t]tweetText
        if len(contentArr) < 2: 
            print "**less than 2 components", contentArr
            continue
        
        tweetIDstr = contentArr[0]
        tweetText = contentArr[-1].lower()
        tweetNum_t += 1

        # use frame element
        # tweetText: frm1[1space]frm2 frm3...
        # frame: arg1|vp|arg2   frmEle: word1_word2_...
        tweetText = re.sub("\|", " ", tweetText)


        textArr = tweetText.strip().split(" ")
        for unit in textArr:
            if len(unit) < 1:
                continue

            # for testing bursty methods
            # predefinedUnitHash usually is bursty skl hash
            if predefinedUnitHash is not None:
                #if re.sub(r"\|", "_", unit).strip("_") not in sklHash: # use frame
                if unit not in predefinedUnitHash: # use frame element or segment
                    continue

            # statistic unit df
                apphash = {}
                if unit in unitAppHash:
                    apphash = unitAppHash[unit]
                apphash[tweetIDstr] = 1
                unitAppHash[unit] = apphash 

        if tweetNum_t % 100000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! units: " + str(len(unitHash))

    inFile.close()
    return unitAppHash


def statisticDF(dataFilePath, predefinedUnitHash):

    stopFileName = r"../data/stoplist.dft"
    stopwordHash = loadStopword(stopFileName)

    unitHash = {} #unit:df_hash
    unitAppHash = {} #unit:apphash
    windowHash = {} # timeSliceIdStr:tweetNum

    fileList = os.listdir(dataFilePath)
    fileList = sorted(fileList)
    for item in fileList:
        if item.find("relSkl_") != 0:
            continue
        inFile = file(dataFilePath + item)
        print "### Processing " + inFile.name
        tStr = item[-2:]

        tweetNum_t = 0
        while 1:
            lineStr = inFile.readline()
            if not lineStr:
                break

            contentArr = lineStr[:-1].split("\t")
            # lineStr frame format: tweetIDstr[\t]tweetText
            if len(contentArr) < 2: 
                print "**less than 2 components", contentArr
                continue
            
            tweetIDstr = contentArr[0]
            tweetText = contentArr[-1].lower()
            tweetNum_t += 1

            # use frame element
            # tweetText: frm1[1space]frm2 frm3...
            # frame: arg1|vp|arg2   frmEle: word1_word2_...
            tweetText = re.sub("\|", " ", tweetText)
            textArr = tweetText.strip().split(" ")

            # del stop words
            textArr = tweetArrClean_delStop(textArr, stopwordHash)
            textArr = tweetArrClean_delUrl(textArr)

            for unit in textArr:
                if len(unit) < 1:
                    continue

                # for testing bursty methods
                # predefinedUnitHash usually is bursty skl hash
                if predefinedUnitHash is not None:
                    #if re.sub(r"\|", "_", unit).strip("_") not in sklHash: # use frame
                    if unit not in predefinedUnitHash: # use frame element or segment
                        continue

                # statistic unit ps
                if unit in unitHash:
                    df_hash = unitHash[unit]
                    if tStr in df_hash:
                        df_t_hash = df_hash[tStr]
                    else:
                        df_t_hash = {}
                else:
                    df_hash = {}
                    df_t_hash = {}
                df_t_hash[tweetIDstr] = 1
                df_hash[tStr] = df_t_hash
                unitHash[unit] = df_hash

            if tweetNum_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! units: " + str(len(unitHash))

        windowHash[tStr] = tweetNum_t
        inFile.close()


        # extra step: decrease memory cost
        for unit in unitHash:
            df_hash = unitHash[unit]
            if tStr not in df_hash:
                df_hash[tStr] = 0.0
            else:
                df_t_hash = df_hash[tStr]
                df_hash[tStr] = len(df_t_hash)*1.0
            unitHash[unit] = df_hash

        print "### (current day)" + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded. unitNum: " + str(len(unitHash))

    print "### In total(whole corpora) ", len(unitHash), UNIT, "s are loaded!"

    return unitHash, windowHash


# writing to dffile
def write2dfFile(unitAppHash, windowHash, dfFilePath):

    dfFile = file(dfFilePath, "w")

    # write each day's tweetNumber into first line of df file
    # Format:01 num1#02 num2#...#15 num15
    sortedTweetNumList = sorted(windowHash.items(), key = lambda a:a[0])
    tweetNumStr = ""
    for item in sortedTweetNumList:
        tStr = item[0]
        tweetNum = item[1]
        tweetNumStr += tStr + " " + str(tweetNum) + "#"

    dfFile.write(tweetNumStr[:-1] + "\n")
    itemNum = 0
    for unit in sorted(unitAppHash.keys()):
        itemNum += 1
        apphash = unitAppHash[unit]
        df = len(apphash)
        dfFile.write(str(df) + "\t" + unit + "\n")
    dfFile.close()
    print "### " + UNIT + "s' df values are written to " + dfFile.name


# writing to unit ps file
def write2psFile(unitHash, windowHash, psFilePath):

    psFile = file(psFilePath, "w")
    unitNum = 0
    for unit in sorted(unitHash.keys()):
        unitNum += 1
        df_hash = unitHash[unit]

        df_hash = dict([(t, df_hash[t]/windowHash[t]) for t in df_hash if df_hash[t]>0])
        l = len(df_hash)
        probTemp = sum(df_hash.values())
        prob = probTemp/l

        psFile.write(str(prob) + "\t" + unit + "\n")

        if unitNum % 100000 == 0:
            print "### " + str(unitNum) + " units are processed at " + str(time.asctime())

    psFile.close()
    print "### " + UNIT + "s' ps values are written to " + psFile.name

global UNIT
UNIT = "skl"

if __name__ == "__main__":
    print "###program starts at " + str(time.asctime())
    if len(sys.argv) == 2:
        dataFilePath = sys.argv[1]+"/"
    else:
        print "Usage python estimatePs_smldata.py [datafilepath] (default: ../ni_data/)"
        sys.exit(0)

    [unitHash, windowHash]  = statisticDF(dataFilePath, None)

    psFilePath = dataFilePath + UNIT + "_ps"
    write2psFile(unitHash, windowHash, psFilePath)

    print "###program ends at " + str(time.asctime())

