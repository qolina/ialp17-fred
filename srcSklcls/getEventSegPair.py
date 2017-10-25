#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import math
import cPickle

from getbtySkl import *

class Event:
    def __init__(self, eventId):
        self.eventId = eventId
    
    def updateEvent(self, nodeList, edgeHash):
        self.nodeList = nodeList
        self.edgeHash = edgeHash

############################
## load df of word from file into wordDFHash
def loadDF(dfFilePath):
    global wordDFHash
    dfFile = file(dfFilePath)
    wordDFHash = cPickle.load(dfFile)
    #print sorted(wordDFHash.items(), key = lambda a:a[1], reverse = True)[0:50]
    print "### " + str(time.asctime()) + str(len(wordDFHash)) + " " + UNIT + "s' df values are loaded from " + dfFile.name
    dfFile.close()
    return wordDFHash

############################
## load event segments from file
def loadEvtseg(filePath):
    unitInvolvedHash = {}#sid:1
    unitHash = {}#segment:segmentID(count from 0)
    unitDFHash = {} # segmentID:f_st
    unitScoreHash = {} # segmentID: score

    inFile = file(filePath)
    segStrList = cPickle.load(inFile)
    unitInvolvedHash = cPickle.load(inFile)
    unitID = 0
    for lineStr in segStrList:
        lineStr = re.sub(r'\n', '', lineStr)
        contentArr = lineStr.split("\t")
        f_st = int(contentArr[0])
        unit = contentArr[2]
        unitHash[unit] = unitID
        unitDFHash[unitID] = f_st
        #unitScoreHash[unitID] = float(contentArr[1]) # one score
        unitScoreHash[unitID] = contentArr[1] # two score
        unitID += 1
    inFile.close()
    print "### " + str(len(unitHash)) + " event " + UNIT + "s and f_st values are loaded from " + inFile.name + " with Involved tweet number: " + str(len(unitInvolvedHash))

    # segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
    return unitHash, unitDFHash, unitInvolvedHash, unitScoreHash

def newHour(hourStr):
    hour = int(hourStr)
    if hour >= 16:
        return str(hour-16)
    else:
        return str(hour+8)


############################
## load tweetID-createdHour
def loadTime(filepath, tweIdFileName):
    inFile = file(filepath,"r")
    attHash = cPickle.load(inFile)
    inFile.close()
    print "## " + str(time.asctime()) + " Loading done (hour of tweets). " + filepath

    if tweIdFileName:
        tweIdList = getTweetID(tweIdFileName)
        timeHash = dict([(tid, attHash[tid]["Time"]) for tid in tweIdList if tid in attHash]) 
    else:
        timeHash = dict([(tid, attHash[tid]["Time"]) for tid in attHash])  # in version 1

    print "## " + str(time.asctime()) + " Loading done. timeOfTwe" , len(timeHash)

    return timeHash

############################
## calculate similarity of two segments
def calSegPairSim(segAppHash, segTextHash, unitDFHash, docNum):
    segPairHash = {}
    segfWeiHash = {}
    segTVecHash = {}
    segVecNormHash = {}
    for segId in segAppHash:

        # m_eSegAppHash mapping: segID -> [twitterID -> 1/0]
        # m_eSegTextHash mapping: segID -> twitterText(segment|segment|...)###twitterText###...
        # segmentDFHash mapping: segID -> f_st
        # segmentDFHash mapping: twitterNum
        f_st = unitDFHash[segId]
        f_stm = len(segAppHash[segId])

        f_weight = f_stm * 1.0 / f_st
        segfWeiHash[segId] = f_weight
        segText = segTextHash[segId]
        if segText.endswith("###"):
            segText = segText[:-3]

        [featureHash, norm] = toTFIDFVector(segText, docNum)
        segTVecHash[segId] = featureHash
        segVecNormHash[segId] = norm

    # calculate similarity
    segList = sorted(segfWeiHash.keys())
    segNum = len(segList)
    for i in range(0,segNum):
        for j in range(i+1,segNum):
            segId1 = segList[i]
            segId2 = segList[j]
            segPair = str(segId1) + "|" + str(segId2)
            tSim = textSim(segTVecHash[segId1], segVecNormHash[segId1], segTVecHash[segId2], segVecNormHash[segId2])
            sim = segfWeiHash[segId1] * segfWeiHash[segId2] * tSim
            segPairHash[segPair] = sim
            
    return segPairHash 

############################
## represent text string into tf-idf vector
def textSim(feaHash1, norm1, feaHash2, norm2):
    tSim = 0.0
    for seg in feaHash1:
        if seg in feaHash2:
            w1 = feaHash1[seg]
            w2 = feaHash2[seg]
            tSim += w1 * w2
    tSim = tSim / (norm1 * norm2)
    return tSim

############################
## represent text string into tf-idf vector
def toTFIDFVector(text, docNum):

    # m_eSegTextHash mapping: segID -> twitterText(segment segment ...)###twitterText###...
    # segmentDFHash mapping: twitterNum
    docArr = text.split("###")
    docId = 0
    # one word(unigram) is a feature, not segment
    feaTFHash = {}
    #feaAppHash = {}
    featureHash = {}
    norm = 0.0
    for docStr in docArr:
        docId += 1
        segArr = docStr.split(" ")
        for segment in segArr:

            wordArr = segment.split(" ")
            for word in wordArr:
                #appHash = {}
                if len(word) < 1:
                    continue
                if word in feaTFHash:
                    feaTFHash[word] += 1
                else:
                    feaTFHash[word] = 1
    for word in feaTFHash:
        tf = feaTFHash[word] 
        if word not in wordDFHash:
            print "## word not existed in wordDFhash: " + word
            continue
        idf = math.log(TWEETNUM/wordDFHash[word])
        weight = tf*idf
        featureHash[word] = weight
        norm += weight * weight
    norm = math.sqrt(norm)

    return featureHash, norm

############################
def loadText(textFilePath, IDmap, unitInvolvedHash):
    unitTextHash = {} #sid:text (word word word)
    textFile = file(textFilePath)

    while True:
        lineStr = textFile.readline()
        if not lineStr:
            print "## loading text done. " + str(time.asctime()) + textFile.name
            break
        arr = lineStr[:-1].strip().split("\t")
        sid = arr[0]

        if len(sid) != 18:
            tid = IDmap[int(sid[2:])]
        else:
            tid = sid

        if tid in unitInvolvedHash:
            text = re.sub(r"\|", " ", arr[-1])
            unitTextHash[sid] = text 
    textFile.close()
    return unitTextHash

def loadOriText(oriTweetTextDir, tStr, IDmap, unitInvolvedHash):
    unitTextHash = {} #sid:text (word word word...)
#    textFile = file(r"../data/201301_preprocess/text_2013-01-"+tStr)
    textFile = file(oriTweetTextDir + r"/tweetText"+tStr)
    idx = 0
    while True:
        lineStr = textFile.readline().lower()
        if not lineStr:
            print "## loading text done. " + str(time.asctime()) + textFile.name, " len(unitTextHash)", len(unitTextHash)
            break
        lineStr = lineStr[:-1]

        sid = tStr + str(idx)
        tid = IDmap[idx]
        if tid in unitInvolvedHash:
            unitTextHash[sid] = lineStr
        idx += 1
    textFile.close()
    return unitTextHash

############################
## merge two hash: add smallHash's content into bigHash
def merge(smallHash, bigHash):
    print "Incorporate " + str(len(smallHash)) + " pairs into " + str(len(bigHash)),
    newNum = 0
    changeNum = 0
    for pair in smallHash:
        if pair in bigHash:
            bigHash[pair] += smallHash[pair]
            changeNum += 1
        else:
            bigHash[pair] = smallHash[pair]
            newNum += 1
    print " with newNum/changedNum " + str(newNum) + "/" + str(changeNum)
    return bigHash

############################
## cluster Event Segment
def geteSegPairSim(dataFilePath, M, idmapFileDir, tweetSocialInfoDir, oriTweetTextDir):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("relSkl_") != 0:
            continue

        tStr = item[-2:]
        if tStr != Day:
            continue
        print "### Processing " + item
        print "Time window: " + tStr
        N_t = 0 # tweetNum appeared in time window tStr
        # load segged tweet files in time window tStr
        seggedFile = file(dataFilePath + item)

        # load extracted event segments in tStr
        if len(sys.argv) == 3:
            eventSegFilePath = btyEleFilename
        else:
            eventSegFilePath = dataFilePath + "event" + UNIT + tStr
        [unitHash, unitDFHash, unitInvolvedHash, unitScoreHash] = loadEvtseg(eventSegFilePath)

        # load extracted createdHour of tweet in tStr
        tweetTimeFilePath = tweetSocialInfoDir + "tweetSocialFeature" + tStr
        #timeHash = loadTime(tweetTimeFilePath, dataFilePath+item)
        timeHash = loadTime(tweetTimeFilePath, None)

        IDmapFilePath = idmapFileDir + "IDmap_2015-05-" + tStr
        IDmap = loadID(IDmapFilePath)

        if UNIT == "skl":
            unitTextHash = loadOriText(oriTweetTextDir, tStr, IDmap, unitInvolvedHash)
        elif UNIT == "segment":
            unitTextHash = loadText(dataFilePath+item, IDmap, unitInvolvedHash)

        m = 0
        m_step = 24 / M # split time window tStr into M parts
        m_docNum = 0
        m_eSegAppHash = {} # event segments' appearHash in time interval m
        m_eSegTextHash = {} # event segments' appeared in Text in time interval m
        segPairHash = {} # all edges in graph
        while True:
            lineStr = seggedFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            contentArr = lineStr.split("\t")
            tweetIDstr = contentArr[0]
            if len(tweetIDstr) < 18:
                tweIDOri = IDmap[int(tweetIDstr[2:])]
            else:
                tweIDOri = tweetIDstr
            tweetText = contentArr[-1]
            if tweetIDstr in unitTextHash:
                tweTxtOri = unitTextHash[tweetIDstr]
            N_t += 1
            hourStr = timeHash.get(tweIDOri)
            if hourStr is None:
                continue
            hour = int(hourStr)
            #print tweetIDstr + " is created at hour: " + str(hour)
            if hour >= (m+m_step):
                print "### new interval time slice in tStr: " + str(hour) + " with previous tweet Num: " + str(m_docNum) + " bursty seg number: " + str(len(m_eSegTextHash))
                # end of one m interval

                m_segPairHash = calSegPairSim(m_eSegAppHash, m_eSegTextHash, unitDFHash, m_docNum)
                segPairHash = merge(m_segPairHash, segPairHash)
                m_eSegAppHash.clear()
                m_eSegTextHash.clear()
                m_docNum = 0
                #m += m_step
                m = hour
            if hour < m:
                print "##!! tweet created time in chaos: " + str(hour) + " small than " + str(m)
                continue

            m_docNum += 1

            # for frame element
            tweetText = re.sub("\|", " ", tweetText)

            textArr = tweetText.strip().split(" ")
            for segment in textArr:
                if segment not in unitHash:
                    continue
                # event segments
                segId = unitHash[segment]
                appTextStr = ""
                apphash = {}
                if segId in m_eSegAppHash:
                    apphash = m_eSegAppHash[segId]
                    appTextStr = m_eSegTextHash[segId]
                if tweIDOri in apphash:
                    continue
#                print segment, tweetIDstr, tweTxtOri
                appTextStr += tweTxtOri + "###"
                apphash[tweIDOri] = 1
                m_eSegAppHash[segId] = apphash
                m_eSegTextHash[segId] = appTextStr

            if N_t % 10000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed! segNum: " + str(len(m_eSegAppHash)) + " " + str(len(m_eSegTextHash))

        # last interval in tStr
        m_segPairHash = calSegPairSim(m_eSegAppHash, m_eSegTextHash, unitDFHash, m_docNum)
        segPairHash = merge(m_segPairHash, segPairHash)
        seggedFile.close()
        print "### " + str(time.asctime()) + " " + str(len(unitHash)) + " event segments in " + item + " are loaded. With segment pairs Num: " + str(len(segPairHash))
        
        segPairFile = file(dataFilePath + "segPairFile" + tStr, "w")
        cPickle.dump(unitHash, segPairFile)
        cPickle.dump(segPairHash, segPairFile)
        segPairFile.close()

############################
## keep top K (value) items in hash
def getTopItems(sampleHash, K):
    sortedList = sorted(sampleHash.items(), key = lambda a:a[1], reverse = True)
    sampleHash.clear()
    sortedList = sortedList[0:K]
    for key in sortedList:
        sampleHash[key[0]] = key[1]
    return sampleHash

############################
## main Function
global Day, UNIT, TWEETNUM, btyEleFilename 
UNIT = "segment"
#UNIT = "skl"

if __name__=="__main__":
    if len(sys.argv) == 2:
        Day = sys.argv[1]
    elif len(sys.argv) == 3:
        Day = sys.argv[1]
        btyEleFilename = sys.argv[2]
    else:
        print "Usage: python getSklpair.py day [filename]"
        sys.exit()

    print "###program starts at " + str(time.asctime())


    dataFilePath = r"path_to_fred/201301_skl/"

    dfFilePathFromSkl = dataFilePath + "wordDF"
    dfFilePathFromOriText = dataFilePath + "../clean/"+ "wordDF"

    idmapFileDir = dataFilePath + "../clean/"
    tweetSocialInfoDir = dataFilePath + "../nonEng/"

    # used for calculate textSim of bursty feature(frame or segment)
    oriTweetTextDir = dataFilePath + "../preprocess"

    TWEETNUM = 28651435 # total tweet number in relSkl-2013-01-??

    wordDFHash = {}
    M = 12

    loadDF(dfFilePathFromOriText)

    geteSegPairSim(dataFilePath, M, idmapFileDir, tweetSocialInfoDir, oriTweetTextDir)

    print "###program ends at " + str(time.asctime())
