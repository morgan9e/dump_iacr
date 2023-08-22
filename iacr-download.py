import requests, json, time
from bs4 import BeautifulSoup as bs
import aiohttp, aiofiles
import asyncio
import tqdm, os
from urllib.parse import urlparse

HOST = "https://eprint.iacr.org"
BASE = "downloads"
MAX_RETRIES = 3  # You can adjust this value as needed
RETRY_DELAY = 5  # Delay in seconds before retrying

async def fetch_content(session, url):
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an error for bad responses
                return await response.read()
        except (aiohttp.client_exceptions.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
            if attempt < MAX_RETRIES - 1:  # i.e. don't sleep on the last attempt
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise e from None

async def save_to_file(filename, content):
    async with aiofiles.open(os.path.join(BASE, filename), 'wb') as f:
        await f.write(content)

async def download_url(session, url, pbar=None):
    parsed_url = urlparse(url)
    filename = str(parsed_url.path)[1:].replace("/", "-")
    if os.path.exists(os.path.join(BASE, filename)):
        if pbar:
            pbar.update(1)
        return
    content = await fetch_content(session, url)
    # print(filename)
    await save_to_file(filename, content)
    if pbar:
        pbar.update(1)

async def main(jsons):
    # Flatten the files lists to get a single list of all files
    all_files = [file for entry in jsons for file in entry["files"]]
    pbar = tqdm.tqdm(total=len(all_files))
    
    async with aiohttp.ClientSession() as session:
        tasks = [download_url(session, HOST + file, pbar) for file in all_files]
        await asyncio.gather(*tasks)
    pbar.close()

with open("iacr_all.json", "r") as f:
    files = json.loads(f.read())

asyncio.run(main(files))