import sys

pTag2rTag = {"NN":"N", "NNS":"N", 
"PRP":"O", "WP":"O", 
#"":"S", 
"NNP":"^", "NNPS":"^", 
#"":"Z", 
#"":"L", 
#"":"M", 

"MD":"V", "VB":"V", "VBD":"V", "VBG":"V", "VBN":"V", "VBP":"V", "VBZ":"V", 
"JJ":"A", "JJR":"A", "JJS":"A", 
"WRB":"R", "RB":"R", "RBR":"R", "RBS":"R", "RP":"R", 
"UH":"!",

"WDT":"D", "DT":"D", "WP$":"D", "PRP$":"D", 
"IN":"P", "TO":"P", 
"CC":"&", 
"RP":"T", 
"EX":"X", "PDT":"X", 
#"":"Y", 

"#":"#",
"USR":"@",
"RT":"~",
"URL":"U",
#"":"E",

"CD":"$", 
"#":",", "$":",", ".":",", ",":",", ":":",", "''":",", "``":",", "-LRB-":",", "-RRB-":",", "(":",", ")":",", 
"FW":"G", "POS":"G", "SYM":"G", "LS":"G"
} 

def pos2TwiTag(penTag):
	if penTag in pTag2rTag:
		return pTag2rTag[penTag]
	else:
		return None


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage: python regular2ritter.py inputfilename"
		sys.exit(0)

	datafile = file(sys.argv[1])

	existedTags = {}
	unmapped = {}
	while 1:
		lineStr = datafile.readline()
		if not lineStr:
			break
		wordsWithTags = lineStr[:-1].split(" ")
		words = [w[:w.rfind("/")] for w in wordsWithTags]
		tags = [w[w.rfind("/")+1:] for w in wordsWithTags]
		wordCount = len(words)
		wordsWithRTags = []
		for idx in range(wordCount):
			if tags[idx] in existedTags:
				existedTags[tags[idx]] += 1
			else:
				existedTags[tags[idx]] = 1

			newTag = pos2TwiTag(tags[idx])
			if newTag is None:
				#unmapped[newTag] = wordsWithRTags[idx]
				unmapped[tags[idx]] = words[idx]
				wordsWithRTags.append(words[idx]+"/"+tags[idx])
			else:
				wordsWithRTags.append(words[idx]+"/"+newTag)
		
		print " ".join(wordsWithRTags)

	print sorted(existedTags.items(), key = lambda a:a[0], reverse = True)
	print sorted(unmapped.items(), key = lambda a:a[0], reverse = True)
