"""
Data collection orchestrator
Coordinates all data collection from different sources
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from typing import Dict, List
import json
import time

from data_collection.eur_lex_collector import EURLexCollector
from data_collection.edpb_collector import EDPBCollector
from data_collection.gdprhub_collector import GDPRhubCollector


class DataCollectionOrchestrator:
    """Orchestrates data collection from all sources"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.data_sources = config.get('data_sources', {})
        
        # Initialize collectors
        self.eur_lex = EURLexCollector()
        self.edpb = EDPBCollector()
        self.gdprhub = GDPRhubCollector()
    
    def collect_all(self) -> Dict[str, List]:
        """
        Collect data from all enabled sources
        
        Returns:
            Dictionary with collected documents by source
        """
        results = {}
        
        logger.info("Starting comprehensive data collection...")
        
        # Collect EUR-Lex GDPR text
        if self.data_sources.get('eur_lex', {}).get('enabled', True):
            logger.info("\n=== Collecting EUR-Lex GDPR Regulation ===")
            languages = self.data_sources.get('eur_lex', {}).get('languages', ['EN'])
            results['eur_lex'] = self.eur_lex.fetch_all_languages(languages)
            logger.info(f"Collected {len(results['eur_lex'])} GDPR documents")
        
        # Collect EDPB materials
        if self.data_sources.get('edpb_guidelines', {}).get('enabled', True):
            logger.info("\n=== Collecting EDPB Guidelines ===")
            results['edpb_guidelines'] = self.edpb.fetch_all_guidelines(limit=10)
            logger.info(f"Collected {len(results['edpb_guidelines'])} guidelines")
        
        if self.data_sources.get('edpb_sme_guide', {}).get('enabled', True):
            logger.info("\n=== Collecting EDPB SME Guide ===")
            sme_guide = self.edpb.fetch_sme_guide()
            results['edpb_sme'] = [sme_guide] if sme_guide else []
        
        # Collect case law
        if self.data_sources.get('gdprhub', {}).get('enabled', True):
            logger.info("\n=== Collecting GDPRhub Case Law ===")
            results['gdprhub_cases'] = self.gdprhub.fetch_all_cases(limit=20)
            logger.info(f"Collected {len(results['gdprhub_cases'])} cases")
        
        # Save collection summary
        self._save_collection_summary(results)
        
        logger.info("\n=== Data Collection Complete ===")
        logger.info(f"Total documents collected: {sum(len(v) for v in results.values())}")
        
        return results
    
    def _save_collection_summary(self, results: Dict):
        """Save summary of data collection"""
        summary = {
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {}
        }
        
        for source, documents in results.items():
            summary["sources"][source] = {
                "count": len(documents),
                "documents": [
                    {
                        "title": doc.get("title", "Unknown"),
                        "language": doc.get("language", "en"),
                        "word_count": doc.get("metadata", {}).get("word_count", 0)
                    }
                    for doc in documents
                ]
            }
        
        summary_file = Path("data/raw/collection_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved collection summary to {summary_file}")


if __name__ == "__main__":
    # Load config
    import yaml
    
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    orchestrator = DataCollectionOrchestrator(config)
    orchestrator.collect_all()
