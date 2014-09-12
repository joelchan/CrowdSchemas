from lsa_client import lsa_uc
import itertools as it
import pandas as pd
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

srcdir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/small_surface/"

docs = {}
for f in os.listdir(srcdir):
    fpath = srcdir + f
    if ".DS_Store" not in f and os.path.isfile(fpath):
        words = []
        for w in read_data(fpath):
            words.append(w.split(',')[0])
        docs[f] = ' '.join(words)

# docs = {}
# for doc in os.listdir(srcdir):
#     if ".DS_Store" not in doc:
#         text = open(os.path.join(srcdir,doc)).read()
#         docs[doc] = text
    # print "%s:\n%s\n" %(doc, text)

combos = []
pairs = []
for c in it.product(docs.keys(),docs.keys()):
    (doc1, doc2) = c
    if [doc1, doc2] not in pairs and doc1 != doc2:
        pairName = "%s VS %s" %(doc1,doc2)
        cDict = {"docPair": pairName, "doc1": docs[doc1], "doc2": docs[doc2]}
        sim = lsa_uc(docs[doc1],docs[doc2])
        cDict["LSASIM"] = sim
        combos.append(cDict)
        pairs.append([doc1,doc2])
        pairs.append([doc2,doc1])
        print "Sim for docpair %s is %.2f" %(pairName,sim)

df = pd.DataFrame(combos)
df.to_csv("lsa_surface.csv")
