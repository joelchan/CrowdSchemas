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

def pair_sims(texts,names,dim):
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
	for pair in pairs[:100]:
		pairsims.append([names[pair[0]], 
						 names[pair[1]], 
						 cosine(pair[0],pair[1],vMatrix)])
		counter += 1
		sys.stdout.write("\tProcessed %i of %i pairs...\r" %(counter, len(pairs[:100])))
        sys.stdout.flush()
	sys.stdout.write("\tProcessed %i of %i pairs...\n" %(counter, len(pairs[:100])))

	# spit out the pair-cosine list in reverse sorted order 
	# so we can just grab the top N
	# http://stackoverflow.com/questions/10695139/sort-a-list-of-tuples-by-2nd-item-integer-value
	return sorted(pairsims,key=itemgetter(2),reverse=True)

def naive_lsa_pairs(textdir):
	"""
	return top n most similar pairs of documents (ranked by lsa cosine)
	doesn't frequency screen for now
	"""
	
	# extract text and names
	texts, names = extract_text(textdir)

	# get sim ranked pairs
	pairsims = pair_sims(texts,names,300)

	# print to file with a csv
	with open("naive_lsa_pairs.csv",'w') as csvfile:
		resultwriter = csv.writer(csvfile, delimiter=',',quotechar='|')
		resultwriter.writerow(["doc1","doc2","cosine"])
		for pairSim in pairsims:
			resultwriter.writerow([pairSim[0],pairSim[1],pairSim[2]])
	csvfile.close()

def naive_pos_lsa_pairs(structureDir,surfaceDir):
	"""
	return top n 
	"""
	
	# structure
	structureTexts, structureNames = extract_text(structureDir)
	print "Processing structure pairings..."
	pairsims = pair_sims(structureTexts,structureNames,300)
	structurePairs = pd.DataFrame(pairsims, columns=["doc1","doc2","structureCosine"])
	structurePairs['pair'] = structurePairs.doc1 + "_" + structurePairs.doc2

	# surface
	surfaceTexts, surfaceNames = extract_text(surfaceDir)
	print "Processing surface pairings..."
	pairsims = pair_sims(surfaceTexts,surfaceNames,300)
	surfacePairs = pd.DataFrame(pairsims, columns=["doc1","doc2","surfaceCosine"])
	surfacePairs['pair'] = surfacePairs.doc1 + "_" + surfacePairs.doc2

	# merge them and print them out
	mergedPairs = pd.merge(surfacePairs,structurePairs,on="pair")
	mergedPairs.to_csv("naive_pos_lsa_pairs.csv")

def main():
	allDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_All/"
	structureDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_Verbs/"
	surfaceDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaProcessedText_Nouns/"
	# naive_lsa_pairs(textdir)
	naive_pos_lsa_pairs(structureDir,surfaceDir)

if __name__ == '__main__':
	main()
