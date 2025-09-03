import logging
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class NewsScrapper:
    def __init__(self):
        self.session = requests.Session()
        # Rotate between different user agents
        self.user_agents = [
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        
    def get_headers(self, referer=None):
        agent =random.choice(self.user_agents)
        logger.info(agent)
        """Generate headers with random user agent"""
        headers = {
            "User-Agent": agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
        
        if referer:
            headers["Referer"] = referer
            
        return headers

    def extract_image(self, url=None, max_retries=3, delay_range=(1, 3)):
        """
        Extract image with enhanced anti-detection measures
        """
        if not url:
            return None
            
        for attempt in range(max_retries):
            try:
                # Add random delay between requests
                if attempt > 0:
                    delay = random.uniform(*delay_range)
                    logger.info(f"Retry {attempt}, waiting {delay:.1f}s...")
                    time.sleep(delay)
                
                # Get domain for referer
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                headers = self.get_headers(referer=base_url)
                
                resp = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=15,
                    allow_redirects=True
                )
                
                # Handle different status codes
                if resp.status_code == 403:
                    logger.info(f"403 Forbidden on attempt {attempt + 1}")
                    continue
                elif resp.status_code == 429:
                    logger.info(f"Rate limited, waiting longer...")
                    time.sleep(random.uniform(10, 20))
                    continue
                    
                resp.raise_for_status()
                
                # Parse content
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Multiple strategies to find images
                image_url = self._find_main_image(soup, base_url)
                
                return image_url
                
            except requests.exceptions.RequestException as e:
                logger.info(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                    
        return None
    
    def _find_main_image(self, soup, base_url):
        """
        Multiple strategies to find the main image
        """
        image_selectors = [
            # Open Graph image
            'meta[property="og:image"]',
            'meta[property="og:image:url"]',
            # Twitter Card image
            'meta[name="twitter:image"]',
            'meta[name="twitter:image:src"]',
            # Article images
            'article img',
            '.article-image img',
            '.featured-image img',
            '.hero-image img',
            # General content images
            '.content img',
            'main img',
            # Fallback to any img
            'img'
        ]
        
        for selector in image_selectors:
            elements = soup.select(selector)
            
            for element in elements:
                if element.name == 'meta':
                    image_url = element.get('content')
                else:
                    image_url = element.get('src') or element.get('data-src')
                
                if image_url:
                    # Convert relative URLs to absolute
                    if not image_url.startswith(('http://', 'https://')):
                        image_url = urljoin(base_url, image_url)
                    
                    # Basic validation
                    if self._is_valid_image_url(image_url):
                        return image_url
        
        return None
    
    def _is_valid_image_url(self, url):
        """
        Basic validation for image URLs
        """
        if not url or len(url) < 10:
            return False
            
        # Skip common non-image patterns
        skip_patterns = [
            'logo', 'icon', 'avatar', 'placeholder', 
            'default', 'blank', 'spacer', '1x1'
        ]
        
        url_lower = url.lower()
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False
                
        return True
