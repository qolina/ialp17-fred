#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import math
import cPickle

sys.path.append("../srcStat")
from getSocialInfo import *

############################
## load ps from file
def loadps(psFilePath):
    global unitpsHash
    psFile = file(psFilePath)
    while True:
        lineStr = psFile.readline()
        lineStr = re.sub(r'\n', '', lineStr)
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        #print contentArr
        prob = float(contentArr[0])
        unit = contentArr[1]
        unitpsHash[unit] = prob
    psFile.close()
    print "### " + str(time.asctime()) + " " + str(len(unitpsHash)) + " " + UNIT + "s' ps values are loaded from " + psFile.name

############################
## load tweetID-usrID
def loadUsrId(filepath, tweIdFileName):

    usrFile = file(filepath,"r")
    attHash = cPickle.load(usrFile)
    usrFile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath

    if tweIdFileName:
        tweIdList = getTweetID(tweIdFileName)
#        tweIdToUsrIdHash_emp = dict([(tid, "empty") for tid in tweIdList if tid not in attHash])  # only 1 in day 10, 13, 15
        tweIdToUsrIdHash = dict([(tid, attHash[tid]["Usr"]) for tid in tweIdList if tid in attHash]) 
    else:
        tweIdToUsrIdHash = dict([(tid, attHash[tid]["Usr"]) for tid in attHash]) 
    print "## " + str(time.asctime()) + " Loading done. Twe2Usr" , len(tweIdToUsrIdHash)
    return tweIdToUsrIdHash

############################
## load tweetID-usrID
def loadID(filepath):
    if not os.path.exists(filepath):
        return None

    idfile = file(filepath)
    IDmap = cPickle.load(idfile)
    idfile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath
    return IDmap

############################
## calculate sigmoid
def sigmoid(x):
    return 1.0/(1.0+math.exp(-x))

############################
## getEventSkl
def getEventSkl(dataFilePath, socialFeaFilePath, idmapFilePath):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("relSkl_") != 0:
            continue
        tStr = item[-2:]
        if Day != tStr:
            continue
        print "Time window: " + tStr
        print "### Processing " + item
        seggedFile = file(dataFilePath + item)
        N_t = 0
        userHash = {}# statistic user number in current day
        unitHash = {} #unit:df_t_hash
        #df_t_hash --> tweetIDStr:1
        unitUsrHash = {}
        unitInvolvedHash = {}
        tweToUsrFilePath = socialFeaFilePath + "tweetSocialFeature" + tStr
        tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath, None)
        IDmap = loadID(idmapFilePath + "IDmap_2013-01-" + tStr)
        while True:
            lineStr = seggedFile.readline()[:-1].strip()
            if len(lineStr) == 0:
                break
            contentArr = lineStr.split("\t")
            if len(contentArr) < 2:
                print "wrong format", len(contentArr)
                continue
            # format of lineStr: tweetID(originalTweetID)[\t]score[\t]tweetText   Or tweetId(day+lineId)[\t]tweetText
            tweetIDstr = contentArr[0]
            tweetText = contentArr[-1].lower()
            
            if len(tweetIDstr)==18:
                usrIDstr = tweIdToUsrIdHash.get(tweetIDstr)
            else:
                usrIDstr = tweIdToUsrIdHash.get(IDmap[int(tweetIDstr[2:])])

            if usrIDstr is None:
                continue

            userHash[usrIDstr] = 1 # statistic user number in current day

            N_t += 1

            # use frame element
            tweetText = re.sub("\|", " ", tweetText)
            textArr = tweetText.strip().split(" ")

            for segment in textArr:
                unit = segment
                #unit = segment.strip("|")
                if len(unit) < 1:
                    continue
                # segment df
                df_t_hash = {}
                if unit in unitHash:
                    df_t_hash = unitHash[unit]
                df_t_hash[tweetIDstr] = 1
                unitHash[unit] = df_t_hash

                # segment users
                usr_hash = {}
                if unit in unitUsrHash:
                    usr_hash = unitUsrHash[unit]
#                    if unit == "clemson":
#                        print "## userDF of ", unit, len(usr_hash), usrIDstr
                usr_hash[usrIDstr] = 1
                unitUsrHash[unit] = usr_hash

            if N_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        windowHash[tStr] = N_t
        seggedFile.close()
        print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded.", len(unitHash), "\t", len(userHash)

        burstySegHash = {}

        pbSegHash = {}
        for unit in unitHash:

            # twitterNum / unit, timeWindow
            f_st = len(unitHash[unit])*1.0

            # usrNum / unit, timeWindow
            u_st_num = len(unitUsrHash[unit])


            #segmentpsHash mapping: segment -> ps, N_t: twitterNum / timeWindow
            ps = unitpsHash.get(unit)
            if ps is None:
                continue

            e_st = N_t * ps
            if f_st <= e_st: # non-bursty segment or word
                continue
            # bursty segment or word
            sigma_st = math.sqrt(e_st*(1-ps))

            if f_st >= e_st + 2*sigma_st: # extremely bursty segments or words
                Pb_st = 1.0
            else:
                Pb_st = sigmoid(10*(f_st - e_st - sigma_st)/sigma_st)
            u_st = math.log10(u_st_num)
            wb_st = Pb_st*u_st

            burstySegHash[unit] = wb_st
            pbSegHash[unit] = "\t".join([str(i) for i in [wb_st, Pb_st, f_st, e_st, 2*sigma_st, u_st_num, u_st]])

        K = int(math.sqrt(N_t)) + 1
        print "K (num of event " + UNIT + "): " + str(K)

        sortedList = sorted(burstySegHash.items(), key = lambda a:a[1], reverse = True)
        sortedList = sortedList[0:K]

        # write to file
        segStrList = []
        for key in sortedList:
            eventSeg = key[0]
            if len(tweetIDstr) == 18:
                apphash = dict([(tid, 1) for tid in unitHash[eventSeg]])
            else:
                apphash = dict([(IDmap[int(tid[2:])], 1) for tid in unitHash[eventSeg]])

            unitInvolvedHash.update(apphash)
            f_st = len(unitHash[eventSeg])

            segStrList.append(str(f_st) + "\t" + str(key[1]) + "\t" + eventSeg + "\n")

        if len(sys.argv) == 2:
            eventSegFile = file(dataFilePath + "event" + UNIT + tStr, "w")
        else:
            eventSegFile = file(btyFileName, "w")

        cPickle.dump(segStrList, eventSegFile)
        cPickle.dump(unitInvolvedHash, eventSegFile)
        eventSegFile.close()

        for item in sortedList:
            print item[0], "\t", pbSegHash[item[0]]

global UNIT
UNIT = "skl"

############################
## main Function
if __name__ == "__main__":
    global Day, btyFileName
    if len(sys.argv) > 2:
        Day = sys.argv[1]
        btyFileName = sys.argv[2]
    elif len(sys.argv) == 2:
        Day = sys.argv[1]
    else:
        print "Usage getbtyskl.py day [btyFileName]"
        sys.exit()

    print "###program starts at " + str(time.asctime())

    dataFilePath = r"../ni_data/"

    psFilePath = dataFilePath + UNIT + "_ps"

    # for frame
    socialFeaFilePath = dataFilePath + r"/aux/"

    idmapFilePath = dataFilePath + r"/aux/"

    windowHash = {} # timeSliceIdStr:tweetNum
    unitpsHash = {} # unit:ps

    loadps(psFilePath)
    getEventSkl(dataFilePath, socialFeaFilePath, idmapFilePath)

    print "###program ends at " + str(time.asctime())
