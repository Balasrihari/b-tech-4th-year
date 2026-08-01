"""Web Scraping Service for URL content ingestion"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from loguru import logger
import re


class WebScrapingService:
    """Service for extracting content from URLs"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 30
    
    def extract_content_from_url(
        self,
        url: str,
        include_links: bool = False
    ) -> Dict[str, Any]:
        """
        Extract content from a URL
        
        Args:
            url: URL to scrape
            include_links: Whether to include links in content
            
        Returns:
            Dictionary with title, content, metadata
        """
        try:
            # Fetch the URL
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else url
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Clean content
            content = self._clean_text(content)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, response)
            
            # Extract links if requested
            links = []
            if include_links:
                links = self._extract_links(soup, url)
            
            result = {
                'title': title.strip(),
                'content': content,
                'url': url,
                'metadata': metadata,
                'links': links if include_links else [],
                'word_count': len(content.split()),
                'char_count': len(content)
            }
            
            logger.info(f"Successfully extracted content from {url}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            raise
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            return main_content.get_text(separator=' ', strip=True)
        
        # Fallback to body
        return soup.body.get_text(separator=' ', strip=True) if soup.body else ''
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'[.,!?;:]{2,}', '.', text)
        
        return text.strip()
    
    def _extract_metadata(self, soup: BeautifulSoup, response) -> Dict[str, str]:
        """Extract metadata from HTML"""
        metadata = {}
        
        # Meta description
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            metadata['description'] = description.get('content', '')
        
        # Meta keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords:
            metadata['keywords'] = keywords.get('content', '')
        
        # Open Graph tags
        og_tags = ['og:title', 'og:description', 'og:image', 'og:type']
        for tag in og_tags:
            og_element = soup.find('meta', property=tag)
            if og_element:
                metadata[tag] = og_element.get('content', '')
        
        # Response headers
        metadata['content_type'] = response.headers.get('content-type', '')
        metadata['last_modified'] = response.headers.get('last-modified', '')
        
        return metadata
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract links from page"""
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            
            if text and href:
                links.append({
                    'url': href,
                    'text': text
                })
        
        return links[:20]  # Limit to first 20 links
    
    def is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))


# Global web scraping service instance
web_scraping_service = WebScrapingService()
