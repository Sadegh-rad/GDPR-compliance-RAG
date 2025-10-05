#!/bin/bash
# Rebuild database with improved quality settings

echo "🔄 GDPR RAG - Rebuilding with Quality Improvements"
echo "=================================================="
echo ""

cd "/home/ubuntu-beond/gdpr compliance/GDPR-compliance-RAG"
source venv/bin/activate

echo "Improvements applied:"
echo "  ✓ Switched to gpt-oss:latest model (higher quality)"
echo "  ✓ Upgraded embeddings to all-mpnet-base-v2 (768-dim, more accurate)"
echo "  ✓ Optimized chunk size: 800 chars with 150 overlap"
echo "  ✓ Enhanced sentence splitting for legal text"
echo "  ✓ Improved prompts with detailed instructions"
echo "  ✓ Increased context window: 8192 tokens"
echo "  ✓ Better retrieval: top_k=7, threshold=0.45"
echo ""
echo "This will rebuild the vector store with better quality."
echo "Estimated time: 2-3 minutes"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "⚙️  Step 1/2: Re-processing documents with improved chunking..."
python -c "
import sys
from pathlib import Path
sys.path.append(str(Path.cwd() / 'src'))

import yaml
import json
from preprocessing.document_processor import GDPRDocumentProcessor

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Load collected data
data_file = Path('data/raw/eur_lex/gdpr_en.json')
with open(data_file, 'r', encoding='utf-8') as f:
    doc = json.load(f)

# Process with new settings
processor = GDPRDocumentProcessor(config)
chunks = processor.process_eur_lex_document(doc)

print(f'✓ Created {len(chunks)} improved chunks')

# Save
output_file = Path('data/processed/gdpr_chunks_improved.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump([chunk.to_dict() for chunk in chunks], f, ensure_ascii=False, indent=2)

print(f'✓ Saved to: {output_file}')
"

echo ""
echo "🔨 Step 2/2: Building improved vector store..."
python -c "
import sys
from pathlib import Path
sys.path.append(str(Path.cwd() / 'src'))

import yaml
import json
from vectorstore.faiss_store import FAISSVectorStore

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Load improved chunks
chunks_file = Path('data/processed/gdpr_chunks_improved.json')
with open(chunks_file, 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f'Building with {len(chunks)} chunks...')
print('Using higher quality embeddings (all-mpnet-base-v2, 768-dim)...')

# Build vector store
vector_store = FAISSVectorStore(config)
vector_store.build_index_from_chunks(chunks)

# Save
index_path = Path('vectorstore/gdpr_faiss_index')
vector_store.save_index(index_path)

print(f'✓ Improved vector store built: {vector_store.index.ntotal} vectors')
print(f'✓ Embedding dimension: {vector_store.embedding_model.get_sentence_embedding_dimension()}')
"

echo ""
echo "✅ Rebuild complete with quality improvements!"
echo ""
echo "Test the improved system:"
echo "  python main.py query --query 'What are data subject rights?'"
echo ""
