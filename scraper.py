import requests
import os
from bs4 import BeautifulSoup

url = "http://tinyurl.com/sample-oss-posts"
ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
headers = {"User-Agent": ua}
resp = requests.get(url, headers=headers)
bytes = resp.content
with open('blog_list.html', 'wb+') as outfile:
    outfile.write(bytes)

parsed = BeautifulSoup([resp.text],"html5lib")
entries = parsed.find_all('div', class_='feedEntry')
titles = [e.find('a').find('h2').string for e in entries]
print(titles)