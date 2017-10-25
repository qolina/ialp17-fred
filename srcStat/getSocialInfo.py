#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import cPickle
import sys
import json

sys.path.append("/path_to_fred/srcPreprocess")
sys.path.append("path_to_fred/Scripts")
from Tweet import *
from read_tweet_from_json import *
from strOperation import *  # readTime

def getSocialFeatures(currTweet):
    usrIDstr = currTweet.user_id_str
    timeStr = readTime(currTweet.created_at)
    hourStr = time.strftime("%H", timeStr)


    RT = False
    Men = False
    Reply = False
    Url = False
    RT1 = currTweet.retweeted
    if len(currTweet.text) > 5:
        partText = currTweet.text[0:4].lower()
        if partText.startswith("rt @"): 
            RT = True
            #print "rt @: " + str(currTweet.text[0:5])
    if len(currTweet.user_mentions) > 0:
        Men = True
        #print "Men: " + str(Men)
    if currTweet.in_reply_to_status_id_str != None:
        Reply = True
        #print "Reply: " + str(Reply)
    if len(currTweet.urls) > 0:
        Url = True
        #print "Url: " + str(Url)
    Fav = currTweet.favorited
    Tag = ""
    for tag in currTweet.hashtags:
        hashtag = "#" + tag["text"]
        Tag += hashtag + " "
    if len(Tag) > 1:
        Tag = Tag[:-1]
        #print Tag
    wordArr = currTweet.text.split(" ")
    Past = ""
    for word in wordArr:
        if word.endswith("ed"):
            Past += word + " "
    if len(Past) > 1:
        Past = Past[:-1]
        #print Past
        
    feahash = {}
    feahash["Usr"] = usrIDstr
    feahash["Time"] = hourStr
    #feahash["RT"] = RT
    #feahash["Men"] = Men
    #feahash["Reply"] = Reply
    #feahash["Url"] = Url
    #feahash["Fav"] = Fav
    #feahash["Tag"] = Tag
    #feahash["Past"] = Past
    return feahash

def read_rawFile(dataFileName, specificTidList):
    attriHash = {}
    tweetNum_t = 0

    jsonFile = file(dataFileName)

    firstLine = jsonFile.readline()
    jsonContents = jsonFile.readlines()
    print "File loaded done. start processing", len(jsonContents), time.asctime()
    jsonFile.close()

    for lineStr in jsonContents:
        lineStr = lineStr[:-1]
        lineStr = re.sub(r'\\\\', r"\\", lineStr)

        tweetNum_t += 1
        if tweetNum_t % 10000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed!"

        try:
            jsonObj = json.loads(lineStr)
        except ValueError as errInfo:
            if loadDataDebug:
                print "Non-json format! ", lineStr
            continue

        # create tweet and user instance for current jsonObj
        currTweet = getTweet(jsonObj)
        currUser = getUser(jsonObj)
        currTweet.user_id_str = currUser.id_str

        if currTweet is None: # lack of id_str
            if loadDataDebug:
                print "Null tweet (no id_str)" + str(jsonObj)
            continue

#        if currTweet.id_str in specificTidList:
        feahash = getSocialFeatures(currTweet)
        attriHash[currTweet.id_str] = feahash 

    return attriHash

# read file type 2
def read_structFile(dataFileName):
    attriHash = {}
    tweetNum_t = 0

    tweFile = file(dataFileName, "rb")
    while True:
        try:
            currTweet = cPickle.load(tweFile)
            tweetIDstr = currTweet.id_str

            feahash = getSocialFeatures(currTweet)
            attriHash[tweetIDstr] = feahash 
            tweetNum_t += 1
            if tweetNum_t % 10000 == 0:
                print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed!"
        except EOFError:
            print "### " + str(time.asctime()) + " tweets in " + item + " are loaded." + str(len(attriHash))
            tweFile.close()
            break
    return attriHash


def getTweetID(seggedFilePath):

    if not os.path.exists(seggedFilePath):
        return None
    inFile = file(seggedFilePath)
    content = inFile.readlines()
    inFile.close()
    tweetIdList = [line.split("\t")[0] for line in content]

    print "## ", len(tweetIdList), " tweets' Id are obtained. EG. ", tweetIdList[0]

    return tweetIdList

if __name__ == "__main__":

    print "###program starts at " + str(time.asctime())

    dayStr = sys.argv[1]

    dataFilePath = "path_to_fred/data/timeCorrect/"

    outputStr = "tweetSocialFeature"
    M = 12

    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("rawTwitter_timeCorrect-2013-01") != 0:
            print item
            continue
        tStr = item[-2:]
        if tStr != dayStr:
            continue

        print "### Processing " + item

        dataFileName = dataFilePath + item

        attriHash = read_structFile(dataFileName)

        # output into file
        outputFile = file(dataFilePath + outputStr  + tStr, "w")
        cPickle.dump(attriHash, outputFile)
        print "### tweetID:" + outputStr + " in time window " + tStr + " is dumped to " + outputFile.name
        outputFile.close()

    print "###program ends at " + str(time.asctime())
