"""
Main entry point for GDPR Compliance RAG System
Provides CLI interface and workflow orchestration
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

import argparse
import yaml
from loguru import logger

from utils import load_config, setup_logging, ensure_directories
from data_collection.orchestrator import DataCollectionOrchestrator
from preprocessing.document_processor import GDPRDocumentProcessor
from vectorstore.faiss_store import FAISSVectorStore
from rag.gdpr_rag import GDPRRAGSystem
from violation_finder.violation_finder import GDPRViolationFinder


def setup_system(config_path: str = "config.yaml"):
    """Initialize the system with configuration"""
    config = load_config(config_path)
    setup_logging(config)
    ensure_directories()
    return config


def collect_data(config):
    """Run data collection from all sources"""
    logger.info("Starting data collection...")
    orchestrator = DataCollectionOrchestrator(config)
    results = orchestrator.collect_all()
    logger.info(f"Data collection complete. Collected from {len(results)} sources")
    return results


def process_documents(config):
    """Process collected documents into chunks"""
    logger.info("Starting document processing...")
    processor = GDPRDocumentProcessor(config)
    chunks = processor.process_all_documents()
    logger.info(f"Document processing complete. Created {len(chunks)} chunks")
    return chunks


def build_vectorstore(config):
    """Build FAISS vector store from processed chunks"""
    logger.info("Building vector store...")
    
    # Load processed chunks
    import json
    chunks_file = Path("data/processed/all_chunks.json")
    
    if not chunks_file.exists():
        logger.error("Processed chunks not found. Run 'process' command first.")
        return False
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Build vector store
    vector_store = FAISSVectorStore(config)
    vector_store.build_index_from_chunks(chunks)
    vector_store.save_index()
    
    # Print statistics
    stats = vector_store.get_statistics()
    logger.info(f"Vector store built successfully:")
    logger.info(f"  Total vectors: {stats['total_vectors']}")
    logger.info(f"  Sources: {list(stats['sources'].keys())}")
    logger.info(f"  Document types: {list(stats['document_types'].keys())}")
    
    return True


def run_query(config, query: str, top_k: int = 5):
    """Run a single query against the RAG system"""
    logger.info(f"Processing query: {query}")
    
    rag = GDPRRAGSystem(config)
    result = rag.query(query, top_k=top_k)
    
    print("\n" + "="*80)
    print(f"Query: {query}")
    print("="*80)
    print(f"\nAnswer:\n{result['answer']}\n")
    
    if result.get('sources'):
        print(f"\nSources ({len(result['sources'])}):")
        for i, source in enumerate(result['sources'], 1):
            print(f"\n{i}. {source['source']} - {source['document_type']}")
            if source.get('article_number'):
                print(f"   Article {source['article_number']}")
            print(f"   Score: {source['score']:.3f}")
            print(f"   {source['text'][:200]}...")
    
    print("\n" + "="*80 + "\n")


def analyze_violation(config, scenario: str, output_file: str = None):
    """Analyze a scenario for GDPR violations"""
    logger.info("Analyzing scenario for violations...")
    
    finder = GDPRViolationFinder(config)
    assessment = finder.analyze_scenario(scenario)
    
    # Generate report
    report = finder.generate_compliance_report(scenario, assessment, format="markdown")
    
    print(report)
    
    # Save report if output file specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {output_file}")


def run_interactive(config):
    """Run interactive Q&A session"""
    rag = GDPRRAGSystem(config)
    
    print("\n" + "="*80)
    print("GDPR Compliance RAG System - Interactive Mode")
    print("="*80)
    print("\nAsk questions about GDPR compliance. Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            result = rag.query(query)
            print(f"\nAnswer:\n{result['answer']}\n")
            
            if result.get('sources'):
                print(f"Based on {len(result['sources'])} sources")
                show_sources = input("Show sources? (y/n): ").strip().lower()
                
                if show_sources == 'y':
                    for i, source in enumerate(result['sources'], 1):
                        print(f"\n{i}. {source['source']} - {source['document_type']}")
                        if source.get('article_number'):
                            print(f"   Article {source['article_number']}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="GDPR Compliance RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build the complete system from scratch
  python main.py setup
  
  # Run a single query
  python main.py query "What are data subject rights under GDPR?"
  
  # Analyze a scenario for violations
  python main.py analyze --scenario "We collect user data without consent"
  
  # Run interactive mode
  python main.py interactive
        """
    )
    
    parser.add_argument(
        'command',
        choices=['setup', 'collect', 'process', 'build', 'query', 'analyze', 'interactive'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--query',
        help='Query string (for query command)'
    )
    
    parser.add_argument(
        '--scenario',
        help='Scenario description (for analyze command)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path (for analyze command)'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of results to retrieve (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = setup_system(args.config)
    
    try:
        if args.command == 'setup':
            logger.info("Running complete system setup...")
            collect_data(config)
            process_documents(config)
            build_vectorstore(config)
            logger.info("System setup complete!")
            
        elif args.command == 'collect':
            collect_data(config)
            
        elif args.command == 'process':
            process_documents(config)
            
        elif args.command == 'build':
            build_vectorstore(config)
            
        elif args.command == 'query':
            if not args.query:
                logger.error("Please provide a query with --query")
                return
            run_query(config, args.query, args.top_k)
            
        elif args.command == 'analyze':
            if not args.scenario:
                logger.error("Please provide a scenario with --scenario")
                return
            analyze_violation(config, args.scenario, args.output)
            
        elif args.command == 'interactive':
            run_interactive(config)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise


if __name__ == "__main__":
    main()
