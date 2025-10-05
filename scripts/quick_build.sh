#!/bin/bash
# Quick Start - Build the GDPR Database

echo "🚀 GDPR RAG System - Quick Database Build"
echo "=========================================="
echo ""

cd "/home/ubuntu-beond/gdpr compliance/GDPR-compliance-RAG"
source venv/bin/activate

echo "This will:"
echo "  1. Collect GDPR data from EUR-Lex (English)"
echo "  2. Process into optimized chunks"
echo "  3. Build searchable FAISS vector store"
echo ""
echo "Estimated time: 5-10 minutes for quick build"
echo ""
read -p "Press Enter to continue..."

# Quick build: English GDPR only
echo ""
echo "📥 Step 1/3: Collecting GDPR text (English only)..."
python main.py collect --sources eur-lex --languages EN

echo ""
echo "⚙️  Step 2/3: Processing documents..."
python main.py process

echo ""
echo "🔨 Step 3/3: Building vector store..."
python main.py build

echo ""
echo "✅ Quick database build complete!"
echo ""
echo "Try it now:"
echo "  python main.py query --query 'What are data subject rights?'"
echo "  python main.py interactive"
echo ""
