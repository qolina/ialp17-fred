import sys


sys.path.append("/home/yxqin/Scripts")
import langid

def isLine_inEng(line):
    lang = langid.classify(line)
    lang = lang[0]
    if lang == "en":
        return True
    return False

def get_engLines_from_file(filename):
    datafile = file(filename)
    content = datafile.readlines()
    for line in content:
        line = line[:-1]
        if isLine_inEng(line):
            print line

    datafile.close()


if __name__ == "__main__":
#    if len(sys.argv) != 2:
#        print "usage: python lang.py inputfilename (> outfilename) \n func: filter out non-Eng line."
#        sys.exit(0)

#    get_engLines_from_file(sys.argv[1])
    line = "I am an english text."
    print line, "eng:", isLine_inEng(line)

