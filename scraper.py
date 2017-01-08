import requests
import os
from bs4 import BeautifulSoup
import pprint

# Get your requests set up, and write to a txt file
url = "http://tinyurl.com/sample-oss-posts"
ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
headers = {"User-Agent": ua}
resp = requests.get(url, headers=headers)
bytes = resp.content
with open('blog_list.html', 'wb+') as outfile:
    outfile.write(bytes)

# Parse the html using BeautifulSoup and html5lib
parsed = BeautifulSoup(resp.text, "html5lib")

# Grab a list of entries by finding each div with the class name 'feedEntry'
entries = parsed.find_all('div', class_='feedEntry')


def get_classifier(entry):
    """Grab tags (classifiers) from bylines."""
    byline = entry.find('p', class_='discreet')
    for classifier in ['django', 'postgresql']:
        if classifier in byline.text.lower():
            return classifier
    return "other"


def get_title(entry):
    """Find titles and strip off whitespace."""
    return entry.find('a').find('h2').string.strip()


paired = [(get_classifier(e), get_title(e)) for e in entries]

# Create a dictionary with categorized post titles.
groups = {}
for cat, title in paired:
    list = groups.setdefault(cat, [])
    list.append(title)

pprint.pprint(groups['django'])
