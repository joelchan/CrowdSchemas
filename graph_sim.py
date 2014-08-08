from nltk.corpus import wordnet as wn
from copy import deepcopy
from operator import mul
import numpy as np
import itertools as it
import pandas as pd
from pandas import ExcelWriter
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
        self.expansions = []
    def __str__(self):
        return self.label

class pathSim:
    def __init__(self, docPair, wordPair, path, scoreRaw, scoreWeighted):
        self.docPair = str(docPair)
        self.wordPair = str(wordPair)
        self.path = str(path)
        self.scoreRaw = scoreRaw
        self.pathLength = int(1/scoreRaw)
        self.scoreWeighted = scoreWeighted
    def __str__(self):
        return "Wordpair: %s\nPath is FROM %s\nRaw path length: %i\nWeighted path similarity: %.2f" %(self.pair, self.path, self.pathLength, self.scoreWeighted)

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

def find_paths(words1,words2,docName1,docName2):
    """
    words1 and words2 are lists of rawWords
    """
    
    docPair = "%s TO %s" %(docName1, docName2)

    paths = []
    
    # first expand with synonyms
    words1 = expand_words(words1)
    words2 = expand_words(words2)
    
    wordCombos = [c for c in it.product(words1,words2)]
    for wordCombo in wordCombos:
        pair = "%s to %s" %(wordCombo[0].label, wordCombo[1].label)
        pathCombos = [c for c in it.product(wordCombo[0].expansions, wordCombo[1].expansions)]
        # maxSim = max_sim(pathCombos)
        champion = pathSim(docPair,pair,"null",0.1,0.0)
        for pathCombo in pathCombos:
            word1 = pathCombo[0]
            word2 = pathCombo[1]
            if word1.synset.pos == word2.synset.pos: # only try and find shortest paths between same POS
                # find shortest path between word, weight by height in hypernym hierarchy
                simRaw = word1.synset.path_similarity(word2.synset)
                levelWeight = 1.0/np.mean([word1.level, word2.level])
                weight = np.mean([word1.weight, word2.weight])
                if simRaw is not None:    
                    simWeighted = simRaw*levelWeight*weight
                    path = "%s TO %s" %(word1.synset.name, word2.synset.name)
                    pathsim = pathSim(docPair,pair,path,simRaw,simWeighted)
                    if pathsim.scoreWeighted > champion.scoreWeighted:
                        champion = deepcopy(pathsim)
        paths.append(champion)
    if len(paths):
        return sorted(paths, key=lambda x: x.scoreWeighted, reverse=True)
    else:
            return []

def max_sim(combos):
    possibleLinks = []
    for c in combos:
        c1 = c[0]
        c2 = c[1]
        if c1.synset.pos == c2.synset.pos:
            levelWeight = 1.0/np.mean([word1.level, word2.level])
            weight = np.mean([word1.weight, word2.weight])



def expand_words(words):
    for item in words:
        synonyms = set()
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
            currentStack = set(nextStack)
            nextStack.clear()
                        
            # get all hypernyms, put in nextStack
            for s in currentStack:
                for hypernym in s.synset.hypernyms():
                    nextStack.add(enhancedWord(hypernym,level,s.weight))
                    expandedWords.add(enhancedWord(hypernym,level,s.weight))
            level += 1
                
        item.expansions = sorted(list(expandedWords),key=lambda x: x.level)
    return words

def sum_top(sims,n):
    """
    sims is list of similarities
    """
    top = sorted(sims,key=lambda x: x.scoreWeighted, reverse=True)[:n]
    topSims = [t.scoreWeighted for t in top]
    return sum(topSims)

def process_sim(srcdir,n,simType):
    # settings = read_data(settingsFile)
    # srcdir = settings[0]
    documents = []
    docNames = []
    for f in os.listdir(srcdir):
        fpath = srcdir + f
        if ".DS_Store" not in f and os.path.isfile(fpath):
            words = []
            for w in read_data(fpath):
                d = w.split(',')
                # words.append((d[0].lower(),d[1]))
                # print d
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
        p = "%s TO %s" %(docName1, docName2)
        print "Processing %s vs %s..." %(docName1,docName2)
        comboPath = find_paths(doc1,doc2,docName1,docName2)
        doc1Words = [d.label for d in doc1]
        doc2Words = [d.label for d in doc2]
        sim = sum_top(comboPath,n) # sum of top n path similarities
        results.append([docName1,docName2,p,sim,doc1Words,doc2Words])
        for combo in sorted(comboPath,key=lambda x: x.scoreWeighted, reverse=True)[:n]:
            pathsToWrite.append([combo.docPair,combo.wordPair,combo.path,combo.scoreRaw,combo.pathLength,combo.scoreWeighted])

    simsColNames = ['doc1','doc2','docPair','sim','words1','words2']
    for i in xrange(3,len(simsColNames)):
        simsColNames[i] = simType + "_" + simsColNames[i]
    pathsColNames = ['docPair','wordPair','path','rawSim','pathLength','weightedSim']
    for i in xrange(2,len(pathsColNames)):
        pathsColNames[i] = simType + "_" + pathsColNames[i]
    simsDF = pd.DataFrame(results,columns=simsColNames)
    pathsDF = pd.DataFrame(pathsToWrite,columns=pathsColNames)

    return simsDF, pathsDF
    # with open(settings[1],'w') as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     csvwriter.writerow(['doc1','doc2','docPair','sim','words1','words2'])
    #     for result in results:
    #         csvwriter.writerow(result)

    # with open(settings[2],'w') as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     csvwriter.writerow(['docPair','wordPair','path','rawSim','pathLength','weightedSim'])
    #     for path in pathsToWrite:
    #         csvwriter.writerow(path)

def main(n):
    
    # settings
    structureSrcDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_structure_enhanced/"
    surfaceSrcDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_surface/"
    simOutFileName = "smallResults_WT_en_topSum_%i.csv" %n
    pathOutFileName = "smallResults_WT_en_topSum_%i_PATH.csv" %n

    # get data
    structureSimDF, structurePathsDF = process_sim(structureSrcDir,n,"structure")
    surfaceSimDF, surfacePathsDF = process_sim(surfaceSrcDir,n,"surface")
    
    # merge the data
    masterSimsDF = pd.DataFrame.merge(structureSimDF,surfaceSimDF,how="left")
    masterPathsDF = pd.DataFrame.merge(structurePathsDF,surfacePathsDF,how="left")
    masterSimsDF['structure_sim_z'] = (masterSimsDF.structure_sim-np.mean(masterSimsDF.structure_sim))/np.std(masterSimsDF.structure_sim)
    masterSimsDF['surface_sim_z'] = (masterSimsDF.surface_sim-np.mean(masterSimsDF.surface_sim))/np.std(masterSimsDF.surface_sim)

    # print out
    masterSimsDF.to_csv(simOutFileName)
    masterPathsDF.to_csv(pathOutFileName)
    # writer = ExcelWriter(outFileName)
    # masterSimsDF.to_excel(writer,sheet_name="simData",index=False)
    # masterPathsDF.to_excel(writer,sheet_name="pathData")
    # writer.save()


if __name__ == '__main__':
    main(5)
    # call main with two separate settings, make main return pandas dataframes (one for paths and one for sims)
    # merge and print out the pandas dataframes
