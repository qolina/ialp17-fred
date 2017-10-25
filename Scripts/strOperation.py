import re
import time


def readTime(timeStr):
    #Time format in tweet: "Sun Jan 23 00:00:02 +0000 2011"
    tweetTimeFormat = r"%a %b %d %X +0000 %Y"
    createTime = time.strptime(timeStr, tweetTimeFormat)
    return createTime


# normalize replication of character in string item. rep*n (n>3) -> rep*3
# eg: hhhhhaaaaaa->hhhaaa  wwwwwhhhhhyyyyy->wwwhhhyyy
# Problem: could not cover hahahahaha
def normRep(item):
    for match in re.findall(r"(((\w)+)\2{3,})", item):
#        print match
        if len(match[1]) == 1:
            item = re.sub(match[0], match[1]*3, item)
        if (len(match) > 2) and (len(match[2]) == 1):
            item = re.sub(match[0], match[2]*3, item)
            #print match
    return item

# lowercase the string
# replace_ and | to space[ ]
def cleanStr(textStr):
    textStr = re.sub("\|", " ", textStr)
    textStr = re.sub("_", " ", textStr)
    return textStr.lower()
    

# whether a word contain a prefix which in prefixArr and left part in suffixArr
def prefixIn(word, prefixArr, suffixArr):
    for prefix in prefixArr:
        if word.startswith(prefix) and (re.sub(prefix, "", word) in suffixArr):
            return True
    return False


# whether a string (rel) contain nested verb (v+clause)
def nestedVerbs(rel):
    rel = re.sub("_", " ", rel)
    wordArr_rel = rel.split(" ")
    nestedVerb1 = ["say", "suggest", "insist", "announce", "argue", "show", "claim", "maintain", "think", "hope", "wonder", "tell", "expect", "observe"]
    nestedVerb2 = ["said", "thought", "told"]
    suffixArr = ["", "s", "es", "ed", "d", "ing"]

    nestedArr1 = [1 for word in wordArr_rel if prefixIn(word, nestedVerb1, suffixArr)]
    nestedArr2 = [1 for word in wordArr_rel if word in nestedVerb2]

    if len(nestedArr1) + len(nestedArr2) > 0:
        return True
    return False


def splitWordTag(textStr, splitFlag):
    assert (textStr.find("/") > 0), "No need to split, words only: " + textStr
    tagArr = [word[word.rfind("/")+1:] for word in textStr.split(splitFlag)]
    wordArr = [word[:word.rfind("/")] for word in textStr.split(splitFlag)]
    return wordArr, tagArr


def copulas2be(word):
    if word in ["is", "are", "was", "were", "am"]:
        return "be"
    else:
        return word
 

def float_ratio(number):
    return float("%.2f"%number)

def replaceSpecialChar(egStr):
    egStr = re.sub(u"\u2026", "...", egStr)
    egStr = re.sub(u"\u2019|\u2018", "'", egStr)
    egStr = re.sub(u"\xa0", " ", egStr)
    egStr = re.sub(u"\ufffd|\U0001f449|\u25ba|\U0001f49f|\xa2|\U0001f4af|\U0001f608|\U0001f44c", "", egStr)
    egStr = re.sub(u"\u201c|\u201d", "'", egStr)
    egStr = re.sub(u"\u2013|\u2014", "-", egStr)
    egStr = re.sub(u"\u2022", ".", egStr)
    return egStr

def add_space_before_puncsInStr(egStr):
    if egStr.startswith("http"):
        return egStr
    if len(egStr) == 1:
        return egStr
    if not re.search("([!,.;?])", egStr):
        return egStr
#    print egStr
    punList = [33, 44, 46, 59, 63]
    wrongBoundList = range(10)
    wrongBoundList.append(" ")
    # ! , . ; ?
    newSen = egStr[0]
    for letterIdx in range(1, len(egStr)):
        letter = egStr[letterIdx]
        befChar = ""
        aftChar = ""
        encodeNum = ord(letter)
        if encodeNum in punList:
            if egStr[letterIdx-1] not in wrongBoundList:
                befChar = " "
            if letterIdx != len(egStr)-1 and egStr[letterIdx+1] not in wrongBoundList:
                aftChar = " "
        newSen += befChar+letter+aftChar

    newSen = re.sub("\s+", " ", newSen)
    return newSen
 
if __name__ == "__main__":
#    stringTest1 = ["hhhhhhaaaaa", "wwwwwhhhhhyyyyy"]
#    for test in stringTest1:
#        print test, normRep(test)
#    stringA = "hahahahaha"
#    print normRep(stringA)
    stringA = "USA,Bulgaria,....lot"
    print add_space_before_puncsInStr(stringA)
