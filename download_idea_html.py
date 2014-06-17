# usage: python download_idea_html.py <startindex> <stopindex>
# for now, to avoid overloading the quirky servers, we're slowly downloading 50 ideas at a time

from bs4 import BeautifulSoup
import re, urllib, sys, os, json, time

NUM_IDEAS = 300
ideaDir = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/IdeaHTML/"
#START_INDEX = int(sys.argv[1])
#STOP_INDEX = int(sys.argv[2])

# read in the path (to optimize later, we probably don't need to read in the whole thing)
filePath = "/Users/jchan/Dropbox/Research/PostDoc/CrowdSchemas/quirky_ideas_528_byRecency.html"
masterDOM = BeautifulSoup(open(filePath),'html5lib')

# grab the ideas
ideas = masterDOM.find_all(class_=re.compile('new-card'))

ideaLinks = []
for idea in ideas:
	thisLink = idea.find(class_="card-link")['href']
	ideaLinks.append(thisLink)
uniqueIdeaLinks = set()
uniqueIdeaLinks.update(ideaLinks)

# download their pages, store for later reference
for thisLink in uniqueIdeaLinks:
	print "Retrieving %s..." %thisLink
	f_name = ideaDir + thisLink.split('/')[-1]
	urllib.urlretrieve(thisLink,f_name)
	time.sleep(.5) # wait 1/2 a second

# print "%i links found" %len(ideaLinks)
# print "%i unique links" %len(uniqueIdeaLinks)

# f = open("links.txt",'w')
# for link in ideaLinks:
# 	f.write(link + "\n")
# f.close()

# # grab their links
# ideaLinks = []
# for i in xrange(NUM_IDEAS):
# 	thisLink = ideas[i].find(class_="card-link")['href']
# 	ideaLinks.append(thisLink)

# # download their pages, store for later reference
# for i in xrange(START_INDEX,STOP_INDEX):
# 	thisLink = ideaLinks[i]
# 	print "Retrieving %s..." %thisLink
# 	f_name = ideaDir + thisLink.split('/')[-1]
# 	urllib.urlretrieve(thisLink,f_name)

