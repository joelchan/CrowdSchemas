from bs4 import BeautifulSoup
import re, os, json, csv

ideaDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/submissions/"
ideaTextDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/WOZ/text/"

def grab_idea_info(domSoup):
    """
    this is VERY hacky and brittle at the moment, but it works
    we're basically finding all the scripts, 
    then grabbing the relevant idea info (because it's not in HTML tags),
    which luckily is denoted by quirky.cache.ideation, and includes everything
    we need for now
    """
    ideaScripts = ideaSoup.find('head').find_all('script')
    for script in ideaScripts:
        scriptText = str(script)
        if re.search("quirky.cache.ideation",scriptText):
            lines = scriptText.split('\n')
            lineText = lines[2]
            break #no need to search through the whole thing
    return lineText

# parse the ideas
ideaInfo = []
textFields = [u'category',
              u'title',
              u'description',
              u'problem',
              u'solution']
for f in os.listdir(ideaDir):
    if ".DS" not in f:
        # make the soup
        print "Processing %s..." %f
        ideaFile = ideaDir + f
        ideaSoup = BeautifulSoup(open(ideaFile),'html5lib')
        # grab idea info
        lineText = grab_idea_info(ideaSoup)
        # parse from json
        lineText = lineText.replace("window.quirky.cache.ideation = ","")
        lineDict = json.loads(lineText[:-1])
        # now we can grab the relevant bits, because it's in a dict now
        # we can extract more metadata later
        ideaText = ''.join(["%s\n%s\n%s\n%s\n\n" %("-"*20, field, "-"*20, lineDict[field]) for field in textFields])
        # for field in textFields:

        # ideaText = "Title:\n%s\n%s\n\n" %("-"*20, lineDict[u'title'])
        # ideaText += "Title:\n%s\n%s\n\n" %("-"*20, lineDict[u'title'])
        encodedtext = ideaText.encode("utf-8","ignore")
        # print out the data
        #outFileName = ideaTextDir + lineDict[u'id'] + " " + lineDict[u'title'] + ".txt"
        outFileName = "%s%i.txt" %(ideaTextDir,lineDict[u'id'])
        outFile = open(outFileName,'w')
        outFile.write(encodedtext)
        outFile.close()

        # extract some simple metadata
        words = [w for w in encodedtext.split(" ") if any(c.isalpha() for c in w)]
        ideaInfo.append({'id':lineDict[u'id'],
            'title':lineDict[u'title'].encode("utf=8","ignore"),
            'length':len(words),
            'category':lineDict[u'category'].encode("utf=8","ignore"),
            'votes_count':lineDict[u'votes_count'],
            # 'accept_date':lineDict[u'accepted_at'].encode("utf=8","ignore")
            })

with open("metadata.csv",'w') as csvfile:
    writer = csv.writer(csvfile,delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(["id","title","length","category","votes_count","accept_date"])
    for idea in ideaInfo:
        writer.writerow([idea['id'],
            idea['title'],
            idea['length'],
            idea['category'],
            idea['votes_count'],
            # idea['accept_date'],
            ])
    csvfile.close()


