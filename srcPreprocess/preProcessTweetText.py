import sys
import os
import cPickle

sys.path.append(os.path.expanduser("~")+"/Scripts")
from sysOperation import *
from strOperation import *
from tweetStrOperation import *
from fileOperation import *

#########  Procedures
# tweetClean:
#    delete illegal: 
#        delete non-valid Url, 
#        delete illegeLetter in mention, 
#        delete words with puncs only, 
#        changeCode2char, 
#        strip illegal letter in word, 
#        delete illegal letter in word, 
#        delete illegal letter in hashtag
#    add space before punctuations: !,.;?
#    stem words
#    delete stopwords
# delete 0-length cleanedText
# del tweets with no normal words, which are not Mention, Url, RT; del tweets with one Hashtag

#stemmer = stem.PorterStemmer()
#engDetector = enchant.Dict("en_US")
#@profile
def tweetTextCleaning_infile(textFileName, outFileName):
    # debug format
    debugFlag = True

    # for statistics when debugging
    statisticArr = [0, 0] # 0-length tweets, mention-url-RT-only tweet

    outputFlag_text = False
    if outFileName is not None:
        outputFlag_text = True
        out_textFile = file(outFileName, "w")

    textFile = file(textFileName)

    lineIdx = 0
    while 1:
        try:
            lineStr = cPickle.load(textFile)
#            lineStr = textFile.readline()
        except EOFError:
            print "End of file. total lines: ", lineIdx
            break
        lineStr = lineStr.strip()

        lineIdx += 1
        if lineIdx % 100000 == 0:
            print "Lines processed: ", lineIdx, " at ", time.asctime()

        [tweet_id, tweet_text] = lineStr.split("\t")
        #print tweet_id, tweet_text

        cleaned_text = tweetClean(tweet_text)

        # special case filtering
        if len(cleaned_text) < 1:
            if debugFlag:
                statisticArr[0] += 1
            continue

        wordsArr_normalWord = tweWordsArr_delAllSpecial(cleaned_text.split(" "))
        if len(wordsArr_normalWord) < 1 or oneHTArr(wordsArr_normalWord):
            if debugFlag:
                statisticArr[1] += 1
            continue

        if outputFlag_text:
            out_textFile.write(tweet_id + "\t" + cleaned_text + "\n")

    if debugFlag:
        print "Statictis of 0-length, all-special-tag tweets", statisticArr

    textFile.close()
    if outputFlag_text:
        out_textFile.close()
 
def oneHTArr(wordsArr):
    if len(wordsArr) == 1 and wordsArr[0].startswith("#"):
        return True

#@profile
def tweetClean(text):
    wordsArr = text.split(" ")
    wordsArr = tweetArrClean_delIllegal(wordsArr)
    wordsArr = tweetArrClean_spcBefPunc(wordsArr)

#    wordsArr = tweetArr_stem(wordsArr)

#    stopFileName = r"~/Tools/stoplist.dft"
#    stopwordHash = loadStopword(stopFileName)
#    wordsArr = tweetArrClean_delStop(wordsArr, stopwordHash)

    return " ".join(wordsArr)

def tweetArr_stem(wordsArr):
    wordsArr = [stemmer.stem(word) for word in wordsArr]
    return wordsArr

def tweetArrClean_spcBefPunc(wordsArr):
    wordsArr = [add_space_before_puncsInStr(word) for word in wordsArr]
    return wordsArr

def tweetArrClean_delStop(wordsArr, stopwordHash):
    wordsArr = [word for word in wordsArr if word not in stopwordHash]
    return wordsArr

def tweetArrClean_delUrl(wordsArr):
    wordsArr = [word for word in wordsArr if word.find("http") < 0]
    return wordsArr

#@profile
def tweetArrClean_delIllegal(wordsArr):
    newArr = []
    for word in wordsArr:
#        if re.search('http',word):  # keep urls
        if word.find("http") >= 0:
            if not getValidURL(word):
                continue

            newArr.append(getValidURL(word))
            continue        

        if word.find("@") >= 0: # mention
            word = word[word.find("@"):]
            word = re.sub("[^@a-zA-Z0-9_]"," ",word) # catenation of mention and other words
            newArr.append(word)
            continue
 
        hashTagWordCopy = ""
        if word.startswith("#"):
            hashTagWordCopy = word
            word = word[1:]
       
        if len(word) > 1 and contain_only_punc_in_word(word):
            continue

        word = code2char(word)

        word = strip_nonLetter_in_word(word)
        if len(word) < 1:
            continue

        if contain_illegal_letter_in_word(word):
            continue

        if len(hashTagWordCopy)>1: # if hashtag word contains illegal letter, remove it
            newArr.append("#"+word)
            continue

        newArr.append(word)
    return newArr 

def getValidURL(word):
    if not word.startswith("http"):
        return None
    if len(word)<20:
        return None
    if contain_illegal_letter_in_word(word):
        return None
    if len(word) > 20:
        return word[:20]

# replace code like &lt; &gt; to < > in word
def code2char(word):
#    word = re.sub("&lt;","<", word)
#    word = re.sub("&gt;",">", word)
    word = word.replace("&lt;", "<")
    word = word.replace("&gt;", ">")
    word = word.replace("&amp;", "&")
    return word

def contain_illegal_letter_in_word(word):
#    illegalLetters = [1 for letter in word if ord(letter) not in range(32, 127)]
    illegalLetters = [1 for letter in word if (ord(letter) < 32 or ord(letter) > 126)]

    if len(illegalLetters) > 0:
        return True
    return False

def contain_only_punc_in_word(word):
    if re.search("[a-zA-Z0-9]", word):
        return False
    return True

# version-20160512 
# allow $ appear in words ($cashtag in corpus)
def strip_nonLetter_in_word(word):
    if re.findall("[^a-zA-Z0-9$]", word): # contain some punctuations
        word = re.sub("^[^a-zA-Z0-9$]*","", word) # start with punc
        word = re.sub("[^a-zA-Z0-9$]*$","", word) # end with punc
    return word


def parseArgs(args):
    textFileName = getArg(args, "-text")
    if textFileName is None:
        sys.exit(0)
    outFileName = getArg(args, "-out")
    return textFileName, outFileName


#############################
if __name__ == "__main__":
    print "Usage: python preProcessTweetText.py -text tweetTextFileName_nonEng [-out tweetText.outFileName_clean]"
    print "Program starts at time:" + str(time.asctime())

    [textFileName, outFileName] = parseArgs(sys.argv)

    tweetTextCleaning_infile(textFileName, outFileName)

    print "Program ends at time:" + str(time.asctime())
