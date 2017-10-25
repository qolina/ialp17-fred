# func: load content from tweet.txt file. recollect tweets in each day into seperate files
# sequence version is for original tweets arranged by time
# this version is for original tweets may not be arranged by time, and each days' tweet is stored into memory first.

import os
import sys
import re
import time
import json
import cPickle


sys.path.append(os.path.expanduser("~") + "/Scripts/")
from tweetStrOperation import *
from strOperation import *
from hashOperation import *

from Tweet import *

def loadTweetFromFile(dirPath):
    print "### " + str(time.asctime()) + " # Loading files from directory: " + dirPath
    # debug format
    loadDataDebug = True

    currDir = os.getcwd()
    os.chdir(dirPath)
    fileList = os.listdir(dirPath)
    fileList.sort()

    print fileList

    date_tweetHash = {} # date:lineStrList

    # for statistic
    dateHash = {} # date:tweetNum

    for item in fileList:
        print "## Processing file ", item
        jsonFile = file(item)
        firstLine = jsonFile.readline()

        lineIdx = 1
        while 1:
            lineStr = jsonFile.readline()
            if not lineStr:
                print "End of file. total lines: ", lineIdx
                break

            lineIdx += 1
            if lineIdx % 100000 == 0:
                print "Lines processed: ", lineIdx, " at ", time.asctime()

            lineStr = lineStr[:-1]
            if len(lineStr) < 20:
                continue

            # compile into json format
            try:
                jsonObj = json.loads(lineStr)
            except ValueError as errInfo:
                if loadDataDebug:
                    print "Non-json format! in lineNum:", lineIdx, lineStr
                continue

            # create tweet and user instance for current jsonObj
            currTweet = getTweet(jsonObj)
            if currTweet is None: # lack of id_str
                if loadDataDebug:
                    print "Null tweet (no id_str) in lineNum", lineIdx, str(jsonObj)
                continue
            # tweet.user_id is initialized to be empty 


            #################################
            # store into memory: date_tweetHash 
            # time filtering ,keep tweets between (20130101-20130115)
            currTime = readTime_fromTweet(currTweet.created_at)
            currDate = time.strftime("%Y-%m-%d", currTime)
            cumulativeInsert(dateHash, currDate, 1) # for statistic

            lineArr = []
            if currDate in date_tweetHash:
                lineArr = date_tweetHash[currDate]
            lineArr.append(lineStr)
            date_tweetHash[currDate] = lineArr


        jsonFile.close()

    for date in date_tweetHash:
        print "Create a new file for date", date

        output_rawTweetFile = file(dirPath + r"rawTwitter_timeCorrect-" + date, "w")

        for lineStr in date_tweetHash[date]:
            output_rawTweetFile.write(lineStr + "\n")

        output_rawTweetFile.close()


    if loadDataDebug:
        print "#tweet in dates: "
        print sorted(dateHash.items(), key = lambda a:a[0])
  
def getArg(args, flag):
    arg = None
    if flag in args:
        arg = args[args.index(flag)+1]
    return arg

def parseArgs(args):
    rawTweet_dirPath = getArg(args, "-dir")
    if rawTweet_dirPath is None:
        sys.exit(0)
    return rawTweet_dirPath

if __name__ == "__main__":
    print "Usage: python read_tweet_from_json.py -dir rawTweet_dirPath "
    print "       (eg. -dir ~/corpus/rawData_twitter201301 [search for .txt file to process])"

    print "Program starts at time:" + str(time.asctime())

    rawTweet_dirPath = parseArgs(sys.argv)

    loadTweetFromFile(rawTweet_dirPath)

    print "Program ends at time:" + str(time.asctime())
