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

class pathSim:
	def __init__(self, pair, path, scoreRaw, scoreWeighted):
		self.pair = str(pair)
		self.path = str(path)
		self.scoreRaw = scoreRaw
		self.pathLength = int(1/scoreRaw)
		self.scoreWeighted = scoreWeighted
	def __str__(self):
		return "Path is FROM %s\nRaw path length: %i\nWeighted path similarity: %.2f" %(self.path, self.pathLength, self.scoreWeighted)

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

def find_paths(words1,words2,name1,name2):
    """
    words1 and words2 are lists of rawWords
    """
    paths = []
    
    # first expand with synonyms
    expandedWords1 = expand_words(words1)
    expandedWords2 = expand_words(words2)
    
    combos = [c for c in it.product(expandedWords1,expandedWords2)]
    for combo in combos:
        word1 = combo[0]
        word2 = combo[1]
        if word1.synset.pos == word2.synset.pos: # only try and find shortest paths between same POS
            # find shortest path between word, weight by height in hypernym hierarchy
            simRaw = word1.synset.path_similarity(word2.synset)
            levelWeight = 1.0/np.mean([word1.level, word2.level])
            weight = np.mean([word1.weight, word2.weight])
            if simRaw is not None:
                simWeighted = simRaw*levelWeight*weight
                path = "%s TO %s" %(word1.synset.name, word2.synset.name)
                pair = "%s VS %s" %(name1, name2)
                # paths.append(((word1.synset.name,word2.synset.name),sim*weight*levelWeight))
                paths.append(pathSim(pair,path,simRaw,simWeighted))
            #else:
            #    paths.append(0)
    if len(paths):
        return sorted(paths, key=lambda x: x.scoreWeighted, reverse=True)
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
		if synonym.synset.pos == 's':
			for lemma in synonym.synset.lemmas:
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
			for hypernym in s.synset.hypernyms():
				nextStack.add(enhancedWord(hypernym,level,s.weight))
				expandedWords.add(enhancedWord(hypernym,level,s.weight))

		level += 1

	# return sorted(list(expandedWords),key=lambda x: x[1])
	return sorted(list(expandedWords),key=lambda x: x.level)

def sum_top(sims,n):
    """
    sims is list of similarities
    """
    top = sorted(sims,key=lambda x: x.scoreWeighted, reverse=True)[:n]
    topSims = [t.scoreWeighted for t in top]
    return sum(topSims)

def main():
	srcdir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_structure_subset/"
	documents = []
	docNames = []
	for f in os.listdir(srcdir):
		fpath = srcdir + f
		if ".DS_Store" not in f and os.path.isfile(fpath):
			words = []
			for w in read_data(fpath):
				d = w.split(',')
				# words.append((d[0].lower(),d[1]))
				print d
				words.append(rawWord(d[0].lower(),d[1],float(d[2])))
			documents.append(words)
			docNames.append(f)

	results = []
	pathsToWrite = []
	combos = [x for x in it.combinations([i for i in xrange(len(documents))],2)]
	for combo in combos:
		doc1 = documents[combo[0]]
		doc2 = documents[combo[1]]
		docName1 = docNames[combo[0]]
		docName2 = docNames[combo[1]]
		print "Processing %s vs %s..." %(docName1,docName2)
		comboPath = find_paths(doc1,doc2,docName1,docName2)
		doc1Words = [d.label for d in doc1]
		doc2Words = [d.label for d in doc2]
		sim = sum_top(comboPath,10) # sum of top 10 path similarities
		results.append([docName1,docName2,sim,doc1Words,doc2Words])
		for combo in sorted(comboPath,key=lambda x: x.scoreWeighted, reverse=True)[:10]:
			pathsToWrite.append([combo.pair,combo.path,combo.scoreRaw,combo.pathLength,combo.scoreWeighted])

	with open("/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/smallResults_structureSubSet_topSum.csv",'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(['doc1','doc2','sim','words1','words2'])
		for result in results:
			csvwriter.writerow(result)

	with open("/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/smallResults_structureSubSet_topSum_PATHS.csv",'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(['pair','path','rawSim','pathLength','weightedSim'])
		for path in pathsToWrite:
			csvwriter.writerow(path)

if __name__ == '__main__':
	main()
