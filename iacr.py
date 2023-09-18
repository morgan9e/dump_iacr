import requests, json, time
from bs4 import BeautifulSoup as bs
import os, asyncio, aiohttp, aiofiles

class Progress():
    def __init__(self, max = 0):
        self.progress = 0
        self.max = max
        try:
            self.max_width = int(os.get_terminal_size().columns) - 2
        except:
            self.max_width = 80
        self.width = self.max_width - (12 + 2*len(str(self.max)))

    def update(self, n):
        self.progress += 1
        self.display()

    def display(self):
        if self.max:
            width = int(self.progress*self.width / self.max)
            print(f"\r{self.progress*100/self.max:5.2f}% [{('='*width):<{self.width}}] {self.progress}/{self.max} ".ljust(self.max_width), end = "")
        else:
            print(f"\r{self.progress:>4} {'='*self.progress}", end = "")

    def reset(self):
        self.progress = 0

    def close(self):
        print()

async def fetch_get(url, handler, pbar = None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                handler(await resp.text())
                if pbar:
                    pbar.update(1)
    except Exception as e:
        print(e)

papers = []
def handler(data):
    global papers
    off_url = "https://eprint.iacr.org"
    get_items = (lambda x: [ off_url + item.find_all("a")[0]["href"] for item in bs(x,features="lxml").find("div", class_="paperList").find_all("div", class_="flex-grow-1")])
    papers += get_items(data)

async def main():
    tasks = []
    url = "https://eprint.iacr.org/complete/?offset={}"
    cnt = 0
    pbar = Progress(203)
    async with asyncio.TaskGroup() as group:
        for offset in range(0,20330,100):
            group.create_task(fetch_get(url.format(offset), handler, pbar))
    pbar.close()
   
start_time = time.time()
asyncio.run(main())
print(papers)
with open("iacr.json", "w") as f:
    f.write(json.dumps(papers))
print(f"time {(time.time() - start_time):.3f} sec")