"""
EDPB (European Data Protection Board) Data Collector
Fetches guidelines, recommendations, and opinions
"""
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import time
import re


class EDPBCollector:
    """Collector for EDPB guidelines and documents"""
    
    def __init__(self, output_dir: str = "data/raw/edpb"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_url = "https://www.edpb.europa.eu"
        self.guidelines_url = f"{self.base_url}/our-work-tools/our-documents/guidelines_en"
        self.sme_guide_url = f"{self.base_url}/sme-data-protection-guide_en"
    
    def fetch_guidelines_list(self) -> List[Dict]:
        """
        Fetch list of all EDPB guidelines
        
        Returns:
            List of guideline metadata
        """
        try:
            logger.info("Fetching EDPB guidelines list...")
            response = requests.get(self.guidelines_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            guidelines = []
            
            # Find all guideline links
            # EDPB website structure may vary, adapt selectors as needed
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Look for guideline documents
                if 'guideline' in href.lower() or 'guidelines' in text.lower():
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    
                    guidelines.append({
                        "title": text,
                        "url": full_url,
                        "type": "guideline"
                    })
            
            logger.info(f"Found {len(guidelines)} guidelines")
            return guidelines
            
        except requests.RequestException as e:
            logger.error(f"Error fetching guidelines list: {e}")
            return []
    
    def fetch_guideline_content(self, url: str) -> Optional[Dict]:
        """
        Fetch content of a specific guideline
        
        Args:
            url: URL of the guideline page
        
        Returns:
            Dictionary containing guideline content and metadata
        """
        try:
            logger.info(f"Fetching guideline from {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"
            
            # Extract main content
            content_div = (soup.find('div', {'class': 'content'}) or 
                          soup.find('div', {'class': 'main-content'}) or
                          soup.find('article') or
                          soup.find('main'))
            
            if content_div:
                # Remove navigation, headers, footers
                for tag in content_div.find_all(['nav', 'header', 'footer']):
                    tag.decompose()
                
                full_text = content_div.get_text(separator='\n', strip=True)
            else:
                full_text = soup.get_text(separator='\n', strip=True)
            
            # Extract sections
            sections = self._extract_sections(content_div if content_div else soup)
            
            # Look for PDF download link
            pdf_link = None
            for link in soup.find_all('a', href=True):
                if link['href'].endswith('.pdf'):
                    pdf_link = link['href']
                    if not pdf_link.startswith('http'):
                        pdf_link = f"{self.base_url}{pdf_link}"
                    break
            
            document = {
                "source": "EDPB",
                "document_type": "guideline",
                "title": title,
                "url": url,
                "pdf_url": pdf_link,
                "full_text": full_text,
                "sections": sections,
                "metadata": {
                    "fetch_date": time.strftime("%Y-%m-%d"),
                    "word_count": len(full_text.split())
                }
            }
            
            return document
            
        except requests.RequestException as e:
            logger.error(f"Error fetching guideline content: {e}")
            return None
    
    def _extract_sections(self, soup) -> List[Dict]:
        """Extract sections from document"""
        sections = []
        
        # Find all headers
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            section_title = heading.get_text(strip=True)
            
            # Get content until next heading
            content_parts = []
            current = heading.find_next_sibling()
            
            while current:
                if current.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    break
                
                if current.name in ['p', 'ul', 'ol', 'div']:
                    text = current.get_text(strip=True)
                    if text:
                        content_parts.append(text)
                
                current = current.find_next_sibling()
            
            if content_parts:
                sections.append({
                    "title": section_title,
                    "content": "\n".join(content_parts),
                    "level": heading.name
                })
        
        return sections
    
    def fetch_sme_guide(self) -> Optional[Dict]:
        """
        Fetch EDPB SME Data Protection Guide
        
        Returns:
            Dictionary containing the guide content
        """
        try:
            logger.info("Fetching EDPB SME Guide...")
            response = requests.get(self.sme_guide_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            content_div = soup.find('div', {'class': 'content'}) or soup.find('main')
            
            if content_div:
                full_text = content_div.get_text(separator='\n', strip=True)
                sections = self._extract_sections(content_div)
            else:
                full_text = soup.get_text(separator='\n', strip=True)
                sections = []
            
            document = {
                "source": "EDPB",
                "document_type": "sme_guide",
                "title": "EDPB SME Data Protection Guide",
                "url": self.sme_guide_url,
                "full_text": full_text,
                "sections": sections,
                "metadata": {
                    "fetch_date": time.strftime("%Y-%m-%d"),
                    "word_count": len(full_text.split())
                }
            }
            
            # Save to file
            output_file = self.output_dir / "sme_guide.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(document, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved SME guide to {output_file}")
            return document
            
        except requests.RequestException as e:
            logger.error(f"Error fetching SME guide: {e}")
            return None
    
    def fetch_all_guidelines(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch all EDPB guidelines
        
        Args:
            limit: Maximum number of guidelines to fetch (None for all)
        
        Returns:
            List of guideline documents
        """
        guidelines_list = self.fetch_guidelines_list()
        
        if limit:
            guidelines_list = guidelines_list[:limit]
        
        documents = []
        
        for i, guideline_info in enumerate(guidelines_list, 1):
            logger.info(f"Fetching guideline {i}/{len(guidelines_list)}: {guideline_info['title']}")
            
            doc = self.fetch_guideline_content(guideline_info['url'])
            
            if doc:
                documents.append(doc)
                
                # Save individual guideline
                safe_filename = re.sub(r'[^\w\s-]', '', guideline_info['title'])[:100]
                safe_filename = re.sub(r'[-\s]+', '_', safe_filename).lower()
                output_file = self.output_dir / f"guideline_{i}_{safe_filename}.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(doc, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Saved to {output_file}")
            
            time.sleep(2)  # Be respectful to the server
        
        return documents


if __name__ == "__main__":
    collector = EDPBCollector()
    
    # Fetch SME guide
    collector.fetch_sme_guide()
    
    # Fetch first 5 guidelines
    # collector.fetch_all_guidelines(limit=5)
