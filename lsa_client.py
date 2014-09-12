from bs4 import BeautifulSoup as bs
import requests

def lsa_uc(phrase1, phrase2):

    uses = [phrase1, phrase2]


    post_data = {"LSAspace": "General_Reading_up_to_1st_year_college (300 factors)",
                 "txt1": ".\n".join(uses) + "."}

    r = requests.post('http://lsa.colorado.edu/cgi-bin/LSA-sentence-x.html',
                      data=post_data)

    soup = bs(r.text)
    try:
        similarity = str(soup.find_all('td')[0].table.tr.td.text)
        similarity = float(similarity.strip())
    except:
        similarity = 0.0
    finally:
        return similarity