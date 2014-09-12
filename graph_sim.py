from nltk.corpus import wordnet as wn
from copy import deepcopy
from operator import mul
import numpy as np
import itertools as it
import pandas as pd
from pandas import ExcelWriter
import os, csv, json

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
    def __init__(self, docPair, wordPair, path, scoreRaw, level1, level2, weight, scoreWeighted):
        self.docPair = str(docPair)
        self.wordPair = str(wordPair)
        self.path = str(path)
        self.scoreRaw = scoreRaw
        self.pathLength = int(1/scoreRaw)
        self.level1 = level1
        self.level2 = level2
        self.weight = weight
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
    words1 and words2 are lists of enhancedWords
    """
    
    docPair = "%s TO %s" %(docName1, docName2)

    paths = []
    
    # first expand with synonyms
    # words1 = expand_words(words1)
    # words2 = expand_words(words2)
    
    wordCombos = [c for c in it.product(words1,words2)]
    for wordCombo in wordCombos:
        pair = "%s to %s" %(wordCombo[0].label, wordCombo[1].label)
        pathCombos = [c for c in it.product(wordCombo[0].expansions, wordCombo[1].expansions)]
        # maxSim = max_sim(pathCombos)
        champion = pathSim(docPair,pair,"null",0.1,1,1,0.0,0.0)
        for pathCombo in pathCombos:
            word1 = pathCombo[0]
            word2 = pathCombo[1]
            if word1.synset.pos == word2.synset.pos: # only try and find shortest paths between same POS
                # find shortest path between word, weight by height in hypernym hierarchy
                simRaw = word1.synset.path_similarity(word2.synset)
                # levelWeight = 1.0/np.mean([word1.level, word2.level])
                levelWeight = 1.0/(word1.level*word2.level)
                # weight = np.mean([word1.weight, word2.weight])
                weight = word1.weight*word2.weight
                if simRaw is not None:    
                    simWeighted = simRaw*levelWeight*weight
                    path = "%s TO %s" %(word1.synset.name, word2.synset.name)
                    pathsim = pathSim(docPair,pair,path,simRaw,word1.level,word2.level,weight,simWeighted)
                    if pathsim.scoreWeighted > champion.scoreWeighted:
                        champion = deepcopy(pathsim)
        paths.append(champion)
    if len(paths):
        return sorted(paths, key=lambda x: x.scoreWeighted, reverse=True)
    else:
            return []

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

def grade_sim(sims,n):
    """
    sims is list of similarities
    returns normalized similarity, i.e., ratio of "earned" scores to "maximum" possible score
    based on number of "actual" paths
    """
    simsEarned = [s.scoreWeighted for s in sims if s.path is not "null"]
    simsPossible = [s.weight for s in sims if s.path is not "null"]
    if len(simsEarned):
        return sum(simsEarned)/sum(simsPossible)
    else:
        return 0

def process_sim(srcdir,n,simType,norm):
    # settings = read_data(settingsFile)
    # srcdir = settings[0]
    documents = []
    documentsExpanded = []
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
            documentsExpanded.append(expand_words(words))
            docNames.append(f)

    results = []
    pathsToWrite = []
    combos = [x for x in it.combinations([i for i in xrange(len(documents))],2)]
    for combo in combos:
        doc1 = documents[combo[0]]
        doc2 = documents[combo[1]]
        doc1expanded = documentsExpanded[combo[0]]
        doc2expanded = documentsExpanded[combo[1]]
        docName1 = docNames[combo[0]]
        docName2 = docNames[combo[1]]
        p = "%s TO %s" %(docName1, docName2)
        print "Processing %s vs %s..." %(docName1,docName2)
        comboPath = find_paths(doc1expanded,doc2expanded,docName1,docName2)
        doc1Words = [d.label for d in doc1]
        doc2Words = [d.label for d in doc2]
        if norm:
            sim = grade_sim(comboPath,n)
        else:
            sim = sum_top(comboPath,n) # sum of top n path similarities
        results.append([docName1,docName2,p,sim,doc1Words,doc2Words])
        for combo in sorted(comboPath,key=lambda x: x.scoreWeighted, reverse=True)[:n]:
            pathsToWrite.append([combo.docPair,combo.wordPair,combo.path,combo.scoreRaw,combo.pathLength,combo.level1,combo.level2,combo.weight,combo.scoreWeighted])

    simsColNames = ['doc1','doc2','docPair','sim','words1','words2']
    for i in xrange(3,len(simsColNames)):
        simsColNames[i] = simType + "_" + simsColNames[i]
    pathsColNames = ['docPair','wordPair','path','rawSim','pathLength','level1','level2','weight','weightedSim']
    # for i in xrange(2,len(pathsColNames)):
    #     pathsColNames[i] = simType + "_" + pathsColNames[i]
    simsDF = pd.DataFrame(results,columns=simsColNames)
    pathsDF = pd.DataFrame(pathsToWrite,columns=pathsColNames)
    pathsDF['type'] = simType
    pathsDF['pathID'] = pathsDF.docPair + "_" + pathsDF.wordPair

    # masterDF = simsDF.copy(deep=True)
    # masterDF['pathData'] = {}
    # for docPairName, docPairData in pathsDF.groupby(['docPair']):
    #     masterDF[masterDF['docPair'] == docPairName]['pathData'] = docPairData.ix[:,1:].to_dict()

    return simsDF, pathsDF, #masterDF
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

def get_matches(df,surfaceThreshold=0.0,structureThreshold=1.0):
    return df[(df['surface_sim_z'] < surfaceThreshold) & (df['structure_sim_z'] > structureThreshold)].docPair

def main(n,norm):
    
    runtype = "enhanced_WTpr_topSum_%i" %n
    # settings
    structureSrcDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_structure_subset/"
    surfaceSrcDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_surface_subset/"
    resultsDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/results/%s/" %runtype
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)
    simOutFileName = "%ssmallResults_%s.csv" %(resultsDir,runtype)
    pathOutFileName = "%ssmallResults_%s_PATH.csv" %(resultsDir,runtype)
    jsonFileName = "%ssmallResults_%s.json" %(resultsDir,runtype)
    matchFileName = "%ssmallMatches_%s.json" %(resultsDir,runtype)

    # get data
    structureSimDF, structurePathsDF = process_sim(structureSrcDir,n,"structure",norm)
    surfaceSimDF, surfacePathsDF = process_sim(surfaceSrcDir,n,"surface",norm)
    
    # merge the data
    masterSimsDF = pd.DataFrame.merge(structureSimDF,surfaceSimDF,how="left")
    masterPathsDF = pd.DataFrame.merge(structurePathsDF,surfacePathsDF,how="outer")
    # masterMasterDF = pd.DataFrame.merge(structureMaster,surfaceMaster,how="left")
    masterSimsDF['structure_sim_z'] = (masterSimsDF.structure_sim-np.mean(masterSimsDF.structure_sim))/np.std(masterSimsDF.structure_sim)
    masterSimsDF['surface_sim_z'] = (masterSimsDF.surface_sim-np.mean(masterSimsDF.surface_sim))/np.std(masterSimsDF.surface_sim)

    # print out
    masterSimsDF.to_csv(simOutFileName)
    masterPathsDF.to_csv(pathOutFileName)

    masterSimsDFCopy = masterSimsDF.set_index(['docPair'])
    masterSimsDFCopy.to_json(jsonFileName,orient="index")
    
    masterMasterDict = json.loads(open(jsonFileName).read())
    for docPairName, docPairData in masterPathsDF.groupby(['docPair']):
        structurePaths = []
        surfacePaths = []
        for index, row in docPairData.iterrows():
            # print row
            if row['path'] == "null":
                break
            rowDict = {"wordPair":row['wordPair'],
                       "path":row['path'],
                       "pathLength":row['pathLength'],
                       "weight":row['weight'],
                       "weightedSim":row['weightedSim']}
            if row['type'] == "structure":
                structurePaths.append(rowDict)
            else:
                surfacePaths.append(rowDict)
        masterMasterDict[docPairName]['structurePathData'] = structurePaths
        masterMasterDict[docPairName]['surfacePathData'] = surfacePaths

        # masterMasterDict[docPairName]['pathData'] = docPairData.ix[:,1:].to_dict()
    # masterMasterJSON = json.dumps(masterMasterDict)
    open(jsonFileName,'w').write(json.dumps(masterMasterDict,indent=4))

    matches = get_matches(masterSimsDF)
    matchesDict = {}
    for match in matches:
        matchesDict[match] = masterMasterDict[match]
    open(matchFileName,'w').write(json.dumps(matchesDict,indent=4))

    # pathsColNames = ['docPair','wordPair','path','rawSim','pathLength','level1','level2','weight','weightedSim']
    
    # masterMasterDF.to_json(jsonFileName)
    # surfacePathsDF.to_csv("surfaceSimDF.csv")
    # writer = ExcelWriter(outFileName)
    # masterSimsDF.to_excel(writer,sheet_name="simData",index=False)
    # masterPathsDF.to_excel(writer,sheet_name="pathData")
    # writer.save()


if __name__ == '__main__':
    main(n=5,norm=False)
    # call main with two separate settings, make main return pandas dataframes (one for paths and one for sims)
    # merge and print out the pandas dataframes
