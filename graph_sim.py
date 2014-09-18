from nltk.corpus import wordnet as wn
from copy import deepcopy
from operator import mul
import numpy as np
import itertools as it
import pandas as pd
from pandas import ExcelWriter
import os, csv, json, shutil

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
    
    useWeights = False

    docPair = "%s-TO-%s" %(docName1.replace(".txt",""), docName2.replace(".txt",""))

    # for each word
    paths = []
    wordCombos = [c for c in it.product(words1,words2)]
    for wordCombo in wordCombos:
        pair = "%s to %s" %(wordCombo[0].label, wordCombo[1].label)
        pathCombos = [c for c in it.product(wordCombo[0].expansions, wordCombo[1].expansions)]
        
        # for each synset combo
        # champion = pathSim(docPair,pair,"null",0.1,1,1,0.0,0.0)
        for pathCombo in pathCombos:
            word1 = pathCombo[0]
            word2 = pathCombo[1]
            if word1.synset.pos == word2.synset.pos: # only try and find shortest paths between same POS
                # find shortest path between word, weight by height in hypernym hierarchy
                simRaw = word1.synset.path_similarity(word2.synset)
                # levelWeight = 1.0/np.mean([word1.level, word2.level])
                levelWeight = 1.0/(word1.level*word2.level)
                # weight = np.mean([word1.weight, word2.weight])
                if useWeights:
                    weight = word1.weight*word2.weight
                else:
                    weight = 1
                if simRaw is not None:    
                    simWeighted = simRaw*levelWeight*weight
                    path = "%s TO %s" %(word1.synset.name, word2.synset.name)
                    pathsim = pathSim(docPair,pair,path,simRaw,word1.level,word2.level,weight,simWeighted)
                    paths.append(pathsim)
                    # if pathsim.scoreWeighted > champion.scoreWeighted:
                        # champion = deepcopy(pathsim)
        # paths.append(champion)
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

def extract_raw_data(df,simType):
    documents = []
    documentsExpanded = []
    docNames = []
    for docName, docData in df.groupby(['doc']):
        docNames.append(docName)
        keywords = []
        for index, row in docData.iterrows():
            if row['type'] == simType:
                keywords.append(rawWord(row['keyword'],row['POS'],float(row['weight'])))
        documents.append(keywords)
        documentsExpanded.append(expand_words(keywords))
    return documents, documentsExpanded, docNames

def process_combos(combos,documents,documentsExpanded,docNames,norm,n):
    results = []
    pathsToWrite = []
    for combo in combos:
        doc1 = documents[combo[0]]
        doc2 = documents[combo[1]]
        doc1expanded = documentsExpanded[combo[0]]
        doc2expanded = documentsExpanded[combo[1]]
        docName1 = docNames[combo[0]]
        docName2 = docNames[combo[1]]
        p = "%s-TO-%s" %(docName1.replace(".txt",""), docName2.replace(".txt",""))
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
    return results, pathsToWrite

def process_sim(df,n,simType,norm):
    
    # extract the raw data
    documents, documentsExpanded, docNames = extract_raw_data(df,simType)

    # process each possible word pair
    combos = [x for x in it.combinations([i for i in xrange(len(documents))],2)]
    results, pathsToWrite = process_combos(combos,documents,documentsExpanded,docNames,norm,n)

    # write sim results to df
    simsColNames = ['doc1','doc2','docPair','sim','words1','words2']
    for i in xrange(3,len(simsColNames)):
        simsColNames[i] = simType + "_" + simsColNames[i]
    simsDF = pd.DataFrame(results,columns=simsColNames)
    
    # write path results to df
    pathsColNames = ['docPair','wordPair','path','rawSim','pathLength','level1','level2','weight','weightedSim']
    pathsDF = pd.DataFrame(pathsToWrite,columns=pathsColNames)
    pathsDF['type'] = simType
    pathsDF['pathID'] = pathsDF.docPair + "_" + pathsDF.wordPair

    return simsDF, pathsDF, #masterDF

def get_problem_matches(df,noiseThreshold=0.0,signalThreshold=1.0):
    return df[(df['surface_sim_z'] < noiseThreshold) 
                & (df['mechanism_sim_z'] < noiseThreshold)
                & (df['problem_sim_z'] > signalThreshold)].docPair

def get_mechanism_matches(df,noiseThreshold=0.0,signalThreshold=1.0):
    return df[(df['surface_sim_z'] < noiseThreshold) 
                & (df['problem_sim_z'] < noiseThreshold)
                & (df['mechanism_sim_z'] > signalThreshold)].docPair

def get_fulltext(textdir):
    fullText = {}
    for text in os.listdir(textdir):
        textpath = os.path.join(textdir,text)
        if os.path.isfile(textpath):
            fullText[text.replace(".txt","")] = open(textpath).read()
    return fullText

def main(n,norm):
    
    runtype = "enhanced_WTpr_noWordLevelWT_noChamp_split3_topSum_%i" %n
    # settings
    # structureSrcDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_structure_enhanced/"
    # surfaceSrcDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_surface_enhanced/"
    keyWordsData = pd.read_csv("/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_keywords_enhanced_split3.csv")
    fullTextDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_raw/"
    resultsDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/results/%s/" %runtype
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)
    simOutFileName = "%ssmallResults_%s.csv" %(resultsDir,runtype)
    pathOutFileName = "%ssmallResults_%s_PATH.csv" %(resultsDir,runtype)
    jsonFileName = "%srawResults.json" %resultsDir
    problemMatchFileName = "%sproblem_matches.json" %resultsDir
    mechanismMatchFileName = "%smechanism_matches.json" %resultsDir

    # get data
    problemSimDF, problemPathsDF = process_sim(keyWordsData,n,"problem",norm)
    mechanismSimDF, mechanismPathsDF = process_sim(keyWordsData,n,"mechanism",norm)
    surfaceSimDF, surfacePathsDF = process_sim(keyWordsData,n,"surface",norm)
    
    # merge the data
    masterSimsDF = pd.DataFrame.merge(problemSimDF,mechanismSimDF,how="outer")
    masterSimsDF = pd.DataFrame.merge(masterSimsDF,surfaceSimDF,how="outer")
    # masterSimsDF.to_csv("testSim.csv")

    masterPathsDF = pd.DataFrame.merge(problemPathsDF,mechanismPathsDF,how="outer")
    masterPathsDF = pd.DataFrame.merge(masterPathsDF,surfacePathsDF,how="outer")
    # masterPathsDF.to_csv("testPaths.csv")
    
    # masterMasterDF = pd.DataFrame.merge(structureMaster,surfaceMaster,how="left")
    masterSimsDF['problem_sim_z'] = (masterSimsDF.problem_sim-np.mean(masterSimsDF.problem_sim))/np.std(masterSimsDF.problem_sim)
    masterSimsDF['mechanism_sim_z'] = (masterSimsDF.mechanism_sim-np.mean(masterSimsDF.mechanism_sim))/np.std(masterSimsDF.mechanism_sim)
    masterSimsDF['surface_sim_z'] = (masterSimsDF.surface_sim-np.mean(masterSimsDF.surface_sim))/np.std(masterSimsDF.surface_sim)

    # print out
    masterSimsDF.to_csv(simOutFileName)
    masterPathsDF.to_csv(pathOutFileName)

    masterSimsDFCopy = masterSimsDF.set_index(['docPair'])
    masterSimsDFCopy.to_json(jsonFileName,orient="index")
    
    # merge into json
    masterMasterDict = json.loads(open(jsonFileName).read())
    # print masterSimsDF.docPair
    for docPairName, docPairData in masterPathsDF.groupby(['docPair']):
        problemPaths = []
        mechanismPaths = []
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
            if row['type'] == "problem":
                problemPaths.append(rowDict)
            elif row['type'] == "mechanism":
                mechanismPaths.append(rowDict)
            else:
                surfacePaths.append(rowDict)
        masterMasterDict[docPairName]['problemPathData'] = problemPaths
        masterMasterDict[docPairName]['mechanismPathData'] = mechanismPaths
        masterMasterDict[docPairName]['surfacePathData'] = surfacePaths

    # merge in full text
    fullTexts = get_fulltext(fullTextDir)
    for key, value in masterMasterDict.iteritems():
        # print masterMasterDict[key]['doc1']
        masterMasterDict[key]['doc1text'] = fullTexts[masterMasterDict[key]['doc1']]
        masterMasterDict[key]['doc2text'] = fullTexts[masterMasterDict[key]['doc2']]

    open(jsonFileName,'w').write(json.dumps(masterMasterDict,indent=4))

    # screen and print out problem matches
    problemMatches = get_problem_matches(masterSimsDF)
    problemMatchesDict = {}
    for match in problemMatches:
        problemMatchesDict[match] = masterMasterDict[match]
    open(problemMatchFileName,'w').write(json.dumps(problemMatchesDict,indent=4))

    # screen and print out mechanism matches
    mechanismMatches = get_mechanism_matches(masterSimsDF)
    mechanismMatchesDict = {}
    for match in mechanismMatches:
        mechanismMatchesDict[match] = masterMasterDict[match]
    open(mechanismMatchFileName,'w').write(json.dumps(mechanismMatchesDict,indent=4))

    srcdir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/results/src/"
    for f in os.listdir(srcdir):
        srcf = os.path.join(srcdir,f)
        if ".DS_Store" not in f and os.path.isfile(srcf):
            destf = resultsDir + f
            shutil.copy2(srcf,destf)

if __name__ == '__main__':
    main(n=5,norm=False)
    # call main with two separate settings, make main return pandas dataframes (one for paths and one for sims)
    # merge and print out the pandas dataframes
