import asyncio
from urllib.parse import urljoin
from random import choice
from typing import List
import httpx
from dataclasses import dataclass, field


@dataclass
class AirflowHouse:
    zillow_url: str = 'https://www.zillow.com'
    useragent: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Wayland; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.137 Safari/537.36 Ubuntu/22.04 (5.0.2497.35-1) Vivaldi/5.0.2497.35',
        'Mozilla/5.0 (Wayland; Linux x86_64; System76 Galago Pro (galp2)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.175 Safari/537.36 Ubuntu/22.04 (5.0.2497.48-1) Vivaldi/5.0.2497.48',
        'Mozilla/5.0 (Wayland; Linux x86_64; System76 Galago Pro (galp2)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.175 Safari/537.36 Ubuntu/22.04 (5.0.2497.51-1) Vivaldi/5.0.2497.51,',
        'Mozilla/5.0 (Wayland; Linux x86_64; System76) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.133 Safari/537.36 Ubuntu/22.04 (5.2.2623.34-1) Vivaldi/5.2.2623.39',
        'Mozilla/5.0 (Wayland; Linux x86_64; System76) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.92 Safari/537.36 Ubuntu/22.04 (5.2.2623.34-1) Vivaldi/5.2.2623.34'
    ])
    proxies: List[str] = field(default_factory=lambda: [
        '192.126.196.93:8800', '154.38.156.188:8800', '154.12.112.208:8800', '154.38.156.187:8800', '154.12.112.163:8800',
        '192.126.196.137:8800', '192.126.194.95:8800', '192.126.194.135:8800', '154.12.113.202:8800', '154.38.156.14:8800'
    ])

    async def fetch(self, client, url):
        r = await client.get(url)
        if r.status_code != 200:
            r.raise_for_status()
        return r.text

    async def fetch_all(self, client, urls):
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.fetch(client, url))
            tasks.append(task)
        response = await asyncio.gather(*tasks)
        return response

    async def extract(self):
        ua = choice(self.useragent)
        proxy = choice(self.proxies)

        proxies = {
            "http://": f"http://{proxy}",
            "https://": f"http://{proxy}",
        }

        headers = {
            'user-agent': ua
        }

        urls = []
        for page in range(1, 3):
            endpoint = f'/tucson-az/rentals/{page}_p'
            url = urljoin(self.zillow_url, endpoint)
            urls.append(url)

        async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=10, follow_redirects=True) as client:
            htmls = await self.fetch_all(client, urls)
        return htmls


if __name__ == '__main__':
    scraper = AirflowHouse()
    htmls = asyncio.run(scraper.extract())
    # print(htmls)