import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/"
}


class NewsScrapper():
        
    def extract(self, url=None):
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else None

        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            excerpt = meta_desc['content'].strip()

        # 2. fallback: look for the first paragraph in the main content
        if not excerpt:
            article_body = soup.find('div', attrs={'data-gu-name': 'body'})
            if article_body:
                first_p = article_body.find('p')
                if first_p:
                    excerpt = first_p.get_text(strip=True)

        image_url = None
        figure = soup.find('figure')
        if figure:
            img = figure.find('img')
            if img and img.has_attr('src'):
                image_url = img['src']
        return {
            'title': title,
            'excerpt': excerpt,
            'image': image_url,
        }

if __name__ == '__main__':
    # url = 'https://www.theguardian.com/us-news/2025/jul/31/trump-extends-deadline-tariff-deal-mexico'
    # url = "https://www.bbc.com/news/articles/c8ryjpjrvddo"  
    # url = "https://www.nytimes.com/2025/07/31/business/amazon-earnings-second-quarter.html"
    # scrapper = NewsScrapper()
    # data = scrapper.extract(url)
    # print(data)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.nytimes.com/2025/07/31/business/amazon-earnings-second-quarter.html")
        content = page.content()
        print(content)
