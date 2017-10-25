import time

def readTime_fromTweet(timeStr):
    #Time format in tweet: "Sun Jan 23 00:00:02 +0000 2011"
    tweetTimeFormat = r"%a %b %d %X +0000 %Y"
    createTime = time.strptime(timeStr, tweetTimeFormat)
    return createTime
 
################################################
### filter out / replace special words in twitter wordsArr
# del all @usr, url in wordsArr
def tweWordsArr_delAllSpecial(wordsArr):
    wordsArr = tweWordsArr_delMen(wordsArr)
    wordsArr = tweWordsArr_delUrl(wordsArr)
    wordsArr = tweWordsArr_delRT(wordsArr)
    return wordsArr


########## del
# del all url
def tweWordsArr_delUrl(wordsArr):
    wordsArr = tweWordsArr_replaceFlag(wordsArr, "http", "")
    return wordsArr

# del all mention
def tweWordsArr_delMen(wordsArr):
    wordsArr = tweWordsArr_replaceFlag(wordsArr, "@", "")
    return wordsArr

# del all hashtag
def tweWordsArr_delHashtag(wordsArr):
    wordsArr = tweWordsArr_replaceFlag(wordsArr, "#", "")
    return wordsArr

# del all RT
def tweWordsArr_delRT(wordsArr):
    wordsArr = [word for word in wordsArr if word.lower() != "rt"]
    return wordsArr


########## replace
# replace mention into special tag like "@usr"
def tweWordsArr_replaceMen(wordsArr, replacedFlag):
    wordsArr = tweWordsArr_replaceFlag(wordsArr, "@", replacedFlag)
    return wordsArr


# replace url into special tag like "URL"
def tweWordsArr_replaceUrl(wordsArr, replacedFlag):
    wordsArr = tweWordsArr_replaceFlag(wordsArr, "http", replacedFlag)
    return wordsArr


# replace hashtag into special tag like "#hash"
def tweWordsArr_replaceHashtag(wordsArr, replacedFlag):
    wordsArr = tweWordsArr_replaceFlag(wordsArr, "#", replacedFlag)
    return wordsArr


# replace targetFlag in wordsArr into replacedFlag
def tweWordsArr_replaceFlag(wordsArr, targetFlag, replacedFlag):
    for widx in range(len(wordsArr)):
        if wordsArr[widx].startswith(targetFlag):
            wordsArr[widx] = replacedFlag
    wordsArr = [word for word in wordsArr if len(word) > 0]
    return wordsArr
