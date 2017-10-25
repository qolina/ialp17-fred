import re
import sys

sys.path.append("/home/yxqin/Scripts")
from hashOperation import *
from strOperation import *


def getVerbs(tagStr, arr):
    verbIdx = {}
    debug = False
    if debug:
        print " ".join(arr)
        print tagStr
    verbIdx = get_verb_rel_by_pattern(tagStr, arr, verbIdx, SHORT_RELATION_PATTERN)
    verbIdx = get_verb_rel_by_pattern(tagStr, arr, verbIdx, LONG_RELATION_PATTERN)
    return verbIdx


def get_verb_rel_by_pattern(tagStr, arr, verbIdx, pattern):
    debug = False
    i = 0
#    print "###PATTERN: " + pattern
    #print re.findall(r"(%s)"%pattern, tagStr)
    for match in re.finditer(r"(%s)"%pattern, tagStr):
        stIdx = match.span()[0]
        edIdx = match.span()[1]
        st = 0
        if stIdx != 0:
            befArr = tagStr[:stIdx].strip().split(" ")
            st = len(befArr)
        ed = st+len(tagStr[stIdx:edIdx].strip().split(" "))-1

        # old version before 20150201, could not iterates all matches
#        befStr = tagStr[0:tagStr.find(match[0])].strip()
#        befArr = befStr.split(" ")
#        st = len(befArr)
#        ed = st+len(match[0].strip().split(" "))-1

        # print for debug
        if debug:
            print "match" + str(i) + ", matchedStr: ",
            print match.groups(), match.span(),
            print [st, ed],
            print "verbRel :" + str(arr[st:ed+1])

        # store into verbIdx
        if st not in verbIdx: # keep longes match
            verbIdx[st] = ed
        elif verbIdx[st] >= ed:
            continue
        elif verbIdx[st] < ed:
            verbIdx[st] = ed
        i += 1
    return verbIdx

def relation_of_two_index(idx1, idx2):
    (st1, ed1) = idx1
    (st2, ed2) = idx2
    if ed2+1 < st1:
        return "left"
    if ed2+1 == st1:
        return "left adjacent"
    if st2 > ed1+1:
        return "right"
    if st2 == ed1+1:
        return "right adjacent"
    if st2 <= st1 <= ed1 <= ed2:
        return "cover"
    if st1 < st2 <= ed2 <= ed1:
        return "insider"
    if st2 < st1 <= ed2 < ed1:
        return "left intersaction"
    if st1 < st2 <= ed1 < ed2:
        return "right intersaction"
    return str(idx1) + str(idx2)

## merge adjacent verb rels
def mergeAdj(verbIdx):
    newIdx = {}
    if len(verbIdx) == 0:
        return {}
    sts = sorted(verbIdx.keys())
    newIdx[sts[0]] = verbIdx[sts[0]]
    #print newIdx
    pst = sts[0] # previous start idx in newIdx
    for i in range(1, len(sts)):
        st = sts[i]
#        print "###", relation_of_two_index((pst, newIdx[pst]), (st, verbIdx[st])), (pst, newIdx[pst]), (st, verbIdx[st]) 
        if st <= newIdx[pst]:
#            print "st2 < ed1:", (st, verbIdx[st]), (pst, newIdx[pst])
#        elif st == newIdx[pst]:
            if newIdx[pst] < verbIdx[st]:
                newIdx[pst] = verbIdx[st]
        else:
            newIdx[st] = verbIdx[st]
            pst = st
        #print newIdx
    return newIdx


global VERB, WORD, PREP
global SHORT_RELATION_PATTERN, LONG_RELATION_PATTERN
# verb is composed of 
#// 1) Optional adverb
#// 2) Modal or other verbs
#// 3) Optional particle/adverb

# v1 with / in pennTag
VERB = r"(/RB )?" + r"(/MD |/VB |/VBD |/VBP |/VBZ |/VBG |/VBN )" + r"(/RP )?(/RB )?"
WORD = r"(/$ |/PRP$ |/CD |/DT |/JJ |/JJS |/JJR |/NN |" + r"/NNS |/NNP |/NNPS |/POS |/PRP |/RB |/RBR |/RBS |" + r"/VBN |/VBG )" # complete version
#WORD = r"(/$ |/PRP$ |/CD |/DT |/JJ |/JJS |/JJR |/NN |" + r"/NNS |/NNP |/NNPS |/POS |/PRP |/RB |/RBR |/RBS )" # no V in WORD
#WORD = r"(/$ |/PRP$ |/CD |/DT |/JJ |/JJS |/JJR |/NN |" + r"/NNS |/NNP |/NNPS |/POS |/PRP |/RB |/RBR |/RBS |" + r"/VBN |/VBG |/VB |/VBD |/VBP |/VBZ |/MD )" # added VB/VBD/VBP/VBZ/MD in WORD
PREP = r"(/RB )?(/IN |/TO |/RP )(/RB )?"

# v2 without /
#VERB = r"(RB )?" + r"(MD |VB |VBD |VBP |VBZ |VBG |VBN )" + r"(RP )?(RB )?"
#WORD = r"($ |PRP\$ |CD |DT |JJ |JJS |JJR |NN |" + r"NNS |NNP |NNPS |POS |PRP |RB |RBR |RBS |" + r"VBN |VBG )" # complete version
##WORD = r"($ |PRP\$ |CD |DT |JJ |JJS |JJR |NN |" + r"NNS |NNP |NNPS |POS |PRP |RB |RBR |RBS )" # no V in WORD
#PREP = r"(RB )?(IN |TO |RP )(RB )?"

# v3 with Twitter specific tag set
# $ in WORD is ignored, # ignore G(POS) in WORD
#VERB = r"(R )?" + r"(V |L |M |Y )" + r"(T )?(R )?"
#WORD = r"(D |\$ |A |N |\^ |O |R |Z |S )" # 1) ignore VBN/VBG in WORD 
##WORD = r"(D |\$ |A |N |\^ |G |O |R " + r"|VBN |VBG )" # 2) identify VBN/VBG from Vs
#PREP = r"(R )?(P |T )(R )?"


#The pattern (V(W*P)?)+
LONG_RELATION_PATTERN_str = "({0} ({1}* ({2})+)?)+".format('VERB', 'WORD', 'PREP')
#The pattern (VP?)+
SHORT_RELATION_PATTERN_str = "({0} ({1})?)+".format('VERB', 'PREP')
#print "###LONG_RELATION_PATTERN: " + LONG_RELATION_PATTERN_str
#print "###SHORT_RELATION_PATTERN: " + SHORT_RELATION_PATTERN_str

# VP+ version
LONG_RELATION_PATTERN = "({0}(({1})*({2})+)?)+".format(VERB, WORD, PREP)
SHORT_RELATION_PATTERN = "({0}({1})?)+".format(VERB, PREP)
# VP version, which can saparate V|VP|VWP
#LONG_RELATION_PATTERN = "({0}(({1})*({2})+)?)".format(VERB, WORD, PREP)
#SHORT_RELATION_PATTERN = "({0}({1})?)".format(VERB, PREP)


def tagStr_for_verbRel_extract(tagArr):
    tagStr = " ".join(tagArr) + " "
    return tagStr


if __name__ == "__main__":
    # test case
#    textStr = "Everyone/NN who/WP played/VBD Elite/NNP or/CC Frontier/NNP many/JJ years/NNS ago/IN (or/NN ask/VB your/PRP$ parents/NNS help/VBP funding/VBG \"Elite:Dangerous\"/NNP !/."
#    textStr = "has/VBZ stopped/VBN by/RP a/DT workout/NN of/IN g/NNS"
    textStr = "has/V stopped/VBN by/R a/D workout/N of/P g/N"
    arr = textStr.split(" ")
    [wordArr, tagArr] = splitWordTag(textStr)
    print " ".join([item+"_"+str(arr.index(item)) for item in arr])
    print LONG_RELATION_PATTERN

    tagStr = tagStr_for_verbRel_extract(tagArr)
    print "TagStr: " + tagStr, "#end"

    # get verbs
    verbIdx = getVerbs(tagStr, arr)
    print verbIdx
    ## merge adjacent verb rels
    newIdx = mergeAdj(verbIdx)
    print newIdx
