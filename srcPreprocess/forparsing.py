#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Location: D:\TweetyBird_Lab\src\forparsing.py
#author: qolina
#Function: replace USR with NN, Detele RT and URL
# input is the Tag_2013-01-* file after tagging

import os
import re
import sys
import time
# from stemming.porter2 import stem
#from nltk import stem

########################################################
## Load users and tweets from files in directory dirPath

def loadDataFromFiles(filepath, outDirPath):
    lineIdx = 0
    print "### " + str(time.asctime()) + " Reading from file " + ": " + filepath
    subFile = file(filepath)
    newTagtextFile = file(outDirPath + "/Tag" + os.path.basename(subFile.name), "w")
    while True:
        lineStr = subFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        lineIdx += 1

        lineStr = re.sub(r'_', "/", lineStr) # NNP or NN
        lineStr = re.sub(r'/USR', "/NN", lineStr) # NNP or NN
#            lineStr = re.sub(r'/HT', "/", lineStr)
        arr = lineStr.split(" ")
        noRTarr = list([w for w in arr if w[w.rfind("/")+1:] != "RT"])
        noURLarr = list([w for w in noRTarr if w[w.rfind("/")+1:] != "URL"])
        if len(noURLarr) == 0:
            newTagtextFile.write("---/P\n")
            continue
        if (len(noURLarr) == 1) & (noURLarr[0][0] == "@"):
            noURLarr[0] = "---/P"
        newTagtextFile.write(" ".join(noURLarr) + "\n")
    newTagtextFile.close()
    
########################################################
## the main Function
currDir = os.getcwd()
#dirPath = currDir + "/.." + r"/data/201301_preprocess"
dirPath = currDir

print "Program starts at time:" + str(time.asctime())

if len(sys.argv) == 2:
    loadDataFromFiles(sys.argv[1], "./")
elif len(sys.argv) == 3:
    loadDataFromFiles(sys.argv[1] + r"/" + sys.argv[2], sys.argv[1])
else:
    print "Usage: python forparsing.py -dirpath -filename\n"

print "Program ends at time:" + str(time.asctime())
