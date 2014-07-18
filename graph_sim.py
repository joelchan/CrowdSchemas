from nltk.corpus import wordnet as wn
import numpy as np
import itertools as it
import os, csv

class enhancedWord:
    def __init__(self, synset, level, weight):
        self.synset = synset
        self.level = level
        self.weight = weight
    def __str__(self):
        return self.synset.name + " with level " + str(self.level) + " and weight " + str(self.weight)

class rawWord:
    def __init__(self, label, posTag, weight):
        self.label = label
        self.pos = get_wordnet_pos(posTag)
        self.weight = weight
    def __str__(self):
        return self.label

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

	combos = [c for c in it.product(expandedWords1,expandedWords2)]
	for combo in combos:
		word1 = combo[0][0]
		weight1 = combo[0][1]
		word2 = combo[1][0]
		weight2 = combo[1][1]
		if word1.pos == word2.pos: # only try and find shortest paths between same POS
			# find shortest path between word, weight by height in hypernym hierarchy
			sim = word1.path_similarity(word2)
			#weight = 1.0/np.mean([word1[1],word2[1]])
			weight = 1.0/np.mean([weight1,weight2])
			if sim is not None:
				paths.append(sim*weight)
			else:
				paths.append(0)
	if len(paths):
		return paths
	else:
		return []

def expand_words(words):
	
	synonyms = set()
	for item in words:
		synsets = wn.synsets(item.label,item.pos)
		itemWeight = item.weight # divide weight among the synonyms? maybe item.weight/len(synsets)
		for synset in synsets:
			synonyms.add(enhancedWord(synset,1,itemWeight))

	# get derivationally related forms for "properties"
	derivations = set()
	for synonym in synonyms:
		if synonym[0].pos == 's':
			for lemma in synonym[0].lemmas:
				for form in lemma.derivationally_related_forms():
					derivations.add(enhancedWord(form.synset,1,synonym.weight))
	synonyms.update(derivations)

	# add to master
	expandedWords = set(synonyms)
	nextStack = set(synonyms)
	level = 2
	while(len(nextStack)):
	#while(level < 3):
		currentStack = set(nextStack)
		nextStack.clear()

		# get all hypernyms, put in nextStack
		for s in currentStack:
			for hypernym in s[0].hypernyms():
				nextStack.add(enhancedWord(hypernym,level,s.weight))
				expandedWords.add(enhancedWord(hypernym,level,s.weight))

		level += 1

	# return sorted(list(expandedWords),key=lambda x: x[1])
	return sorted(list(expandedWords),key=lambda x: x.level)

def sum_top(sims,n):
	"""
	sims is list of similarities
	"""
	topSims = sorted(sims,reverse=True)[:n]
	return sum(topSims)

def main():
	srcdir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_structure/"
	documents = []
	docNames = []
	for f in os.listdir(srcdir):
		fpath = srcdir + f
		if ".DS_Store" not in f and os.path.isfile(fpath):
			words = []
			for w in read_data(fpath):
				d = w.split(',')
				words.append((d[0].lower(),d[1]))
			documents.append(words)
			docNames.append(f)

	results = []
	combos = [x for x in it.combinations([i for i in xrange(len(documents))],2)]
	for combo in combos:
		doc1 = documents[combo[0]]
		doc2 = documents[combo[1]]
		docName1 = docNames[combo[0]]
		docName2 = docNames[combo[1]]
		print "Processing %s vs %s..." %(docName1,docName2)
		# sim = np.mean(find_paths(doc1,doc2))
		sim = sum_top(find_paths(doc1,doc2),10) # sum of top 10 path similarities
		results.append([docName1,docName2,sim,doc1,doc2])
	# for i in xrange(len(documents)):
	# 	print "Processing %s..." %docNames[i]
	# 	for j in xrange(len(documents)):
	# 		if docNames[i] != docNames[j]: #skip self-comparisons
	# 			doc1 = documents[i]
	# 			doc2 = documents[j]
	# 			#sim = np.mean(find_paths(doc1,doc2))
	# 			sim = sum(find_paths(doc1,doc2))
	# 			results.append([docNames[i],docNames[j],sim,doc1,doc2])

	with open("/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/smallResults_structure_topSum.csv",'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(['doc1','doc2','sim','words1','words2'])
		for result in results:
			csvwriter.writerow(result)

if __name__ == '__main__':
	main()
