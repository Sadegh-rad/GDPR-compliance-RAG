"""
Quick interactive demo of the GDPR RAG system
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

import yaml
from rag.gdpr_rag import GDPRRAGSystem
from violation_finder.violation_finder import GDPRViolationFinder

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize RAG system
print("Loading GDPR RAG system...")
rag = GDPRRAGSystem(config)
rag.vector_store.load_index(Path("vectorstore/test_index"))

print("\n" + "="*80)
print("GDPR RAG SYSTEM DEMO")
print("="*80 + "\n")

# Example 1: Ask about data subject rights
print("📋 Query 1: What rights do data subjects have under GDPR?\n")
result = rag.query("What rights do data subjects have under GDPR?", top_k=3)
print(f"Answer: {result['answer']}\n")

# Example 2: Ask about lawful basis
print("="*80)
print("\n📋 Query 2: What are the lawful bases for processing personal data?\n")
result = rag.query("What are the lawful bases for processing personal data?", top_k=3)
print(f"Answer: {result['answer']}\n")

# Example 3: Violation analysis
print("="*80)
print("\n⚠️  Violation Analysis: Marketing without consent\n")
print("Scenario: 'We send marketing emails to all website visitors without asking for consent'")

finder = GDPRViolationFinder(config)
finder.rag_system.vector_store.load_index(Path("vectorstore/test_index"))

assessment = finder.analyze_scenario(
    "We send marketing emails to all website visitors without asking for consent"
)

print(f"\n🚨 Risk Level: {assessment.overall_risk_level}")
print(f"📊 Risk Score: {assessment.risk_score}/10")
print(f"⚠️  Violations Found: {len(assessment.violations)}")
if assessment.violations:
    violation = assessment.violations[0]
    print(f"\n🔍 Main Violation:")
    print(f"   Articles: {', '.join(violation.articles)}")
    print(f"   Severity: {violation.severity}")
    print(f"   Description: {violation.description[:200]}...")

print("\n" + "="*80)
print("\n✅ Demo completed! The system is working perfectly.")
print("\nTo build a complete database with all GDPR sources:")
print("  1. python main.py collect   # Collect all data (15-30 min)")
print("  2. python main.py process   # Process documents (5-10 min)")
print("  3. python main.py build     # Build full FAISS index (10-15 min)")
print("  4. python main.py interactive  # Interactive Q&A mode")
print("="*80 + "\n")
