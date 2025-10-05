"""
GDPRhub Data Collector
Fetches GDPR case law from GDPRhub
"""
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import time
import re


class GDPRhubCollector:
    """Collector for GDPRhub case law"""
    
    def __init__(self, output_dir: str = "data/raw/gdprhub"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_url = "https://gdprhub.eu"
        self.api_url = f"{self.base_url}/api.php"
    
    def fetch_case_list(self, limit: int = 100) -> List[Dict]:
        """
        Fetch list of GDPR cases
        
        Args:
            limit: Maximum number of cases to fetch
        
        Returns:
            List of case metadata
        """
        try:
            logger.info(f"Fetching up to {limit} cases from GDPRhub...")
            
            # Using MediaWiki API to get pages in certain categories
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": "Category:Case",
                "cmlimit": min(limit, 500),  # API limit
                "format": "json"
            }
            
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            cases = []
            if "query" in data and "categorymembers" in data["query"]:
                for page in data["query"]["categorymembers"]:
                    cases.append({
                        "title": page["title"],
                        "pageid": page["pageid"],
                        "url": f"{self.base_url}/index.php?curid={page['pageid']}"
                    })
            
            logger.info(f"Found {len(cases)} cases")
            return cases
            
        except Exception as e:
            logger.error(f"Error fetching case list: {e}")
            return []
    
    def fetch_case_content(self, case_info: Dict) -> Optional[Dict]:
        """
        Fetch detailed content of a specific case
        
        Args:
            case_info: Dictionary with case metadata
        
        Returns:
            Dictionary containing case content
        """
        try:
            logger.info(f"Fetching case: {case_info['title']}")
            
            # Fetch page content using MediaWiki API
            params = {
                "action": "parse",
                "pageid": case_info["pageid"],
                "format": "json",
                "prop": "text|categories|sections"
            }
            
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "parse" not in data:
                return None
            
            parse_data = data["parse"]
            html_content = parse_data.get("text", {}).get("*", "")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract case information
            case_data = {
                "source": "GDPRhub",
                "document_type": "case_law",
                "title": case_info["title"],
                "url": case_info["url"],
                "pageid": case_info["pageid"],
                "full_text": soup.get_text(separator='\n', strip=True),
                "sections": [],
                "metadata": {
                    "fetch_date": time.strftime("%Y-%m-%d"),
                    "categories": [cat["*"] for cat in parse_data.get("categories", [])]
                }
            }
            
            # Extract structured information
            case_data["case_details"] = self._extract_case_details(soup)
            case_data["sections"] = self._extract_sections(soup)
            
            return case_data
            
        except Exception as e:
            logger.error(f"Error fetching case content: {e}")
            return None
    
    def _extract_case_details(self, soup) -> Dict:
        """Extract structured case details from infobox"""
        details = {}
        
        # Look for infobox table
        infobox = soup.find('table', {'class': 'infobox'})
        
        if infobox:
            for row in infobox.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    details[key] = value
        
        return details
    
    def _extract_sections(self, soup) -> List[Dict]:
        """Extract sections from case"""
        sections = []
        
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            section_title = heading.get_text(strip=True)
            
            # Get content until next heading
            content_parts = []
            current = heading.find_next_sibling()
            
            while current:
                if current.name in ['h2', 'h3', 'h4']:
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
    
    def fetch_all_cases(self, limit: int = 50) -> List[Dict]:
        """
        Fetch multiple GDPR cases
        
        Args:
            limit: Maximum number of cases to fetch
        
        Returns:
            List of case documents
        """
        case_list = self.fetch_case_list(limit=limit)
        
        documents = []
        
        for i, case_info in enumerate(case_list, 1):
            logger.info(f"Fetching case {i}/{len(case_list)}")
            
            case_doc = self.fetch_case_content(case_info)
            
            if case_doc:
                documents.append(case_doc)
                
                # Save individual case
                safe_filename = re.sub(r'[^\w\s-]', '', case_info['title'])[:100]
                safe_filename = re.sub(r'[-\s]+', '_', safe_filename).lower()
                output_file = self.output_dir / f"case_{i}_{safe_filename}.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(case_doc, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Saved to {output_file}")
            
            time.sleep(2)  # Be respectful to the server
        
        # Save summary
        summary_file = self.output_dir / "cases_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_cases": len(documents),
                "fetch_date": time.strftime("%Y-%m-%d"),
                "cases": [{"title": d["title"], "url": d["url"]} for d in documents]
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Fetched {len(documents)} cases total")
        return documents


if __name__ == "__main__":
    collector = GDPRhubCollector()
    
    # Fetch first 10 cases
    collector.fetch_all_cases(limit=10)
