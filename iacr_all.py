import requests, json, time
from bs4 import BeautifulSoup as bs

URL_HOST = "https://eprint.iacr.org"
URL_OFFSET = lambda x: f"{URL_HOST}/complete/?offset={x}"

def parse(html):
    ret = []
    soup = bs(html, features="lxml")
    paperList = soup.find("div", class_="paperList").findChildren("div" , recursive=False)
    assert len(paperList) % 2 == 0
    for i in range(0, len(paperList), 2):
        head = paperList[i]
        body = paperList[i+1]
        links = [k["href"] for k in head.find_all("a")]
        title = body.find("div", class_="papertitle").text
        category = body.find("small", class_="category").text
        authors = body.find("div", class_="summaryauthors").text
        abstract = body.find("div", class_="paper-abstract").text
        ret.append({"title": title, "category": category, "authors": authors.split(", "), "abstract": abstract, "links": links[0], "files": links[1:]})
    return ret

import aiohttp
import asyncio
import tqdm

async def fetch_content(session, url):
    async with session.get(url) as response:
        return await response.text()

async def process_url(session, url, results, pbar = None):
    content = await fetch_content(session, url)
    print(url)
    parsed_data = parse(content)
    results += (parsed_data)
    if pbar:
        pbar.update(1)

async def main(url_list):
    results = []
    pbar = tqdm.tqdm(total=len(url_list))
    async with aiohttp.ClientSession() as session:
        tasks = [process_url(session, url, results, pbar) for url in url_list]
        await asyncio.gather(*tasks)
    pbar.close()
    return results

def find_last():
    offset = 0
    while True:
        req = requests.get(URL_OFFSET(offset))
        if "<h5>No results</h5>" in req.text:
            print(offset)
            offset -= 10000
            break
        offset += 10000
    
    while True:
        req = requests.get(URL_OFFSET(offset))
        if "<h5>No results</h5>" in req.text:
            print(offset)
            offset -= 1000
            break
        offset += 1000
    
    while True:
        req = requests.get(URL_OFFSET(offset))
        if "<h5>No results</h5>" in req.text:
            print(offset)
            offset -= 100
            break
        offset += 100

    return offset

last = find_last()
print(last)
url_list = [URL_OFFSET(i) for i in range(0, last, 100)]
results = asyncio.run(main(url_list))
with open("iacr_all.json", "w") as f:
    f.write(json.dumps(results, indent=4))