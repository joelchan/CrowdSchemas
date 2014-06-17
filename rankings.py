#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Joel Chan joelchan.me

"""
Module with functions for getting pair rankings by similarity.

"""

from gensim import corpora, models, similarities
from operator import itemgetter
import itertools as it
import numpy as np
import pandas as pd
import random, os

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

def pair_sims(texts,names,dim=len(texts)):
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
	lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=len(names)) #create the space

	# output the matrix V so we can use it to get pairwise cosines
	# https://github.com/piskvorky/gensim/wiki/Recipes-&-FAQ#q3-how-do-you-calculate-the-matrix-v-in-lsi-space
	# vMatrix = 

	# get all pairwise cosines into a list
	pairs = generate_pairs(names)
	pairsims = []
	for pair in pairs:
		pairsim = cosine(pair[0],pair[1],vMatrix)
		pairsims.append((pair[0],pair[1],pairsim))

	# spit out the pair-cosine list in reverse sorted order 
	# so we can just grab the top N
	# http://stackoverflow.com/questions/10695139/sort-a-list-of-tuples-by-2nd-item-integer-value
	return sorted(pairsims,key=itemgetter(2),reverse=True)

def naive_lsa_pairs(textdir,names):
	"""
	return top n most similar pairs of documents (ranked by lsa cosine)
	doesn't frequency screen for now
	"""
	texts = []
	for f in os.listdir(textdir):
    	if ".DS" not in f:
    		fpath = textdir + f
    		ftext = open(fpath).read().

    # get sim ranked pairs
    pairSims = pair_sims(texts)

    # print to file with a csv
    with open("naive_lsa_pairs.csv",'w') as csvfile:
    	resultwriter = csv.writer(csvfile, delimiter=' ',quotechar='|'):
    	resultwriter.writerow(["doc1","doc2","cosine"])
    	for pairSim in pairSims:
    		resultwriter.writerow([pairSim[0],pairSim[1],pairSim[2]])
    csvfile.close()

def naive_pos_lsa_pairs(structureDir,surfaceDir,structureNames,surfaceNames):
	"""
	return top n 
	"""
	
	# basically do naive_lsa_pairs up to pairSims separately
	# for structure and surface
	# and then somehow merge the pairs - perhaps use pandas?
	
	# print the data frame to file with a csv
    pairSims.to_csv("naive_pos_lsa_pairs.csv")