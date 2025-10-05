"""
Quick test script to verify system functionality
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

import yaml
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")

print("\n" + "="*80)
print("GDPR RAG System - Quick Test")
print("="*80 + "\n")

# Test 1: Load configuration
print("Test 1: Loading configuration...")
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print("✓ Configuration loaded successfully")
    print(f"  - Ollama model: {config['ollama']['model']}")
    print(f"  - Embedding model: {config['embeddings']['model_name']}")
except Exception as e:
    print(f"✗ Error loading config: {e}")
    sys.exit(1)

# Test 2: Test EUR-Lex collector (just fetch English GDPR)
print("\nTest 2: Testing data collection (EUR-Lex GDPR - English only)...")
try:
    from data_collection.eur_lex_collector import EURLexCollector
    
    collector = EURLexCollector()
    doc = collector.fetch_gdpr_text("EN")
    
    if doc:
        print("✓ Successfully fetched GDPR text")
        print(f"  - Articles: {len(doc.get('articles', []))}")
        print(f"  - Recitals: {len(doc.get('recitals', []))}")
        print(f"  - Word count: {doc['metadata']['word_count']}")
    else:
        print("✗ Failed to fetch GDPR text")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error in data collection: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test document processing
print("\nTest 3: Testing document processing...")
try:
    from preprocessing.document_processor import GDPRDocumentProcessor
    import json
    
    processor = GDPRDocumentProcessor(config)
    chunks = processor.process_eur_lex_document(doc)
    
    print(f"✓ Successfully processed document")
    print(f"  - Total chunks: {len(chunks)}")
    print(f"  - Sample chunk text (first 100 chars): {chunks[0].text[:100]}...")
    
    # Save for next test
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "test_chunks.json", 'w', encoding='utf-8') as f:
        json.dump([chunk.to_dict() for chunk in chunks], f, ensure_ascii=False, indent=2)
    
except Exception as e:
    print(f"✗ Error in processing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test FAISS vector store
print("\nTest 4: Testing FAISS vector store...")
try:
    from vectorstore.faiss_store import FAISSVectorStore
    
    vector_store = FAISSVectorStore(config)
    vector_store.build_index_from_chunks([chunk.to_dict() for chunk in chunks[:100]])  # Test with first 100
    
    print(f"✓ Successfully built FAISS index")
    print(f"  - Total vectors: {vector_store.index.ntotal}")
    
    # Test search
    results = vector_store.search("What are data subject rights?", top_k=3)
    print(f"  - Test search returned {len(results)} results")
    if results:
        print(f"  - Top result score: {results[0]['score']:.3f}")
    
    # Save index
    vector_store.save_index(Path("vectorstore/test_index"))
    print("  - Index saved successfully")
    
except Exception as e:
    print(f"✗ Error in vector store: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test Ollama connection
print("\nTest 5: Testing Ollama connection...")
try:
    import ollama
    
    response = ollama.chat(
        model=config['ollama']['model'],
        messages=[{'role': 'user', 'content': 'Say "Hello, GDPR RAG system is working!"'}]
    )
    
    print("✓ Ollama connection successful")
    print(f"  - Model: {config['ollama']['model']}")
    print(f"  - Response: {response['message']['content'][:100]}...")
    
except Exception as e:
    print(f"✗ Error connecting to Ollama: {e}")
    print("  Make sure Ollama is running with: ollama serve")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test RAG system
print("\nTest 6: Testing RAG system...")
try:
    from rag.gdpr_rag import GDPRRAGSystem
    
    # Load the test index we just created
    rag = GDPRRAGSystem(config)
    rag.vector_store.load_index(Path("vectorstore/test_index"))
    
    query = "What are the main principles of GDPR?"
    result = rag.query(query, top_k=2)
    
    print("✓ RAG system working")
    print(f"  - Query: {query}")
    print(f"  - Answer (first 150 chars): {result['answer'][:150]}...")
    print(f"  - Sources retrieved: {len(result.get('sources', []))}")
    
except Exception as e:
    print(f"✗ Error in RAG system: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test violation finder
print("\nTest 7: Testing violation finder...")
try:
    from violation_finder.violation_finder import GDPRViolationFinder
    
    finder = GDPRViolationFinder(config)
    finder.rag_system.vector_store.load_index(Path("vectorstore/test_index"))
    
    scenario = "We collect user emails without consent for marketing purposes."
    assessment = finder.analyze_scenario(scenario)
    
    print("✓ Violation finder working")
    print(f"  - Risk level: {assessment.overall_risk_level}")
    print(f"  - Risk score: {assessment.risk_score:.1f}/10")
    print(f"  - Violations found: {len(assessment.violations)}")
    
except Exception as e:
    print(f"✗ Error in violation finder: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("ALL TESTS PASSED! ✓")
print("="*80)
print("\nThe system is ready to use!")
print("\nNext steps:")
print("1. Run full data collection: python main.py collect")
print("2. Process all documents: python main.py process")  
print("3. Build complete vector store: python main.py build")
print("4. Start using: python main.py interactive")
