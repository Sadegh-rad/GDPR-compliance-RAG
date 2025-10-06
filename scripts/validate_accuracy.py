#!/usr/bin/env python3
"""
Comprehensive Accuracy Validation Script
Tests system-wide accuracy against 80%+ target
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.violation_finder.violation_finder import GDPRViolationFinder
from src.config import load_config
import time

def test_scenario(finder, name, scenario, expected_articles):
    """Test a scenario and return accuracy metrics"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    print(f"Scenario: {scenario[:100]}...")
    print(f"Expected Articles: {expected_articles}")
    
    start = time.time()
    result = finder.analyze_scenario(scenario)
    elapsed = time.time() - start
    
    # Extract found articles
    found_articles = set()
    for violation in result.violations:
        found_articles.update(violation.articles)
    
    # Calculate accuracy metrics
    total_citations = sum(len(v.source_citations or []) for v in result.violations)
    if total_citations > 0:
        avg_relevance = sum(
            c.relevance_score 
            for v in result.violations 
            if v.source_citations
            for c in v.source_citations
        ) / total_citations
    else:
        avg_relevance = 0.0
    
    # Check article accuracy
    expected_set = set(expected_articles)
    found_set = found_articles
    
    correct = len(expected_set & found_set)
    missed = len(expected_set - found_set)
    wrong = len(found_set - expected_set)
    
    article_accuracy = correct / len(expected_set) if expected_set else 0.0
    
    print(f"\n📊 RESULTS:")
    print(f"  ⏱️  Time: {elapsed:.1f}s")
    print(f"  📚 Citations: {total_citations}")
    print(f"  🎯 Avg Relevance: {avg_relevance:.1%}")
    print(f"  ✅ Articles Correct: {correct}/{len(expected_set)} ({article_accuracy:.1%})")
    if missed:
        print(f"  ❌ Articles Missed: {missed} ({expected_set - found_set})")
    if wrong:
        print(f"  ⚠️  Extra Articles: {wrong} ({found_set - expected_set})")
    
    return {
        'name': name,
        'time': elapsed,
        'citations': total_citations,
        'avg_relevance': avg_relevance,
        'article_accuracy': article_accuracy,
        'correct': correct,
        'total_expected': len(expected_set),
        'missed': missed,
        'wrong': wrong
    }

def main():
    print("="*80)
    print("COMPREHENSIVE ACCURACY VALIDATION")
    print("Target: 80%+ relevance accuracy")
    print("="*80)
    
    config = load_config()
    finder = GDPRViolationFinder(config)
    
    # Test scenarios with known correct articles
    scenarios = [
        {
            'name': 'No Consent for Marketing',
            'scenario': '''
Our company collects email addresses from website visitors without asking for consent.
We use these emails for marketing and share them with advertisers.
Users cannot delete their data.
            ''',
            'expected_articles': ['Article 6', 'Article 7', 'Article 17']
        },
        {
            'name': 'International Data Transfer',
            'scenario': '''
We transfer customer data to our servers in a non-EU country without any safeguards.
Customers are not informed about this transfer.
            ''',
            'expected_articles': ['Article 44', 'Article 45', 'Article 46', 'Article 13']
        },
        {
            'name': 'No Privacy Policy',
            'scenario': '''
Our website collects personal data but has no privacy policy.
Users don't know what data we collect or how we use it.
We also don't have a data protection officer.
            ''',
            'expected_articles': ['Article 13', 'Article 14', 'Article 37']
        },
        {
            'name': 'Data Breach Not Reported',
            'scenario': '''
We discovered a data breach 2 months ago where customer passwords were exposed.
We haven't notified the supervisory authority or affected users.
            ''',
            'expected_articles': ['Article 33', 'Article 34']
        }
    ]
    
    results = []
    for test in scenarios:
        result = test_scenario(
            finder,
            test['name'],
            test['scenario'],
            test['expected_articles']
        )
        results.append(result)
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY - SYSTEM-WIDE ACCURACY")
    print(f"{'='*80}")
    
    total_time = sum(r['time'] for r in results)
    avg_relevance = sum(r['avg_relevance'] for r in results) / len(results)
    avg_article_accuracy = sum(r['article_accuracy'] for r in results) / len(results)
    total_correct = sum(r['correct'] for r in results)
    total_expected = sum(r['total_expected'] for r in results)
    total_missed = sum(r['missed'] for r in results)
    total_wrong = sum(r['wrong'] for r in results)
    
    print(f"\n⏱️  PERFORMANCE:")
    print(f"  Total Time: {total_time:.1f}s")
    print(f"  Avg Time per Test: {total_time/len(results):.1f}s")
    
    print(f"\n🎯 RELEVANCE ACCURACY (Target: 80%+):")
    print(f"  Average Citation Relevance: {avg_relevance:.1%}")
    if avg_relevance >= 0.80:
        print(f"  ✅ TARGET MET! Exceeds 80% threshold")
    elif avg_relevance >= 0.70:
        print(f"  ⚠️  CLOSE: {80 - avg_relevance*100:.1f}% below target")
    else:
        print(f"  ❌ BELOW TARGET: {80 - avg_relevance*100:.1f}% improvement needed")
    
    print(f"\n📋 ARTICLE DETECTION ACCURACY:")
    print(f"  Articles Correctly Identified: {total_correct}/{total_expected} ({avg_article_accuracy:.1%})")
    print(f"  Articles Missed: {total_missed}")
    print(f"  False Positives: {total_wrong}")
    
    print(f"\n{'='*80}")
    print("DETAILED RESULTS:")
    print(f"{'='*80}")
    for r in results:
        status = "✅" if r['avg_relevance'] >= 0.80 else "⚠️" if r['avg_relevance'] >= 0.70 else "❌"
        print(f"{status} {r['name']}: Relevance {r['avg_relevance']:.1%}, Articles {r['correct']}/{r['total_expected']}, Time {r['time']:.1f}s")
    
    print(f"\n{'='*80}")
    print("QUALITY ASSESSMENT:")
    print(f"{'='*80}")
    
    # Overall quality rating
    quality_score = (avg_relevance * 0.6 + avg_article_accuracy * 0.4)
    
    if quality_score >= 0.85:
        rating = "EXCELLENT"
        symbol = "🌟"
    elif quality_score >= 0.75:
        rating = "GOOD"
        symbol = "✅"
    elif quality_score >= 0.65:
        rating = "ACCEPTABLE"
        symbol = "⚠️"
    else:
        rating = "NEEDS IMPROVEMENT"
        symbol = "❌"
    
    print(f"\n{symbol} Overall Quality Score: {quality_score:.1%} - {rating}")
    print(f"\nDatabase Quality: 2693 vectors, 768-dim embeddings")
    print(f"Reranking: {'Enabled ✓' if config.get('retrieval', {}).get('rerank') else 'Disabled'}")
    print(f"Chunking: {config.get('text_processing', {}).get('chunk_size', 800)} size, {config.get('text_processing', {}).get('chunk_overlap', 150)} overlap")
    
    print(f"\n{'='*80}")

if __name__ == '__main__':
    main()
