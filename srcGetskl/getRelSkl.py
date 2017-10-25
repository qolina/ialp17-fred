import os
import sys
import re
import time
import cPickle

sys.path.append("/home/yxqin/Scripts")
from strOperation import * # normRep and cleanStr

from synConstraint_reverb import * # getVerbs(get verbs satisfy regular expression), mergeAdj (merge adjacent verb rels)

####################################
#get relation skeletons from self complemented relation extraction
def getRelskl_fromPOS(filename, chunkedFilename):
    print "Processing " + filename
    global lexHash
    posFile = file(filename)
    outputDir = os.path.split(filename)[0]
    tStr = filename[-5:-3]#[:3]#[-6:-4]
    if not lex:
        npHash = getNPs(chunkedFilename)
        #outputFile = file(outputDir + r"/relSkl_2013-01-" + tStr, "w")
        outputFile = file(outputDir + r"/relSkl_2015-05-" + tStr, "w")
        #outputFile_w2v = file(outputDir + r"/w2v_2013-01-" + tStr, "w")
        ## with lexical constraint
        #lexHash = loadLex(outputDir)
        #lexHash = dict([(rel, lexHash[rel]) for rel in lexHash if lexHash[rel]>5])

    # calculate lexical constraint   
    #lexHash = dict([(rel, lexHash[rel]) for rel in lexHash if lexHash[rel]>1])

    tagHash = {}
    lineIdx = 0
    while 1:
        lineStr = posFile.readline()
        if len(lineStr) <= 0:
            print str(lineIdx) + " lines are processed. End of file. " + str(time.asctime())
            break
        lineStr = lineStr[:-1]
        lineIdx += 1

        #print "************************* " + str(lineIdx)
        arr = lineStr.split(" ")
#        print arr
        wordArr = [word[:word.rfind("/")] for word in arr]
        tagArr = [word[word.rfind("/"):] for word in arr]
#        print tagArr
#        break


        # skip tweets with /FW(foreign word)
        fwArr = [1 for tag in tagArr if tag.startswith("/FW")]
        if len(fwArr) > 0:
            #print "#tweet with FW: " + lineStr
            continue

        # statistic tags appeared
        for tag in tagArr:
            if tag in tagHash:
                tagHash[tag] += 1
            else:
                tagHash[tag] = 1

        npArr = npHash.get(lineIdx-1)
        resultArr = getRelsFromOneTweet(tagArr, arr, npArr)
        if len(resultArr) > 0:
#            print resultArr
            outputFile.write(tStr+str(lineIdx-1) + "\t" + " ".join(resultArr) + "\n")

            #w2vText = getw2vContext(resultArr, wordArr)
            #outputFile_w2v.write(w2vText + "\n")

        # get noiseWords
#        if not os.path.exists("noise"+filename[-5:-3]):
#            getNoise(arr, resultArr)
#        else:
#            delUnTrueNoiseWord(resultArr)
            
        if lineIdx % 10000 == 0:
            print "# tweets processed: " + str(lineIdx) + " at " + str(time.asctime())
    if not lex:
        print "Appeared tags: ",
        print sorted(tagHash.keys())
        outputFile.close()
    posFile.close()
    #outputFile_w2v.close()


def getRelsFromOneTweet(tagArr, arr, initNPs):

    tagStr = " ".join(tagArr) + " "
    #print "TagStr: " + tagStr

    # get verbs
    verbIdx = getVerbs(tagStr, arr)
    #print verbIdx
    ## merge adjacent verb rels
    newIdx = mergeAdj(verbIdx)
#    print newIdx

    # construct lexical constraint-Dcorpus
#    if lex:
#        constructLexCorp(arr, newIdx) # update lexHash
#        if lineIdx % 100000 == 0:
#            print "# tweets processed: " + str(lineIdx) + " at " + str(time.asctime())
#        continue

    # op1: take nearest NN as argument
    npArr = []
    #resultArr = getArgs_chunk(newIdx, tagArr, arr, npArr)

    # chunk version 0
    # op2: take nearest chunked NP as argument
    #'''
    npArr = initNPs

    #'''
    # op3: take nearest chunked NP(DIY) as argument
    # chunkNew version 1/2/3
    #print npArr
    #print arr
    npArr = getNPDIY(tagArr, npArr, arr)

    resultArr = getArgs_chunk(newIdx, tagArr, arr, npArr)
    return resultArr

# prepare context text for word2vec. consider frame element as one word
## oriTweet: _a_b_c_d_e_f_g_
## rels: b_c e_f
## replacedTweet: _a_0_d_1_g_
## output context: a b_c d e_f g
def getw2vContext(relsArr, wordArr):
    puncArr = [',','.',';','?','!','#','&','<','>']
    nopuncWordArr = []
    tempArr = [nopuncWordArr.append(w) for w in wordArr if w not in puncArr]
    wordsStr = "_".join(nopuncWordArr).lower()
    mixWordsStr = "_" + wordsStr + "_"
    
    relsStr = " ".join(relsArr)
    relsStr = re.sub("\|", " ", relsStr)
    relEleArr = relsStr.strip().split(" ")
    #print lineIdx,
    #print "..Relations: ",
    #print relsArr
    #print "Ori tweet: " + wordsStr
    #print "Rels: ",
    #print relEleArr
    eleLenHash = dict([(i,len(relEleArr[i])) for i in range(len(relEleArr))])
    sortedList = sorted(eleLenHash.items(), key = lambda a:a[1], reverse = True)
    for item in sortedList:
        idx = item[0]
        relEle = relEleArr[idx]
        try:
            mixWordsStr = re.sub("_%s_"%relEle, "_"+str(idx)+"_", mixWordsStr)
        except Exception:
            print "Replacement error! Illegal character in relEle: ", relEle
            break

    #print "Replaced tweet: " + mixWordsStr
    mixWordArr = mixWordsStr.split("_")
    w2vArr = []
    for mixWord in mixWordArr:
        if mixWord.isdigit() and (int(mixWord) < len(relEleArr)):
            w2vArr.append(relEleArr[int(mixWord)])
        else:
            w2vArr.append(mixWord)

    w2vArr = normMen(w2vArr)
    w2vText = " ".join(w2vArr)
    #print "context: " + w2vText
    return w2vText

# get noise words which are filtered out in frame extraction
def getNoise(arr, resultArr):
    global noiseHash
    words = getWord(arr, 0, len(arr)).lower().split("_")

    relStr = " ".join(resultArr)
    relStr = cleanStr(relStr)
    relArr = relStr.split(" ")
    noiseArr = [word for word in words if word not in relArr]
    #print words
    #print relArr
    #print noiseArr
    for word in noiseArr:
        if word in noiseHash:
            noiseHash[word] += 1
        else:
            noiseHash[word] = 1

def delUnTrueNoiseWord(resultArr):
    global noiseHash
    relStr = " ".join(resultArr)
    relStr = cleanStr(relStr)
    relArr = relStr.split(" ")
    for word in relArr:
        if word in noiseHash:
            del noiseHash[word]
    
def constructLexCorp(arr, newIdx):
    global lexHash
    vbArr = [getWord(arr, st, newIdx[st]) for st in sorted(newIdx.keys())]
    if len(vbArr) == 0:
        return 0
    #print vbArr
    for vb in vbArr:
        if vb in lexHash:
            lexHash[vb] += 1
        else:
            lexHash[vb] = 1

########################################################
# replace mention with @usr
def normMen(relArr):
    relArrUSR = []
    for wd in relArr:
#        if wd.find("#") >= 0:
#            continue
        if len(wd) <= 0:
            continue
        if wd[0] == "@" and len(wd) > 1:
            wd = "@usr" # op1
            #continue # op2
        wd = re.sub(r"\|", "", wd) # | is used as separator later for frame
        relArrUSR.append(wd)
    return relArrUSR

def getNPs(chunkedFilename):
    npHash = {}
    # eg. r"/Chunktext_2013-01-" + tStr
    chFile = file(chunkedFilename)
    lineIdx = 0
    while 1:
        lineStr = chFile.readline()
        if len(lineStr) <= 0:
            print str(lineIdx) + " lines are processed. End of file. NPs obtained." + str(time.asctime())
            break
        lineStr = lineStr[:-1]
        if lineStr[-1:] == "]":
            lineStr = lineStr[:-1] + " ]"
        lineIdx += 1

        arr = lineStr.split(" ")
        #print "**** " + str(arr)
        #wArr = [w[:w.find("/")] for w in arr if w.find("/")>=0]
        bArr = [i for i in range(len(arr)) if arr[i].find("/") < 0]
        #print bArr
        npIdx = [(bArr[2*i]+1-(2*i+1), bArr[2*i+1]-1-(2*i+1)) for i in range(len(bArr)/2)]
        #print npIdx
        #npArr = ["_".join(wArr[item[0]:item[1]+1]) for item in npIdx] 
        #print npArr

        if len(npIdx) > 0:
            npHash[lineIdx-1] = npIdx
        #if lineIdx % 100000 == 0:
            #print "# tweets processed: " + str(lineIdx) + " at " + str(time.asctime()) + " npHash: " + str(len(npHash))
            #break
    print "## " + str(len(npHash)) + " tweets contain np are obtained."
    return npHash

def getWord(arr, st, ed):
    if st == -1:
        return ""
    wordArr = normMen([w[:w.rfind("/")] for w in arr[st:ed+1]])
    return "_".join(wordArr)
    
def normRelation(rel, arg1, arg2):
    relArr = [arg1, rel, arg2]
#    relArr = [normRep(w.lower()) for w in relArr if len(w) > 1]
    relArr = [normRep(w.lower()) for w in relArr]
    #print relArr
    return relArr

def getlnnIdxes(tagArr, st, arr):
    arg1Idx = -1
    lidx = getlnnIdx(tagArr, st)
    if lidx != -1:
        if (lidx-1 >= 0) and (tagArr[lidx-1].startswith("/NN")):
            #arg1 = getWord(arr, lidx-1, lidx)
            arg1Idx = (lidx-1, lidx)
        else:
            #arg1 = getWord(arr, lidx, lidx)
            arg1Idx = (lidx, lidx)
    return arg1Idx

def getrnnIdxes(tagArr, ed, arr):
    arg2Idx = -1
    ridx = getrnnIdx(tagArr, ed)
    if ridx != -1:
        if (ridx+1 < len(tagArr)) and (tagArr[ridx+1].startswith("/NN")):
            #arg2 = getWord(arr, ridx, ridx+1)
            arg2Idx = (ridx, ridx+1)
        else:
            #arg2 = getWord(arr, ridx, ridx)
            arg2Idx = (ridx, ridx)
    return arg2Idx

def getlnnWord(tagArr, st, arr):
    arg1 = ""
    lidx = getlnnIdx(tagArr, st)
    if lidx != -1:
        arg1 = getWord(arr, lidx, lidx)
    return arg1

def getrnnWord(tagArr, ed, arr):
    arg2 = "" 
    ridx = getrnnIdx(tagArr, ed)
    if ridx != -1:
        #arg2 = arr[ridx] 
        #arg2 = arg2[:arg2.rfind("/")]
        arg2 = getWord(arr, ridx, ridx)
    return arg2

def getlnnIdx(tagArr, st):
    lidx = st - 1
    while lidx >= 0:
        if not tagArr[lidx].startswith("/NN"):
            lidx -= 1
            continue
        return lidx
    return -1

def getrnnIdx(tagArr, ed):
    ridx = ed+1
    while ridx < len(tagArr):
        if not tagArr[ridx].startswith("/NN"):
            ridx += 1
            continue
        return ridx
    return -1

def lStripArr(tagArr, item, tag):
    if item is None:
        return None
    st = item[0]
    ed = item[1]
    while tagArr[st] == tag:
        st += 1
        #print "Tag: " + tag + ": " + str(item)
        if st > ed:
            return None
    return (st, ed)

def rStripArr(tagArr, item, tag):
    #strip tag(/UH) in item range of tagArr
    if item is None:
        return None
    st = item[0]
    ed = item[1]
    while tagArr[ed] == tag:
        ed -= 1
        #print "Tag: " + tag + ": " + str(item)
        if st > ed:
            return None
    return (st, ed)

def stripArr(tagArr, item, tag):
    if item is None:
        return None
    item = lStripArr(tagArr, item, tag)
    item = rStripArr(tagArr, item, tag)
    return item

# separate NP into NPs if punctuations inside NP
def getNewNP(tagArr, item, arr):
    item = stripArr(tagArr, item, "/UH")
    item = stripArr(tagArr, item, "/,")
    item = stripArr(tagArr, item, "/.")
    # following two lines are added in Mar. 13, 2015. chunking result take ( or ) as a np
    item = stripArr(tagArr, item, "/-LRB-")
    item = stripArr(tagArr, item, "/-RRB-")
    # to be added to improve np chunking in twitter
#    if item[1]-item[0] > 0:
#        item = rStripArr(tagArr, item, "URL")
#        item = rStripArr(tagArr, item, "HT")


    if item is None:
        return None

    newItems = []
    st = item[0]
    ed = item[1]

    # split NPs with /, /. tag
    puncArr = [id for id in range(st, ed+1) if (tagArr[id].startswith("/,") or tagArr[id].startswith("/."))]
    if len(puncArr) > 0:
        #print "NP with punc: " + "_".join(arr[item[0]:item[1]+1])
        #if len(puncArr) > 1:
            #print "##Multiple puncs"
        i = 0
        while i < len(puncArr):
            id = puncArr[i]
            if tagArr[id-1].startswith("/NN"):
                if i == 0:
                    newItems.append((st, id-1))
                else:
                    newItems.append((puncArr[i-1]+1, id-1))
            if i == len(puncArr)-1:
                if tagArr[ed].startswith("/NN"):
                    newItems.append((puncArr[i]+1, ed))
            i += 1
    else:
        newItems.append((st, ed))

    #print newItems

#    # chunkNewV1-part2
#    # chunkNewV2 skip this part compared with V1
#    # do not use this part in chunkNewV2 and later chunkNew version(appeared in V4)
#    # lead to worse precision
#    items = []
#    for it in newItems:
#        st = it[0]
#        ed = it[1]
#        # delete chunk without /NN
#        nounArr = [id for id in range(st, ed+1) if tagArr[id].startswith("/NN")]
#        if len(nounArr) < 1:
#            #print "chunk without noun: " + "_".join(arr[st: ed+1])
#            continue
#        usrArr = [id for id in range(st, ed+1) if not arr[id].startswith("@")]
#        # check chunks with length >= 5
#        if ed-st+1 >= 5:
#            if ed-st+1-len(usrArr) < 5: # < 5 when delete @usr(later)
#                items.append((st,ed))
#            if len(nounArr) <= 3:
#                items.append((st,ed))
#        
#    return items

    return newItems
    
def getNPDIY(tagArr, npArr, arr):
    if npArr is None:
        return None
    newNPArr = []
    #print "*************************************"
    #print tagArr
    #print npArr
    for item in npArr:
        newItems = getNewNP(tagArr, item, arr)
        if newItems is not None:
            newNPArr.extend(newItems)
    #print newNPArr
    return newNPArr

# should not be EX, WDT, WP, WP$
def validArg(idx_tuple, arr, tagArr):
    tags_arg = tagArr[idx_tuple[0]:idx_tuple[1]+1]
    tags_arg = [tag[tag.find("/")+1:]for tag in tags_arg]
    inValidTags = ['WDT', 'WP', 'WP$', # relative pronoun, which, that, who, whom, whose
#            '', # who-adverb ??
            'EX'] # existential there
    invalid = [1 for tag in tags_arg if tag in inValidTags]
    if len(invalid) > 0:
        return False
    return True


def getRelationIdx(newIdx, tagArr, arr, npArr):
    relationIdxArr = []
    for st in sorted(newIdx.keys()):
        ed = newIdx[st]

        relIdx = (st, ed)
        [arg1Idx, arg2Idx] = getArgsIdx_chunk(relIdx, tagArr, arr, npArr)

        relationIdxArr.append((relIdx, arg1Idx, arg2Idx))
    return relationIdxArr


def getArgs_chunk_new(newIdx, tagArr, arr, npArr):
    resultArr = []
    # detect argument in left and right
    relationIdxArr = getRelationIdx(newIdx, tagArr, arr, npArr)

    for relationIdx in relationIdxArr:
        [relIdx, arg1Idx, arg2Idx] = relationIdx

        rel = getWord(arr, relIdx[0], relIdx[1])
        arg1 = getWord(arr, arg1Idx[0], arg1Idx[1])
        arg2 = getWord(arr, arg2Idx[0], arg2Idx[1])

        relArr = normRelation(rel, arg1, arg2)
#        if rel not in lexHash: # lexical constraint
#            continue

        if len(relArr) != 3:
            print "Not triple."
            continue

        resultArr.append("|".join(relArr))
    return resultArr


def getArgs_chunk(newIdx, tagArr, arr, npArr):
    global confFeas
    resultArr = []
    for st in sorted(newIdx.keys()):
        ed = newIdx[st]
        arg1 = "" 
        arg2 = "" 

        relIdx = (st, ed)
        rel = getWord(arr, st, ed)
#        if rel not in lexHash: # lexical constraint
#            continue

        [arg1Idx, arg2Idx] = getArgsIdx_chunk(relIdx, tagArr, arr, npArr)

        arg1 = getWord(arr, arg1Idx[0], arg1Idx[1])
        arg2 = getWord(arr, arg2Idx[0], arg2Idx[1])

        relArr = normRelation(rel, arg1, arg2)
#        print rel
#        print "relation: ",
#        print relArr

        # calculate confidence
#        confArr = fea_Conf(arr, tagArr, relArr, rel, st, ed, arg1Idx, arg2Idx)
#
#        for i in range(len(confFeas)):
#            if confArr[i] == 1:
#                confFeas[i] += 1
#        confVal = confidence(confArr)
#        #print confArr
#        if confVal <= 0:
#            #print "Skip " + str(relArr) + "\t" + str(confVal)
#            continue
#        #else:
#            #print "Keep " + str(relArr) + "\t" + str(confVal)

        #if len(relArr) > 0:
            #resultArr.append("|".join(relArr))
        if len(relArr) != 3:
            print "Not triple."
            continue

#        for rel in relArr:
#            if rel.find("|") >= 0:
#                print arr
#                print "| appeared in rel: ", rel


#        global lvHash
#        print "-- relword: ", relArr[1]
#        lvArr = ["is", "do", "give", "have", "make", "take", "get", "was", "were", "are", "did", "does", "gave", "had", "has", "makes", "made", "takes", "took", "gets", "got"]
#        relWords = relArr[1].split("_")
#        if len(relWords)==1 and relArr[1] in lvArr:
#            print "-- verb=lv: ", relArr[1], " ", arr
#            if relArr[1] in lvHash:
#                lvHash[relArr[1]] += 1
#            else:
#                lvHash[relArr[1]] = 1
#        else:
#            for w in relWords:
#                if w in lvArr:
#                    print "-- contain lv-verb: ", relArr[1], " ",arr
#                    tmpWord = "c-"+w
#                    if tmpWord in lvHash:
#                        lvHash[tmpWord] += 1
#                    else:
#                        lvHash[tmpWord] = 1


        # triple structure
        resultArr.append("|".join(relArr))

        # 2-tuple structure
        #resultArr.append("|".join(relArr[0:2]))
        #resultArr.append("|".join(relArr[1:]))
    return resultArr


def getArgsIdx_chunk(relIdx, tagArr, arr, npArr):
    st = relIdx[0]
    ed = relIdx[1]

    arg1Idx = -1
    arg2Idx = -1

    if npArr is not None and len(npArr) > 0:# with chunking results
        idx = len(npArr)-1
        while idx >= 0:
            item = npArr[idx]
            
            if item[1] < st and validArg(item, arr, tagArr):
                #arg1 = getWord(arr, item[0], item[1])
                arg1Idx = item
                break
            idx -= 1
        idx = 0
        while idx < len(npArr):
            item = npArr[idx]
            if item[0] > ed and validArg(item, arr, tagArr):
                #arg2 = getWord(arr, item[0], item[1])
                arg2Idx = item
                break
            idx += 1
    else: # no chunking results
        ## get nearest /NN tagged word
#            arg1 = getlnnWord(tagArr, st, arr)
#            arg2 = getrnnWord(tagArr, ed, arr)

    ## get nearest /NN tagged word[s]
        arg1Idx = getlnnIdxes(tagArr, st, arr)
        arg2Idx = getrnnIdxes(tagArr, ed, arr)

    ## chunkNewV3: if no chunk is found for argument, take nearest nn as argument
    ## get Index 2/24/2014
    if arg1Idx == -1:
        arg1Idx = getlnnIdx(tagArr, st)
        arg1Idx = (arg1Idx, arg1Idx)
    if arg2Idx == -1:
        arg2Idx = getrnnIdx(tagArr, ed)
        arg2Idx = (arg2Idx, arg2Idx)

    ## In chunkNewV3
    # getWord directly
#    if len(arg1) <= 1:
#        ## get nearest /NN tagged word
#        arg1 = getlnnWord(tagArr, st, arr)
#    if len(arg2) <= 1:
#        arg2 = getrnnWord(tagArr, ed, arr)

    ## chunkNewV3_NNs: if no chunk is found for argument, take nearest NN[s] as argument
    # worse than chunkNewV3
#    if len(arg1) <= 1:
#        ## get nearest /NN tagged word[s]
#        arg1 = getlnnWords(tagArr, st, arr)
#    if len(arg2) <= 1:
#        arg2 = getrnnWords(tagArr, ed, arr)


    return arg1Idx, arg2Idx


def fea_Conf(arr, tagArr, relArr, rel, st, ed, arg1Idx, arg2Idx):
    # confidence score
    confArr = [0]*19
    arg1 = ""
    if arg1Idx != -1:
        arg1 = getWord(arr, arg1Idx[0], arg1Idx[1])
    
    ## calculate confidence
    relStr = "|".join(relArr)
    relStr = re.sub("_", "|", relStr)
    if len(relStr.split("|")) == len(arr):
        confArr[0] = 1
    if rel.split("_")[-1] == "for":
        confArr[1] = 1
    if rel.split("_")[-1] == "on":
        confArr[2] = 1
    if rel.split("_")[-1] == "of":
        confArr[3] = 1
    if len(arr) <= 10:
        confArr[4] = 1

    whTags = [1 for tag in tagArr[:st] if tag.startswith("/W")]
    if len(whTags) > 0:
        confArr[5] = 1
    tagStr = " ".join(tagArr[st:ed+1]) + " "
    if re.match(r"(%s)"%LONG_RELATION_PATTERN, tagStr):
        confArr[6] = 1
    if rel.split("_")[-1] == "to":
        confArr[7] = 1
    if rel.split("_")[-1] == "in":
        confArr[8] = 1
    if (len(arr) > 10) and (len(arr) <= 20):
        confArr[9] = 1
        
    wordStr = "_".join(normMen([w[:w.rfind("/")] for w in arr]))
    if wordStr.startswith(arg1):
        confArr[10] = 1
    if arg1Idx != -1:
        if isNP(tagArr, arg1Idx):
            confArr[11] = 1
        if arg1Idx[0] > 0:
            leftNP = [1 for tag in tagArr[0:arg1Idx[0]] if tag.startswith("/NNP")]
            if len(leftNP) > 0:
                confArr[13] = 1
        if arg1Idx[0] > 0:
            partTagStr = " ".join(tagArr[0:arg1Idx[0]])
            if re.match(r"(%s)"%PREP, partTagStr):
                confArr[16] = 1

    if arg2Idx != -1:
        if isNP(tagArr, arg2Idx):
            confArr[12] = 1
        if arg2Idx[1] < len(arr)-1:
            rightNP = [1 for tag in tagArr[arg2Idx[1]:] if tag.startswith("/NNP")]
            if len(rightNP) > 0:
                confArr[17] = 1

    if len(arr) > 20:
        confArr[14] = 1
    if ed == st:
        confArr[15] = 1

    if st > 0:
        leftCC = [1 for tag in tagArr[0:st] if tag.startswith("/CC")]
        if len(leftCC) > 0:
            confArr[18] = 1
    return confArr

def confidence(confArr):
    weightArr = [1.16, 0.5, 0.49, 0.46, 0.43, #0-4
              0.43, 0.42, 0.39, 0.25, 0.23,#5-9
              0.21, 0.16, 0.01,            #10-12
              -0.3, -0.43, -0.61, -0.65, -0.81, -0.93]#13-18
    val = 0.0
    score = [confArr[i]*weightArr[i] for i in range(len(weightArr))]
    val = sum(score)
    return val

def isNP(tagArr, wIdx):
    st = wIdx[0]
    ed = wIdx[1]
    if st == -1:
        return False
    if tagArr[ed].startswith("/NNP"):
        return True
    return False


def getLexRel(filename):
    global lex
    lex = True
    outputDir = os.path.split(filename)[0]
    tArr = [str(i).zfill(2) for i in range(1, 16)]
    for tStr in tArr:
        filename = filename[:-5] + tStr + filename[-3:]
        getRelskl_fromPOS(filename)
        print filename + " --",
        print len(lexHash)
    oHash = dict([(rel, lexHash[rel]) for rel in lexHash if lexHash[rel]==1])
    tHash = dict([(rel, lexHash[rel]) for rel in lexHash if lexHash[rel]==2])
    thHash = dict([(rel, lexHash[rel]) for rel in lexHash if lexHash[rel]==3])
    fHash = dict([(rel, lexHash[rel]) for rel in lexHash if lexHash[rel]==4])
    fiHash = dict([(rel, lexHash[rel]) for rel in lexHash if lexHash[rel]==5])
    newlexHash = dict([(rel, lexHash[rel]) for rel in lexHash if lexHash[rel]>5])
    print "Statistics of verb under lexical constraint."
    print len(lexHash)
    print len(oHash)
    print len(tHash)
    print len(thHash)
    print len(fHash)
    print len(fiHash)
    print len(newlexHash)

    lexDicFile = file(outputDir + r"/lex.dic", "w")
    cPickle.dump(newlexHash, lexDicFile)
    '''
    sortedList = sorted(newlexHash.items(), key = lambda a:a[1])
    for it in sortedList:
        lexDicFile.write(it[0] + str(it[1]) + "\n")
    '''
    lexDicFile.close()

def loadLex(outputDir):
    lexDicFile = file(outputDir + r"/lex.dic")
    lexverb = cPickle.load(lexDicFile)
    lexDicFile.close()
    return lexverb 
    
##############################################################
## filter out unTrue noisy words which appear in other tweets
#noiseFilename = "noise"+filename[-5:-3]
#if os.path.exists(noiseFilename):
#    global noiseHash
#    noiseFile = file(noiseFilename)
#    noiseHash = cPickle.load(noiseFile)
#    noiseHash = dict([(w.lower(), noiseHash[w]) for w in noiseHash])
#    print str(len(noiseHash)) + " noise words are loaded."
#    noiseFile.close()
##############################################################

####################################
#main
if __name__ == "__main__":
    # lexical constaint
    lexHash = {}
    lex = False
    # confidence score
    confFeas = [0]*19
    # noise words
    noiseHash = {}
    # light verb checking
    lvHash = {}


    if len(sys.argv) == 3:
        filename = sys.argv[1]
        chunkedFilename = sys.argv[2]
        getRelskl_fromPOS(filename, chunkedFilename) # extract skl from Postagged file(self-completed reverb)
    elif len(sys.argv) == 4:
        filename = sys.argv[1]
        chunkedFilename = sys.argv[2]
        getLexRel(filename, chunkedFilename) # use lexical constraint and confidence
    else:
        print "Usage getRelSkl.py posFileName chunkedFileName [lex] "
        sys.exit()

    #print sorted(lvHash.items(), key = lambda a:a[0])
    #print sorted(lvHash.items(), key = lambda a:a[1])
    
    ##############################################################
    # record noisy words which does not appear in frames in one tweet
#    if not os.path.exists(noiseFilename):
#        print "############### output Noisy words " + str(time.asctime())
#        noiseFile = file("noise"+filename[-5:-3], "w")
#    else:
#        print "############### output New noisy words " + str(time.asctime())
#        noiseFile = file("NewNoise"+filename[-5:-3], "w")
#    print len(noiseHash)
#    cPickle.dump(noiseHash, noiseFile)
#    
#    for item in sorted(noiseHash.items(), key = lambda a:a[1], reverse = True):
#        #noiseFile.write(item[0] + " " + str(item[1]) + "\n")
#        print item
#    noiseFile.close()
    ##############################################################

    print "Program ends at " + str(time.asctime())
