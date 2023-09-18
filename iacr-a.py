import requests, json, time
from bs4 import BeautifulSoup as bs

url = "https://eprint.iacr.org/complete/?offset={}"

def pfetch(href):
    

def modify_urls(soup):
    for i in soup.find_all("link") + soup.find_all("a"):
        if href := i.get("href"):
            href = pfetch(href)

for offset in range(0,1000,100):
    URL = url.format(offset)
    soup = bs(requests.get(URL).text, features="lxml")
    modify_urls(soup)
    with open("index.html", "w") as f:
        f.write(str(soup))