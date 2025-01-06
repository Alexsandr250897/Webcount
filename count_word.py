import asyncio
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urljoin, urlparse
from typing import Set, Dict, List, Tuple


class AsyncWordCounter:
    def __init__(self, base_url: str, max_depth: int, max_requests: int):
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_requests = max_requests
        self.visited_urls: Set[str] = set()
        self.word_counts: Counter[str] = Counter()
        self.semaphore = asyncio.Semaphore(self.max_requests)

    async def fetch_html(self, url: str, session: ClientSession) -> str:
        async with self.semaphore:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"Failed to fetch {url}: HTTP {response.status}")
            except Exception as e:
                print(f"Error fetching {url}: {e}")
            return ""

    async def extract_links(self, html: str, current_url: str) -> Set[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            full_url = urljoin(current_url, href)
            if urlparse(full_url).netloc == urlparse(self.base_url).netloc and not any(
                    exclude in full_url for exclude in ["action=edit", "discussion", "redlink=1"]):
                links.add(full_url)
        return links

    async def count_words(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        if text.strip():
            words = text.split()
            self.word_counts.update(word.lower() for word in words if word.isalpha())

    async def crawl_page(self, url: str, depth: int, session: ClientSession):
        """Crawl the page, visit links, and count words."""
        if url in self.visited_urls or depth > self.max_depth:
            return
        print(f"Visiting {url} at depth {depth}")
        self.visited_urls.add(url)
        html = await self.fetch_html(url, session)
        if not html:
            return
        await self.count_words(html)
        links = await self.extract_links(html, url)
        tasks = [self.crawl_page(link, depth + 1, session) for link in links]
        if tasks:
            await asyncio.gather(*tasks)

    async def start_crawling(self):
        async with aiohttp.ClientSession() as session:
            await self.crawl_page(self.base_url, 0, session)

    async def get_top_words(self, n: int) -> List[Tuple[str, int]]:
        return self.word_counts.most_common(n)


async def main():
    base_url = "https://ru.wikipedia.org/"
    max_depth = 1
    max_requests = 5
    word_counter = AsyncWordCounter(base_url, max_depth, max_requests)

    await word_counter.start_crawling()
    top_words = await word_counter.get_top_words(10)

    print("Top words:")
    for word, count in top_words:
        print(f"{word}: {count}")


if __name__ == "__main__":
    asyncio.run(main())

