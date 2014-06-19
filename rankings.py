#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Joel Chan joelchan.me

"""
Module with functions for getting pair rankings by similarity.

"""

from gensim import corpora, models, similarities, matutils
from operator import itemgetter
import itertools as it
import numpy as np
import pandas as pd
import random, os, csv, sys

def cosine(doc1, doc2, doc_topic_weights):
    weights1 = doc_topic_weights[doc1]
    weights2 = doc_topic_weights[doc2]
    dotProduct = np.dot(weights1,weights2)
    mag1 = np.sqrt(sum([np.square(weight) for weight in weights1]))
    mag2 = np.sqrt(sum([np.square(weight) for weight in weights2]))
    return dotProduct/(mag1*mag2)

def generate_pairs(names):
	"""
	get all pairs of documents
	"""
	return [p for p in it.combinations(names,2)] 

def extract_text(textdir):
	texts = []
	names = []
	for f in os.listdir(textdir):
		if ".DS" not in f:
			names.append(f.split("_")[0])
			fpath = textdir + f
			ftext = open(fpath).read().split()
			texts.append(ftext)
	return texts, names

def random_pairs(names,n=50):
	"""
	return n randomly selected pairs of documents

	params:
	@n how many pairs we want
	@names list of document names
	"""
	pairs = generate_pairs(names)
	random.shuffle(pairs)
	output = []
	for i in xrange(n):
		output.append(pairs[i])
	return output

def pair_sims(texts,names,dim,rawTexts):
	"""
	from list of texts, return list of pairs with pairwise cosines for each pair
	"""
	# prepare dictionary
	dictionary = corpora.Dictionary(texts)

	# convert tokenized documents to a corpus of vectors
	corpus = [dictionary.doc2bow(text) for text in texts]

	# convert raw vectors to tfidf vectors
	tfidf = models.TfidfModel(corpus) #initialize model
	corpus_tfidf = tfidf[corpus] #apply tfidf model to whole corpus

	# make lsa space, use max dimensions for now
	lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=dim) #create the space

	# output the matrix V so we can use it to get pairwise cosines
	# https://github.com/piskvorky/gensim/wiki/Recipes-&-FAQ#q3-how-do-you-calculate-the-matrix-v-in-lsi-space
	vMatrix = matutils.corpus2dense(lsi[corpus_tfidf],len(lsi.projection.s)).T / lsi.projection.s

	# get all pairwise cosines into a list
	indices = [i for i in xrange(len(names))]
	pairs = generate_pairs(indices)
	pairsims = []
	counter = 0
	for pair in pairs:
		name1 = names[pair[0]]
		name2 = names[pair[1]]
		text1 = rawTexts[name1]
		text2 = rawTexts[name2]
		sim = cosine(pair[0],pair[1],vMatrix)
		pairsims.append([name1, 
						 name2, 
						 text1,
						 text2,
						 sim])
		counter += 1
		sys.stdout.write("\tProcessed %i of %i pairs...\r" %(counter, len(pairs)))
        sys.stdout.flush()
	sys.stdout.write("\tProcessed %i of %i pairs...\n" %(counter, len(pairs)))

	# spit out the pair-cosine list in reverse sorted order 
	# so we can just grab the top N
	# http://stackoverflow.com/questions/10695139/sort-a-list-of-tuples-by-2nd-item-integer-value
	return sorted(pairsims,key=itemgetter(2),reverse=True)

def naive_lsa_pairs(textDir,rawTexts):
	"""
	return top n most similar pairs of documents (ranked by lsa cosine)
	doesn't frequency screen for now
	"""
	
	# extract text and names
	texts, names = extract_text(textDir)

	# get sim ranked pairs
	pairsims = pair_sims(texts,names,300,rawTexts)
	pairsimsDF = pd.DataFrame(pairsims,columns=["doc1","doc2","doc1text","doc2text","cosine"])
	#make sure it's sorted!
	pairsimsDF = pairsimsDF.sort("cosine",ascending=False)
	toppairsimsDF = pairsimsDF[:50]

	# print to file with a csv
	pairsimsDF.to_csv("naive_lsa_pairs.csv")
	toppairsimsDF.to_csv("naive_lsa_pairs_top50.csv")

def naive_pos_lsa_pairs(structureDir,surfaceDir,rawTexts):
	"""
	return top n 
	"""
	
	# structure
	structureTexts, structureNames = extract_text(structureDir)
	print "Processing structure pairings..."
	pairsims = pair_sims(structureTexts,structureNames,300,rawTexts)
	structurePairs = pd.DataFrame(pairsims, columns=["doc1","doc2","doc1text","doc2text","structureCosine"])
	structurePairs['pair'] = structurePairs.doc1 + "_" + structurePairs.doc2

	# surface
	surfaceTexts, surfaceNames = extract_text(surfaceDir)
	print "Processing surface pairings..."
	pairsims = pair_sims(surfaceTexts,surfaceNames,300,rawTexts)
	surfacePairs = pd.DataFrame(pairsims, columns=["doc1","doc2","doc1text","doc2text","surfaceCosine"])
	surfacePairs['pair'] = surfacePairs.doc1 + "_" + surfacePairs.doc2

	# merge them and print them out
	mergedPairs = pd.merge(surfacePairs,structurePairs,on="pair")
	mergedPairs['d'] = mergedPairs.structureCosine - mergedPairs.surfaceCosine
	mergedPairs = mergedPairs.sort('d',ascending=False)
	topMergedPairs = mergedPairs[:50]
	mergedPairs.to_csv("naive_pos_lsa_pairs.csv")
	topMergedPairs.to_csv("naive_pos_lsa_pairs_top50.csv")

def main():
	rawDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaRawText/"
	allDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_All/"
	structureDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_Verbs/"
	surfaceDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_Nouns/"
	rawTexts = {}
	for f in os.listdir(rawDir):
		if ".DS" not in f:
			fname = f.replace(".txt","")
			fpath = rawDir + f
			ftext = open(fpath).read()
			rawTexts[fname] = ftext
	naive_lsa_pairs(allDir,rawTexts)
	# naive_pos_lsa_pairs(structureDir,surfaceDir,rawTexts)

if __name__ == '__main__':
	main()
