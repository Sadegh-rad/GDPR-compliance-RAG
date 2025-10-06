#!/usr/bin/env python3
"""Test script to check article numbers in the vector store and create accurate PDF mapping"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.gdpr_rag import GDPRRAG

# Initialize
print("Loading GDPR system...")
rag = GDPRRAG()

# Check what article numbers we have
article_numbers = set()
for metadata in rag.vector_store.metadata:
    if 'article_number' in metadata and metadata['article_number']:
        article_numbers.add(metadata['article_number'])

print(f"\nFound {len(article_numbers)} unique articles in database:")
print(sorted(article_numbers))

# Show sample of Article 6 to verify
print("\n" + "="*80)
print("Sample chunks from Article 6:")
print("="*80)
for idx, metadata in enumerate(rag.vector_store.metadata[:50]):
    if metadata.get('article_number') == 6:
        text = rag.vector_store.texts[idx]
        print(f"\nChunk {metadata.get('chunk_index', '?')}:")
        print(f"Text preview: {text[:200]}...")
        print(f"Metadata: {metadata}")

print("\n" + "="*80)
print("Creating PDF page mapping based on EUR-Lex official PDF...")
print("="*80)
print("Official EUR-Lex PDF structure:")
print("- Recitals: Pages 1-31")
print("- Article 1 'Subject-matter and objectives': Page 32")
print("- Article 2 'Material scope': Page 33") 
print("- Article 3 'Territorial scope': Page 33-34")
print("- Article 4 'Definitions': Page 34-35")
print("- Article 5 'Principles relating to processing': Page 35-36")
print("- Article 6 'Lawfulness of processing': Page 36-38")
print("- Article 7 'Conditions for consent': Page 38-39")
print("\nAll articles start from page 32 onwards")
