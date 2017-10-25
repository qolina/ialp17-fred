#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Location: D:\TweetyBird_Lab\src\forparsing.py
#author: qolina
#Function: split id[tab]text into two files which contains ids and text separately.
# input is the tweetContentFiles after preprocessing.

import os
import re
import sys
import time
# from stemming.porter2 import stem
#from nltk import stem

## load normalized words
def loadNormword(normFilePath):
    normwordHash = {}
    normFile = file(normFilePath)
    while True:
        lineStr = normFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        arr = lineStr.split(" ")
        normwordHash[arr[0]] = arr[1]
    normFile.close()
    print "### " + str(time.asctime()) + " # " + str(len(normwordHash)) + " normalized words are loaded from " + normFilePath
    return normwordHash

########################################################
## Load users and tweets from files in directory dirPath
def loadDataFromFiles(dirPath, Day):
    print "### " + str(time.asctime()) + " # Loading files from directory: " + dirPath
    normedWords = {}
    currDir = os.getcwd()
    os.chdir(dirPath)
    fileList = os.listdir(dirPath)
    fileList.sort()
    lineIdx = 0
    for item in fileList:
        if not item.startswith("tweetContentFile"):
            continue
        if item[-2:] != Day:
            continue
        print "Reading from file " + ": " + item
        subFile = file(item)
        newIDFile = file(r"tid_" + item[-10:], "w")
        newtextFile = file(r"text_" + item[-10:], "w")
        while True:
            lineStr = subFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = re.sub(r'\s+', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break

            idEnd = lineStr.find(" ")
            textStr = lineStr[idEnd+1:]
            warr = textStr.split(" ")
            if len(warr) <= 1:
                continue

            # delete leading #hashtag words, delete tail #heshtag words
            while (len(warr) > 0) and (len(warr[0]) > 0) and (warr[0][0] == "#"):
                del warr[0]
            while (len(warr) > 0) and (len(warr[-1:]) > 0) and (warr[-1:][0] == "#"):
                del warr[-1:]
                #print "last word: " + warr[-1:]
                #print "updated words: " +  str(warr) + " len: " + str(len(warr))
            if len(warr) <= 1:
                continue
            if (len(warr) == 2) and ((warr[0][0] == "@") or (warr[1][0] == "@")):
                continue
            warrNew = []
            # delete RT and urls, delete # in #hashtag, replace ill-formed word with normed word
            for w in warr:
                if w == "RT":
                    continue
                if w.find("://") >= 0:
                    continue
                w = re.sub(r'#', '', w)
                if w in normwordHash:
                    normedWords[w] = 1
                    w = normwordHash[w]
                warrNew.append(w)
            if len(warrNew) <= 1:
                continue
            textStr = " ".join(warrNew)
            #print textStr

            newtextFile.write(textStr.encode("GBK", 'ignore') + "\n")
            newIDFile.write(lineStr[0:idEnd] + "\n")

            lineIdx += 1
            if lineIdx % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(lineIdx) + " tweets are processed. prepare for tagging."
        newIDFile.close()
        newtextFile.close()
        print "### " + str(time.asctime()) + " " + str(lineIdx) + " IDs are writen into " + newIDFile.name
        print "### " + str(time.asctime()) + " text are writen into " + newtextFile.name
        print "### " + str(time.asctime()) + " " + str(len(normedWords)) + " words are replaced by normed "
    
########################################################
## the main Function
currDir = os.getcwd()
dirPath = currDir + "/.." + r"/data/201301_preprocess"
normwordsFilePath = currDir + "/.." + r"/Tools/emnlp_dict.txt"

print "Program starts at time:" + str(time.asctime())
if len(sys.argv) == 2:
    Day = sys.argv[1]
else:
    print "Usage python fortagging.py day"
    sys.exit()

global normwordHash 
normwordHash = loadNormword(normwordsFilePath)
loadDataFromFiles(dirPath, Day)

print "Program ends at time:" + str(time.asctime())
