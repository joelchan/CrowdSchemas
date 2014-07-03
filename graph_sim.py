from nltk.corpus import wordnet as wn
import numpy as np
import os, csv

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

def get_wordnet_pos(treebank_tag):
	"""
	helper method to convert treebank tags
	into wordnet pos tags for query expansion
	"""
	if treebank_tag.startswith('J'):
		return wn.ADJ
	elif treebank_tag.startswith('V'):
		return wn.VERB
	elif treebank_tag.startswith('N'):
		return wn.NOUN
	elif treebank_tag.startswith('R'):
		return wn.ADV
	else:
		return ''

def find_paths(words1,words2):
	paths = []

	# first expand with synonyms
	expandedWords1 = expand_words(words1)
	expandedWords2 = expand_words(words2)

	for word1 in expandedWords1:
		for word2 in expandedWords2:
			# find shortest path between word, weight by height in hypernym hierarchy
			sim = word1[0].path_similarity(word2[0])
			weight = 1.0/np.mean([word1[1],word2[1]])
			if sim is not None:
				paths.append(sim*weight)
			else:
				paths.append(0)
	if len(paths):
		return paths
	else:
		return [0.0]

def expand_words(words):
	
	synonyms = set()
	for item in words:
		synsets = wn.synsets(item[0],get_wordnet_pos(item[1]))
		for synset in synsets:
			synonyms.add((synset,1))

	# get derivationally related forms for "properties"
	derivations = set()
	for synonym in synonyms:
		if synonym[0].pos == 's':
			for lemma in synonym[0].lemmas:
				for form in lemma.derivationally_related_forms():
					derivations.add((form.synset,1))
	synonyms.update(derivations)

	# add to master
	expandedWords = set(synonyms)
	nextStack = set(synonyms)
	level = 2
	# while(len(nextStack)):
	while(level < 3):
		currentStack = set(nextStack)
		nextStack.clear()

		# get all hypernyms, put in nextStack
		for s in currentStack:
			for hypernym in s[0].hypernyms():
				nextStack.add((hypernym,level))
				expandedWords.add((hypernym,level))

		level += 1

	return sorted(list(expandedWords),key=lambda x: x[1])

def main():
	srcdir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small/"
	documents = []
	for f in os.listdir(srcdir):
		fpath = srcdir + f
		words = []
		for w in read_data(fpath):
			d = w.split(',')
			words.append((d[0],d[1]))
		documents.append(words)

	results = []
	for i in xrange(len(documents)):
		for j in xrange(len(documents)):
			doc1 = documents[i]
			doc2 = documents[j]
			sim = np.mean(find_paths(doc1,doc2))	
			results.append([doc1,doc2,sim])

	with open("/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/smallResults.csv",'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(['doc1','doc2','sim'])
		for result in results:
			csvwriter.writerow(result)

if __name__ == '__main__':
	main()