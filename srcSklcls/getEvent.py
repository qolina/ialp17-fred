#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import math
import cPickle

from getEventSegPair import *

class Event:
    def __init__(self, eventId):
        self.eventId = eventId
    
    def updateEvent(self, nodeHash, edgeHash):
        self.nodeHash = nodeHash
        self.edgeHash = edgeHash

############################
## load seg pair
def loadsegPair(filepath):
    inFile = file(filepath,"r")
    segmentHash = cPickle.load(inFile)
    segPairHash = cPickle.load(inFile)
    inFile.close()
    return segmentHash, segPairHash

############################
## load wikiGram
def loadWiki(filepath):
    wikiProbHash = {}
    inFile = file(filepath,"r")
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        prob = float(lineStr[0:lineStr.find(" ")])
        gram = lineStr[lineStr.find(" ")+1:len(lineStr)]
#        print gram + "\t" + str(prob)
        wikiProbHash[gram] = prob
    inFile.close()
    print "### " + str(time.asctime()) + " " + str(len(wikiProbHash)) + " wiki grams' prob are loaded from " + inFile.name
    return wikiProbHash

############################
## keep top K (value) items in hash
def getTopItems(sampleHash, K):
    sortedList = sorted(sampleHash.items(), key = lambda a:a[1], reverse = True)
    sampleHash.clear()
    sortedList = sortedList[0:K]
    for key in sortedList:
        sampleHash[key[0]] = key[1]
    return sampleHash


# get segments' k nearest neighbor
def getKNN(segPairHash, kNeib):
    kNNHash = {}
    for pair in segPairHash:
        sim = segPairHash[pair]
        segArr = pair.split("|")
        segId1 = int(segArr[0])
        segId2 = int(segArr[1])
        nodeSimHash = {}
        if segId1 in kNNHash:
            nodeSimHash = kNNHash[segId1]
        nodeSimHash[segId2] = sim
        if len(nodeSimHash) > kNeib:
            nodeSimHash = getTopItems(nodeSimHash, kNeib)
        kNNHash[segId1] = nodeSimHash

        nodeSimHash2 = {}
        if segId2 in kNNHash:
            nodeSimHash2 = kNNHash[segId2]
        nodeSimHash2[segId1] = sim
        if len(nodeSimHash2) > kNeib:
            nodeSimHash2 = getTopItems(nodeSimHash2, kNeib)
        kNNHash[segId2] = nodeSimHash2
        
    print "### " + str(time.asctime()) + " " + str(len(kNNHash)) + " event segments' " + str(kNeib) + " neighbors are got."
    return kNNHash

# cluster similar segments into events
def getClusters(kNNHash, segPairHash):
    eventHash = {}
    eventIdx = 0
    nodeInEventHash = {} # segId:eventId # which node(seg) is already been clustered
    for segId1 in kNNHash:
        nodeSimHash = kNNHash[segId1]
#           print "#############################segId1: " + str(segId1)
#           print nodeSimHash
        for segId2 in nodeSimHash:
            if segId2 in nodeInEventHash:
                # s2 existed in one cluster, no clustering again
                continue
#               print "*************segId2: " + str(segId2)
#               print kNNHash[segId2]
            #[GUA] should also make sure segId2 in kNNHash[segId1]
            if segId1 in kNNHash[segId2]:
                # s1 s2 in same cluster

                #[GUA] edgeHash mapping: segId + | + segId -> simScore
                #[GUA] nodeHash mapping: segId -> edgeNum
                #[GUA] nodeInEventHash mapping: segId -> eventId
                eventId = eventIdx
                nodeHash = {}
                edgeHash = {}
                event = None
                if segId1 in nodeInEventHash:
                    eventId = nodeInEventHash[segId1]
                    event = eventHash[eventId]
                    nodeHash = event.nodeHash
                    edgeHash = event.edgeHash
                    nodeHash[segId1] += 1
                else:
                    eventIdx += 1
                    nodeInEventHash[segId1] = eventId
                    event = Event(eventId)
                    nodeHash[segId1] = 1
                nodeHash[segId2] = 1
                if segId1 < segId2:
                    edge = str(segId1) + "|" + str(segId2)
                else:
                    edge = str(segId2) + "|" + str(segId1)
                edgeHash[edge] = segPairHash[edge]
                event.updateEvent(nodeHash, edgeHash)
                eventHash[eventId] = event
                nodeInEventHash[segId2] = eventId

        # seg1's k nearest neighbors have been clustered into other events Or
        # seg1's k nearest neighbors all have long distance from seg1
        if segId1 not in nodeInEventHash:
            eventId = eventIdx
            eventIdx += 1
            nodeHash = {}
            edgeHash = {}
            event = Event(eventId)
            nodeHash[segId1] = 1
            event.updateEvent(nodeHash, edgeHash)
            eventHash[eventId] = event
            nodeInEventHash[segId1] = eventId
    print "### " + str(time.asctime()) + " " + str(len(eventHash)) + " events are got with nodes " + str(len(nodeInEventHash))
    return eventHash

def eventScoring(eventHash, reverseSegHash, dataFilePath):
    eventSegFilePath = dataFilePath + "event" + UNIT + Day
    [unitHash, unitDFHash, unitInvolvedHash, unitScoreHash] = loadEvtseg(eventSegFilePath)

    score_max = 0.0
    score_eventHash = {}
    newWorthScore_nodeHash = {}
    for eventId in sorted(eventHash.keys()):
        event = eventHash[eventId]
        nodeList = event.nodeHash.keys()
        edgeHash = event.edgeHash
        nodeNum = len(nodeList)
 
        # part1
        nodeZScoreArr = [float(unitScoreHash[segId][:unitScoreHash[segId].find("-")]) for segId in nodeList]
        zscore_nodes = sum(nodeZScoreArr)

        # part2
        nodeStrList = [reverseSegHash[nodeid] for nodeid in nodeList]
        node_NewWorthScoreArr = [frmNewWorth(nodeStr) for nodeStr in nodeStrList]
        newWorthScore_nodes = sum(node_NewWorthScoreArr)

        newWorthScore_nodeHash.update(dict([(nodeStrList[i], node_NewWorthScoreArr[i]) for i in range(nodeNum)]))

        simScore_edge = sum(edgeHash.values())

        scoreParts_eventArr = [newWorthScore_nodes, simScore_edge, zscore_nodes]
        score_event = (newWorthScore_nodes/nodeNum) * (simScore_edge/nodeNum)

        if score_event <= 0:
            print "##0-score event", eventId, nodeStrList, scoreParts_eventArr
            continue

        score_eventHash[eventId] = score_event
        if score_event > score_max:
            score_max = score_event

    score_eventHash = dict([(eventId, score_max/score_eventHash[eventId]) for eventId in score_eventHash])
    score_nodeHash = newWorthScore_nodeHash
    print "###Score of events and nodes are obtained. ", len(score_eventHash), len(score_nodeHash), score_max

    return score_eventHash, score_nodeHash


# filtering Or scoreing
def eventScoring_mu(eventHash, reverseSegHash):
    segmentNewWorthHash = {}
    mu_max = 0.0
    mu_eventHash = {}
    for eventId in sorted(eventHash.keys()):
        event = eventHash[eventId]
        nodeList = event.nodeHash.keys()
        edgeHash = event.edgeHash
        segNum = len(nodeList)
        mu_sum = 0.0
        sim_sum = 0.0
        contentArr = [reverseSegHash[id] for id in nodeList]
        currNewWorthHash = {}
        for segment in contentArr:
            mu_s = frmNewWorth(segment)# for frame structure
            #mu_s = segNewWorth(segment) # for segment
            segmentNewWorthHash[segment] = mu_s
            currNewWorthHash[segment] = mu_s
            mu_sum += mu_s

        sim_sum = sum(edgeHash.values())

        mu_avg = mu_sum/segNum
        sim_avg = sim_sum/segNum

        mu_e = mu_avg * sim_avg

        if mu_e > 0:
            mu_eventHash[eventId] = mu_e

        if mu_e > mu_max:
            mu_max = mu_e
    print "### Aft filtering 0 mu_e " + str(len(mu_eventHash)) + " events are kept. mu_max: " + str(mu_max)

    score_eventHash = dict([(eventId, mu_max/mu_eventHash[eventId]) for eventId in mu_eventHash])
    return score_eventHash, segmentNewWorthHash

############################
## newsWorthiness
def frmNewWorth(frm):
    frm = frm.strip("|")
    segArr = frm.split("|")
    worthArr = [segNewWorth(seg) for seg in segArr]
    #return sum(worthArr)/len(worthArr)
    return sum(worthArr)

def segNewWorth(segment):
    wordArr = segment.split("_")
    wordNum = len(wordArr)
    if wordNum == 1:
        if segment in wikiProbHash:
            return math.exp(wikiProbHash[segment])
        else:
            return 0.0
    maxProb = 0.0

    for i in range(0, wordNum):
        for j in range(i+1, wordNum+1):
            subArr = wordArr[i:j]
            prob = 0.0
            subS = " ".join(subArr)
            if subS in wikiProbHash:
                prob = math.exp(wikiProbHash[subS]) - 1.0
            if prob > maxProb:
                maxProb = prob
#    if maxProb > 0:
#        print "Newsworthiness of " + segment + " : " + str(maxProb)
    return maxProb


def writeEvent2File(eventHash, score_eventHash, score_nodeHash, reverseSegHash, tStr, kNeib, taoRatio):

    if len(sys.argv) == 2:
        eventFile = file(dataFilePath + "EventFile" + tStr + "_k" + str(kNeib) + "t" + str(taoRatio), "w")
    else:
        eventFile = file(eventFileName + "_k" + str(kNeib) + "t" + str(taoRatio), "w")

    sortedEventlist = sorted(score_eventHash.items(), key = lambda a:a[1])
    eventNum = 0

    # for statistic
    nodeLenHash = {} 
    eventNumHash = {}

    for eventItem in sortedEventlist:
        eventNum += 1
        eventId = eventItem[0]
        event = eventHash[eventId]

        edgeHash = event.edgeHash
        nodeHash = event.nodeHash
        nodeList = event.nodeHash.keys()

        rankedNodeList_byId = sorted(nodeHash.items(), key = lambda a:a[1], reverse = True)
        nodeList_byId = [item[0] for item in rankedNodeList_byId]

        segList = [reverseSegHash[id] for id in nodeList_byId]

        nodeNewWorthHash = dict([(segId, score_nodeHash[reverseSegHash[segId]]) for segId in nodeList])
        rankedNodeList_byNewWorth = sorted(nodeNewWorthHash.items(), key = lambda a:a[1], reverse = True)
        segList_byNewWorth = [reverseSegHash[item[0]] for item in rankedNodeList_byNewWorth]

        # for statistic
        nodes = len(nodeList)
        if nodes in nodeLenHash:
            nodeLenHash[nodes] += 1
        else:
            nodeLenHash[nodes] = 1
        ratioInt = int(eventItem[1])
        if ratioInt <= 10:
            if ratioInt in eventNumHash:
                eventNumHash[ratioInt] += 1
            else:
                eventNumHash[ratioInt] = 1

        eventFile.write("****************************************\n###Event " + str(eventNum) + " ratio: " + str(eventItem[1]))
        eventFile.write(" " + str(len(nodeList)) + " nodes and " + str(len(edgeHash)) + " edges.\n")
        eventFile.write(str(nodeList_byId) + "\n")
        eventFile.write(" ".join(segList) + "\n")
        eventFile.write(" ".join(segList_byNewWorth) + "\n")
        eventFile.write(str(edgeHash) + "\n")

    eventFile.close()

############################
## cluster Event Segment
def clusterEventSegment(dataFilePath, kNeib, taoRatio):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("relSkl_") != 0:
            continue
        tStr = item[-2:]
        if tStr != Day:
            continue
        print "Time window: " + tStr
        if len(sys.argv) == 2:
            segPairFilePath = dataFilePath + "segPairFile" + tStr
        else:
            segPairFilePath = segPairFileName

        [segmentHash, segPairHash] = loadsegPair(segPairFilePath)

        print "### " + str(time.asctime()) + " " + str(len(segmentHash)) + " event segments in " + segPairFilePath  + " are loaded. With segment pairs Num: " + str(len(segPairHash))

        kNNHash = getKNN(segPairHash, kNeib)

        eventHash = getClusters(kNNHash, segPairHash)

        reverseSegHash = dict([(segmentHash[seg], seg) for seg in segmentHash])

        [score_eventHash, score_nodeHash] = eventScoring(eventHash, reverseSegHash, dataFilePath)

        writeEvent2File(eventHash, score_eventHash, score_nodeHash, reverseSegHash, tStr, kNeib, taoRatio)


global UNIT
UNIT = "skl"

############################
## main Function
if __name__=="__main__":
    print "###program starts at " + str(time.asctime())

    global Day, segPairFileName, eventFileName  

    if len(sys.argv) > 2:
        Day = sys.argv[1]
        segPairFileName = sys.argv[2]
        eventFileName = sys.argv[3]
    elif len(sys.argv) == 2:
        Day = sys.argv[1]
    else:
        print "Usage getEvent.py day [segPairFileName] [eventFileName]"
        sys.exit()

    kNeib = 5
    taoRatio = 2

    dataFilePath = r"../ni_data/"

    wikiPath = "../data/anchorProbFile_all"

    if True:
        global wikiProbHash
        wikiProbHash = loadWiki(wikiPath)

    clusterEventSegment(dataFilePath, kNeib, taoRatio)

    # exp: for choosing suitable parameters
    #for kNeib in range(4,7):
    #    clusterEventSegment(dataFilePath, kNeib, taoRatio)
    #for taoRatio in range(3,6):
    #    clusterEventSegment(dataFilePath, kNeib, taoRatio)

    print "###program ends at " + str(time.asctime())
