from lsa_client import lsa_uc
import itertools as it
import pandas as pd
import os, csv, json

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

def get_fulltext(textdir):
    fullText = {}
    for text in os.listdir(textdir):
        textpath = os.path.join(textdir,text)
        if os.path.isfile(textpath):
            fullText[text] = open(textpath).read()
    return fullText

srcdir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_tokenized/"
fullTextDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_raw/"
resultsDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/results/lsa/"
jsonOut = "%slsa.json" %resultsDir

keyWordsData = pd.read_csv("/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_keywords_enhanced.csv")
# docs = {}
# for f in os.listdir(srcdir):
#     fpath = srcdir + f
#     if ".DS_Store" not in f and os.path.isfile(fpath):
#         text = open(fpath).read()
#         text.replace(".","").replace(",","")
#         docs[f] = text
    # print "%s:\n%s\n" %(doc, text)

combos = []
pairs = []
docNames = set(keyWordsData['doc'])
for c in it.product(docNames,docNames):
    (doc1, doc2) = c
    if [doc1, doc2] not in pairs and doc1 != doc2:
        pairName = "%s-TO-%s" %(doc1.replace(".txt",""),doc2.replace(".txt",""))
        pairNameReverse = "%s-TO-%s" %(doc2.replace(".txt",""),doc1.replace(".txt",""))
        cDict = {"docPair": pairName, "docPairReverse":pairNameReverse, "doc1": doc1, "doc2": doc2}
        for name, group in keyWordsData.groupby(['type']):
            words1 = ' '.join(group[group['doc'] == doc1].keyword)
            words2 = ' '.join(group[group['doc'] == doc2].keyword)
            print "%s words for doc1: %s" %(name, words1)
            print "%s words for doc2: %s" %(name, words2)
            sim = lsa_uc(words1,words2)
            cDict[name] = sim
            combos.append(cDict)
            pairs.append([doc1,doc2])
            pairs.append([doc2,doc1])
            print "%s similarity for docpair %s is %.2f" %(name,pairName,sim)

df = pd.DataFrame(combos)

# dfMatches = df.sort(['LSASIM'],ascending=False)[:20]

df.to_csv("%slsa_split2.csv" %resultsDir)
# df = df.set_index(['docPair'])
# dfMatches.to_json(jsonOut,orient="index")

# masterMasterDict = json.loads(open(jsonOut).read())

# # merge in full text
# fullTexts = get_fulltext(fullTextDir)
# for key, value in masterMasterDict.iteritems():
#     print masterMasterDict[key]['doc1']
#     masterMasterDict[key]['doc1text'] = fullTexts[masterMasterDict[key]['doc1']]
#     masterMasterDict[key]['doc2text'] = fullTexts[masterMasterDict[key]['doc2']]


# open(jsonOut,'w').write(json.dumps(masterMasterDict,indent=4))
