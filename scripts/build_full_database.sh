#!/bin/bash
# Full System Build Script

echo "=================================="
echo "GDPR RAG - Full Database Build"
echo "=================================="
echo ""

cd /home/ubuntu-beond/gdpr\ compliance/GDPR-compliance-RAG
source venv/bin/activate

# Step 1: Collect all data sources
echo "Step 1/3: Collecting data from all sources..."
echo "  - EUR-Lex (GDPR in 10+ languages)"
echo "  - EDPB Guidelines"
echo "  - GDPRhub Case Law"
echo "  Estimated time: 15-30 minutes"
echo ""
python main.py collect --sources all

echo ""
echo "Step 2/3: Processing documents into optimized chunks..."
echo "  - Smart chunking with overlap"
echo "  - Violation categorization"
echo "  - Metadata enrichment"
echo "  Estimated time: 5-10 minutes"
echo ""
python main.py process

echo ""
echo "Step 3/3: Building FAISS vector store..."
echo "  - Creating embeddings"
echo "  - Building HNSW index"
echo "  - Optimizing for fast retrieval"
echo "  Estimated time: 10-15 minutes"
echo ""
python main.py build

echo ""
echo "=================================="
echo "✅ Build Complete!"
echo "=================================="
echo ""
echo "Your GDPR database is ready. Start using:"
echo "  python main.py interactive"
echo ""
