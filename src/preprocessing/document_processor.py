"""
Document Processor
Handles preprocessing and chunking of collected GDPR documents
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import re
from dataclasses import dataclass, asdict


@dataclass
class DocumentChunk:
    """Represents a chunk of text with metadata"""
    text: str
    metadata: Dict
    chunk_id: str
    source: str
    document_type: str
    
    def to_dict(self):
        return asdict(self)


class GDPRDocumentProcessor:
    """Process and chunk GDPR documents for optimal retrieval"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.text_processing = config.get('text_processing', {})
        self.chunk_size = self.text_processing.get('chunk_size', 1000)
        self.chunk_overlap = self.text_processing.get('chunk_overlap', 200)
        self.min_chunk_size = self.text_processing.get('min_chunk_size', 100)
        self.preserve_structure = self.text_processing.get('preserve_structure', True)
        
        # GDPR article keywords for violation categorization
        self.violation_categories = {
            "Data Subject Rights": ["right to access", "right to erasure", "right to rectification", 
                                    "right to portability", "right to object", "Article 15", "Article 16", 
                                    "Article 17", "Article 18", "Article 20", "Article 21"],
            "Data Processing Principles": ["lawfulness", "fairness", "transparency", "purpose limitation",
                                          "data minimisation", "accuracy", "storage limitation", 
                                          "integrity", "confidentiality", "Article 5"],
            "Legal Basis": ["consent", "contract", "legal obligation", "vital interests", 
                           "public interest", "legitimate interests", "Article 6", "Article 9"],
            "Data Protection Officer": ["DPO", "data protection officer", "Article 37", "Article 38", "Article 39"],
            "Data Breach Notification": ["personal data breach", "breach notification", "Article 33", "Article 34"],
            "Cross-Border Transfer": ["international transfer", "third country", "adequacy decision", 
                                     "standard contractual clauses", "Article 44", "Article 45", "Article 46"],
            "Consent Management": ["freely given", "specific", "informed", "unambiguous", 
                                  "withdrawal of consent", "Article 7"],
            "Privacy by Design": ["data protection by design", "data protection by default", "Article 25"],
            "Records of Processing": ["records of processing activities", "Article 30"],
            "Impact Assessment": ["data protection impact assessment", "DPIA", "Article 35"]
        }
    
    def process_eur_lex_document(self, doc: Dict) -> List[DocumentChunk]:
        """
        Process EUR-Lex GDPR regulation document
        
        Args:
            doc: EUR-Lex document dictionary
        
        Returns:
            List of document chunks
        """
        chunks = []
        
        # Process recitals
        for recital in doc.get('recitals', []):
            if len(recital['content']) >= self.min_chunk_size:
                chunk = DocumentChunk(
                    text=f"Recital ({recital['number']}): {recital['content']}",
                    metadata={
                        "source": doc['source'],
                        "document_type": doc['document_type'],
                        "language": doc.get('language', 'EN'),
                        "structure_type": "recital",
                        "recital_number": recital['number'],
                        "url": doc.get('url', ''),
                        "violation_categories": self._categorize_text(recital['content'])
                    },
                    chunk_id=f"eur_lex_recital_{recital['number']}_{doc.get('language', 'EN')}",
                    source="EUR-Lex",
                    document_type="regulation"
                )
                chunks.append(chunk)
        
        # Process articles
        for article in doc.get('articles', []):
            if len(article['content']) >= self.min_chunk_size:
                # Create chunk with article title and content
                article_text = f"Article {article['number']}"
                if article['title']:
                    article_text += f" - {article['title']}"
                article_text += f"\n\n{article['content']}"
                
                chunk = DocumentChunk(
                    text=article_text,
                    metadata={
                        "source": doc['source'],
                        "document_type": doc['document_type'],
                        "language": doc.get('language', 'EN'),
                        "structure_type": "article",
                        "article_number": article['number'],
                        "article_title": article['title'],
                        "url": doc.get('url', ''),
                        "violation_categories": self._categorize_text(article['content'])
                    },
                    chunk_id=f"eur_lex_article_{article['number']}_{doc.get('language', 'EN')}",
                    source="EUR-Lex",
                    document_type="regulation"
                )
                chunks.append(chunk)
                
                # If article is long, also create sub-chunks
                if len(article['content']) > self.chunk_size * 2:
                    sub_chunks = self._create_overlapping_chunks(
                        article['content'],
                        prefix=f"Article {article['number']} - {article['title']}\n\n"
                    )
                    
                    for i, sub_chunk_text in enumerate(sub_chunks):
                        sub_chunk = DocumentChunk(
                            text=sub_chunk_text,
                            metadata={
                                "source": doc['source'],
                                "document_type": doc['document_type'],
                                "language": doc.get('language', 'EN'),
                                "structure_type": "article_section",
                                "article_number": article['number'],
                                "article_title": article['title'],
                                "section_index": i,
                                "url": doc.get('url', ''),
                                "violation_categories": self._categorize_text(sub_chunk_text)
                            },
                            chunk_id=f"eur_lex_article_{article['number']}_sec_{i}_{doc.get('language', 'EN')}",
                            source="EUR-Lex",
                            document_type="regulation"
                        )
                        chunks.append(sub_chunk)
        
        logger.info(f"Processed EUR-Lex document: {len(chunks)} chunks created")
        return chunks
    
    def process_edpb_document(self, doc: Dict) -> List[DocumentChunk]:
        """
        Process EDPB guideline or document
        
        Args:
            doc: EDPB document dictionary
        
        Returns:
            List of document chunks
        """
        chunks = []
        
        # Process sections
        for i, section in enumerate(doc.get('sections', [])):
            section_text = f"{section['title']}\n\n{section['content']}"
            
            if len(section['content']) < self.chunk_size:
                # Small section - create single chunk
                chunk = DocumentChunk(
                    text=section_text,
                    metadata={
                        "source": doc['source'],
                        "document_type": doc['document_type'],
                        "structure_type": "section",
                        "section_title": section['title'],
                        "section_level": section.get('level', 'h2'),
                        "document_title": doc.get('title', ''),
                        "url": doc.get('url', ''),
                        "violation_categories": self._categorize_text(section['content'])
                    },
                    chunk_id=f"edpb_{doc['document_type']}_{i}",
                    source="EDPB",
                    document_type=doc['document_type']
                )
                chunks.append(chunk)
            else:
                # Large section - create overlapping chunks
                sub_chunks = self._create_overlapping_chunks(
                    section['content'],
                    prefix=f"{section['title']}\n\n"
                )
                
                for j, sub_chunk_text in enumerate(sub_chunks):
                    chunk = DocumentChunk(
                        text=sub_chunk_text,
                        metadata={
                            "source": doc['source'],
                            "document_type": doc['document_type'],
                            "structure_type": "section_part",
                            "section_title": section['title'],
                            "section_level": section.get('level', 'h2'),
                            "section_index": i,
                            "part_index": j,
                            "document_title": doc.get('title', ''),
                            "url": doc.get('url', ''),
                            "violation_categories": self._categorize_text(sub_chunk_text)
                        },
                        chunk_id=f"edpb_{doc['document_type']}_{i}_part_{j}",
                        source="EDPB",
                        document_type=doc['document_type']
                    )
                    chunks.append(chunk)
        
        logger.info(f"Processed EDPB document '{doc.get('title', 'Unknown')}': {len(chunks)} chunks created")
        return chunks
    
    def process_case_law_document(self, doc: Dict) -> List[DocumentChunk]:
        """
        Process case law document
        
        Args:
            doc: Case law document dictionary
        
        Returns:
            List of document chunks
        """
        chunks = []
        
        # Extract case details
        case_details = doc.get('case_details', {})
        
        # Create chunk from case summary/facts
        for i, section in enumerate(doc.get('sections', [])):
            if len(section['content']) >= self.min_chunk_size:
                section_text = f"Case: {doc.get('title', '')}\n{section['title']}\n\n{section['content']}"
                
                if len(section['content']) < self.chunk_size:
                    chunk = DocumentChunk(
                        text=section_text,
                        metadata={
                            "source": doc['source'],
                            "document_type": doc['document_type'],
                            "structure_type": "case_section",
                            "case_title": doc.get('title', ''),
                            "section_title": section['title'],
                            "section_level": section.get('level', 'h2'),
                            "url": doc.get('url', ''),
                            "case_details": case_details,
                            "violation_categories": self._categorize_text(section['content'])
                        },
                        chunk_id=f"case_{doc.get('pageid', '')}_{i}",
                        source=doc['source'],
                        document_type="case_law"
                    )
                    chunks.append(chunk)
                else:
                    # Large section - create overlapping chunks
                    sub_chunks = self._create_overlapping_chunks(
                        section['content'],
                        prefix=f"Case: {doc.get('title', '')}\n{section['title']}\n\n"
                    )
                    
                    for j, sub_chunk_text in enumerate(sub_chunks):
                        chunk = DocumentChunk(
                            text=sub_chunk_text,
                            metadata={
                                "source": doc['source'],
                                "document_type": doc['document_type'],
                                "structure_type": "case_section_part",
                                "case_title": doc.get('title', ''),
                                "section_title": section['title'],
                                "section_level": section.get('level', 'h2'),
                                "section_index": i,
                                "part_index": j,
                                "url": doc.get('url', ''),
                                "case_details": case_details,
                                "violation_categories": self._categorize_text(sub_chunk_text)
                            },
                            chunk_id=f"case_{doc.get('pageid', '')}_{i}_part_{j}",
                            source=doc['source'],
                            document_type="case_law"
                        )
                        chunks.append(chunk)
        
        logger.info(f"Processed case law '{doc.get('title', 'Unknown')}': {len(chunks)} chunks created")
        return chunks
    
    def _create_overlapping_chunks(self, text: str, prefix: str = "") -> List[str]:
        """
        Create overlapping chunks from text
        
        Args:
            text: Text to chunk
            prefix: Prefix to add to each chunk (e.g., section title)
        
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Split by sentences for better chunking
        sentences = self._split_into_sentences(text)
        
        current_chunk = []
        current_length = len(prefix)
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = prefix + " ".join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap
                overlap_text = " ".join(current_chunk[-3:])  # Last 3 sentences for context
                current_chunk = current_chunk[-3:] if len(current_chunk) >= 3 else current_chunk
                current_length = len(prefix) + len(overlap_text)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = prefix + " ".join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(chunk_text)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences with improved handling for legal text"""
        # Enhanced sentence splitting that handles common legal text patterns
        # Handle abbreviations like "Art.", "No.", "e.g.", "i.e."
        text = re.sub(r'\b(Art|No|e\.g|i\.e)\.\s', r'\1PLACEHOLDER ', text)
        
        # Split on sentence boundaries (period/question/exclamation followed by space and capital)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z(])', text)
        
        # Restore abbreviations
        sentences = [s.replace('PLACEHOLDER', '.') for s in sentences]
        
        # Filter out very short sentences (likely fragments)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _categorize_text(self, text: str) -> List[str]:
        """
        Categorize text based on GDPR violation categories
        
        Args:
            text: Text to categorize
        
        Returns:
            List of applicable violation categories
        """
        text_lower = text.lower()
        categories = []
        
        for category, keywords in self.violation_categories.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    categories.append(category)
                    break
        
        return list(set(categories))  # Remove duplicates
    
    def process_all_documents(self, raw_data_dir: str = "data/raw") -> List[DocumentChunk]:
        """
        Process all collected documents
        
        Args:
            raw_data_dir: Directory containing raw collected data
        
        Returns:
            List of all document chunks
        """
        all_chunks = []
        raw_path = Path(raw_data_dir)
        
        logger.info("Processing all collected documents...")
        
        # Process EUR-Lex documents
        eur_lex_dir = raw_path / "eur_lex"
        if eur_lex_dir.exists():
            for json_file in eur_lex_dir.glob("*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                chunks = self.process_eur_lex_document(doc)
                all_chunks.extend(chunks)
        
        # Process EDPB documents
        edpb_dir = raw_path / "edpb"
        if edpb_dir.exists():
            for json_file in edpb_dir.glob("*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                chunks = self.process_edpb_document(doc)
                all_chunks.extend(chunks)
        
        # Process case law
        gdprhub_dir = raw_path / "gdprhub"
        if gdprhub_dir.exists():
            for json_file in gdprhub_dir.glob("case_*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                chunks = self.process_case_law_document(doc)
                all_chunks.extend(chunks)
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        
        # Save processed chunks
        self._save_chunks(all_chunks)
        
        return all_chunks
    
    def _save_chunks(self, chunks: List[DocumentChunk]):
        """Save processed chunks to disk"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save all chunks
        output_file = output_dir / "all_chunks.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([chunk.to_dict() for chunk in chunks], f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(chunks)} chunks to {output_file}")
        
        # Save summary
        summary = {
            "total_chunks": len(chunks),
            "by_source": {},
            "by_type": {},
            "by_category": {}
        }
        
        for chunk in chunks:
            # Count by source
            source = chunk.source
            summary["by_source"][source] = summary["by_source"].get(source, 0) + 1
            
            # Count by document type
            doc_type = chunk.document_type
            summary["by_type"][doc_type] = summary["by_type"].get(doc_type, 0) + 1
            
            # Count by violation categories
            for category in chunk.metadata.get('violation_categories', []):
                summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        summary_file = output_dir / "processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved processing summary to {summary_file}")


if __name__ == "__main__":
    import yaml
    
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    processor = GDPRDocumentProcessor(config)
    processor.process_all_documents()
