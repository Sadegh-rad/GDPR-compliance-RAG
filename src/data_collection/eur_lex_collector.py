"""
EUR-Lex GDPR Data Collector
Fetches GDPR regulation text in multiple languages
"""
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import time
import re


class EURLexCollector:
    """Collector for EUR-Lex GDPR regulation data"""
    
    def __init__(self, output_dir: str = "data/raw/eur_lex"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # CELEX number for GDPR
        self.celex = "32016R0679"
        self.base_url = "https://eur-lex.europa.eu/legal-content"
        
        # Language codes
        self.languages = {
            "EN": "English",
            "DE": "German",
            "FR": "French",
            "ES": "Spanish",
            "IT": "Italian",
            "NL": "Dutch",
            "PL": "Polish",
            "PT": "Portuguese",
            "RO": "Romanian",
            "SV": "Swedish"
        }
    
    def fetch_gdpr_text(self, language: str = "EN") -> Optional[Dict]:
        """
        Fetch GDPR text in specified language
        
        Args:
            language: Two-letter language code (e.g., 'EN', 'DE')
        
        Returns:
            Dictionary containing the full text and metadata
        """
        if language not in self.languages:
            logger.error(f"Unsupported language: {language}")
            return None
        
        url = f"{self.base_url}/{language}/TXT/HTML/?uri=CELEX:{self.celex}"
        
        try:
            logger.info(f"Fetching GDPR text in {self.languages[language]}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main content
            content_div = soup.find('div', {'id': 'text'}) or soup.find('div', {'class': 'eli-main-content'})
            
            if not content_div:
                logger.warning("Could not find main content div")
                content_div = soup.find('body')
            
            # Extract structured content
            articles = self._extract_articles(content_div)
            recitals = self._extract_recitals(content_div)
            chapters = self._extract_chapters(content_div)
            
            # Get full text
            full_text = content_div.get_text(separator='\n', strip=True) if content_div else ""
            
            document = {
                "source": "EUR-Lex",
                "document_type": "regulation",
                "celex": self.celex,
                "title": "Regulation (EU) 2016/679 (GDPR)",
                "language": language,
                "language_name": self.languages[language],
                "url": url,
                "full_text": full_text,
                "articles": articles,
                "recitals": recitals,
                "chapters": chapters,
                "metadata": {
                    "fetch_date": time.strftime("%Y-%m-%d"),
                    "word_count": len(full_text.split())
                }
            }
            
            # Save to file
            output_file = self.output_dir / f"gdpr_{language.lower()}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(document, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved GDPR text to {output_file}")
            logger.info(f"Articles: {len(articles)}, Recitals: {len(recitals)}, Chapters: {len(chapters)}")
            
            return document
            
        except requests.RequestException as e:
            logger.error(f"Error fetching GDPR text: {e}")
            return None
    
    def _extract_articles(self, soup) -> List[Dict]:
        """Extract individual articles from the document"""
        articles = []
        
        # Look for article patterns
        article_pattern = re.compile(r'Article\s+(\d+)', re.IGNORECASE)
        
        # Find all potential article headers
        for tag in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4']):
            text = tag.get_text(strip=True)
            match = article_pattern.search(text)
            
            if match:
                article_num = match.group(1)
                
                # Extract article title (text after article number)
                title = text[match.end():].strip()
                
                # Get content (next siblings until next article)
                content_parts = []
                current = tag.find_next_sibling()
                
                while current:
                    if current.name in ['p', 'div']:
                        sibling_text = current.get_text(strip=True)
                        if article_pattern.search(sibling_text):
                            break
                        if sibling_text:
                            content_parts.append(sibling_text)
                    current = current.find_next_sibling()
                
                articles.append({
                    "number": article_num,
                    "title": title,
                    "content": "\n".join(content_parts)
                })
        
        return articles
    
    def _extract_recitals(self, soup) -> List[Dict]:
        """Extract recitals from the document"""
        recitals = []
        
        # Recitals typically appear before Article 1
        recital_pattern = re.compile(r'\((\d+)\)')
        
        for tag in soup.find_all(['p', 'div']):
            text = tag.get_text(strip=True)
            
            # Check if this starts with a recital number
            match = recital_pattern.match(text)
            if match:
                recital_num = match.group(1)
                content = text[match.end():].strip()
                
                recitals.append({
                    "number": recital_num,
                    "content": content
                })
        
        return recitals
    
    def _extract_chapters(self, soup) -> List[Dict]:
        """Extract chapter structure"""
        chapters = []
        
        chapter_pattern = re.compile(r'CHAPTER\s+([IVX]+)', re.IGNORECASE)
        
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
            text = tag.get_text(strip=True)
            match = chapter_pattern.search(text)
            
            if match:
                chapter_num = match.group(1)
                title = text[match.end():].strip()
                
                chapters.append({
                    "number": chapter_num,
                    "title": title
                })
        
        return chapters
    
    def fetch_all_languages(self, languages: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch GDPR text in multiple languages
        
        Args:
            languages: List of language codes. If None, fetches all available languages
        
        Returns:
            List of document dictionaries
        """
        if languages is None:
            languages = list(self.languages.keys())
        
        documents = []
        for lang in languages:
            logger.info(f"Fetching {lang}...")
            doc = self.fetch_gdpr_text(lang)
            if doc:
                documents.append(doc)
            time.sleep(2)  # Be respectful to the server
        
        return documents


if __name__ == "__main__":
    collector = EURLexCollector()
    
    # Fetch English version
    collector.fetch_gdpr_text("EN")
    
    # Or fetch multiple languages
    # collector.fetch_all_languages(["EN", "DE", "FR"])
