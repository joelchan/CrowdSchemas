import nltk, os

def read_data(filename):
	"""
	Read in data from a file and return a list with each element being one line from the file.
	Parameters:
	1) filename: name of file to be read from
	Note: the code now opens as a binary and replaces carriage return characters with newlines because python's read and readline functions don't play well with carriage returns.
	However, this will no longer be an issue with python 3.
	"""	
	with open(filename, "rb") as f:
		s = f.read().replace('\r\n', '\n').replace('\r', '\n')
		data = s.split('\n')
	return data

def remove_urls(words):
	newwords = []
	for word in words:
		if word.count("-") < 3 and word.count('.') < 2 and word.count('/') < 2 and not '.com' in word and not '.pdf' in word:
			newwords.append(word)
	return newwords

def remove_punctuation_only(words):
	newwords = []
	for word in words:
		if any(c.isalpha() for c in word):
			newwords.append(word)
	return newwords

def remove_trailing_punctuation(words):
	#newwords = []
	#for word in words:
	#	if word[-1] == '.' or word[-1] == '?' or word[-1] == '!':
	#		newwords.append(word[:-1])
	#	else:
	#		newwords.append(word)
	#return newwords

    newwords = []
    for word in words:
        punct = True
        while punct:
            if word[-1].isalpha():
                punct = False
                newwords.append(word)
            else:
                word = word[:-1]
    return newwords

def remove_leading_punctuation(words):
	newwords = []
	for word in words:
		if len(word):
			# print word
			punct = True
			while punct:
				if word[0].isalpha():
					punct = False
					newwords.append(word)
				else:
					word = word[1:]
	return newwords

def split_slashes_and_periods(words):
	newwords = []
	for word in words:
		if '/' in word:
			temp = word.split('/')
			for t in temp:
				newwords.append(t)
		elif '.' in word:
			temp = word.split('.')
			for t in temp:
				newwords.append(t)
		else:
			newwords.append(word)
	return newwords

def main(srcdir= "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaRawText/", 
		verbsdir="/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_Verbs/", 
		nounsdir="/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_Nouns/", 
		alldir="/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_All/"):
	
	stopWords = read_data("englishstopwords-jc.txt")

	# for text in folder
	for f in os.listdir(srcdir):
		if ".DS_Store" not in f:
			# read in text
			fpath = srcdir + f
			text = open(fpath).read()
			# split into sentences (PunktSentenceTokenizer)
			sentences = nltk.sent_tokenize(text)
			# tokenize words (TreeBank)
			tokens = []
			for sentence in sentences:
				tokens += [token for token in nltk.word_tokenize(sentence)]

			# strip out stop words, other preprocessing
			tokens = [t.lower() for t in tokens if t.lower() not in stopWords]
			tokens = remove_urls(tokens)
			tokens = remove_punctuation_only(tokens)
			tokens = remove_leading_punctuation(tokens)
			tokens = remove_trailing_punctuation(tokens)
			# POS tag (Penn TreeBank) - lemmatize first???
			# wnl = nltk.WordNetLemmatizer()
			# lemmas = [wnl.lemmatize(t) for t in tokens]
			tokens_tagged = nltk.pos_tag(tokens)
			# collect nouns and verbs
			verbs = []
			nouns = []
			others = []
			allTokens = []
			for token in tokens_tagged:
				allTokens.append(token[0])
				if token[1].startswith('V'):
					verbs.append(token[0])
				elif token[1].startswith('N'):
					nouns.append(token[0])
				else:
					others.append(token)
			# "enrich" with hypernyms
			
			# dump into folders
			verbsout = verbsdir + f.replace(".txt","_verbs.txt")
			verbswrite = open(verbsout,'w')
			verbswrite.write(' '.join(verbs))

			nounsout = nounsdir + f.replace(".txt","_nouns.txt")
			nounswrite = open(nounsout,'w')
			nounswrite.write(' '.join(nouns))

			allout = alldir + f.replace(".txt","_all.txt")
			allwrite = open(allout,'w')
			allwrite.write(' '.join(allTokens))

if __name__ == '__main__':
	main()

	# verb_lemmas = []
	# noun_lemmas = []
	# other_lemmas = []
	# for token in lemmas_tagged:
	# 	if token[1].startswith('V'):
	# 		verb_lemmas.append(token[0])
	# 	elif token[1].startswith('N'):
	# 		noun_lemmas.append(token[0])
	# 	else:
	# 		other_lemmas.append(token)

