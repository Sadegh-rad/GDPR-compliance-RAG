#!/usr/bin/env python3
"""
Quick Test for Enhanced Violation Detection
Fast test with simplified scenario
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from src.violation_finder.violation_finder import GDPRViolationFinder
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | {message}")


def main():
    """Run quick test"""
    print("\n" + "="*80)
    print("QUICK TEST: Enhanced Violation Detection")
    print("="*80 + "\n")
    
    start_time = time.time()
    
    # Load config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize violation finder
    print("🔧 Initializing system...")
    finder = GDPRViolationFinder(config)
    init_time = time.time() - start_time
    print(f"✅ Initialized in {init_time:.2f}s\n")
    
    # Simple test scenario
    scenario = """
    Our company collects email addresses from website visitors without asking for consent.
    We use these emails for marketing and share them with advertisers.
    Users cannot delete their data.
    """
    
    print("📄 SCENARIO:")
    print(scenario)
    print("\n" + "-"*80 + "\n")
    
    # Analyze
    print("🔍 Analyzing...\n")
    analysis_start = time.time()
    assessment = finder.analyze_scenario(scenario)
    analysis_time = time.time() - analysis_start
    
    print(f"✅ Analysis completed in {analysis_time:.2f}s\n")
    print("="*80 + "\n")
    
    # Show results
    print(f"📊 RESULTS:")
    print(f"   Risk Level: {assessment.overall_risk_level} ({assessment.risk_score:.1f}/10)")
    print(f"   Violations Found: {len(assessment.violations)}\n")
    
    for i, v in enumerate(assessment.violations, 1):
        print(f"\n{i}. {v.category} [{v.severity}]")
        print(f"   Description: {v.description}")
        
        if v.highlighted_text:
            print(f"   🔴 Problematic: \"{v.highlighted_text[:60]}...\"")
        
        if v.source_citations:
            print(f"   📚 Citations:")
            for cit in v.source_citations[:2]:  # Show first 2
                print(f"      - {cit.article_or_recital} ({cit.relevance_score:.0%} relevant)")
        
        print(f"   ✓ Recommendation: {v.recommendation[:80]}...")
    
    # Generate report
    print("\n" + "="*80)
    print("📄 GENERATING REPORT...")
    print("="*80 + "\n")
    
    report_start = time.time()
    report = finder.generate_compliance_report(scenario, assessment, format="markdown")
    report_time = time.time() - report_start
    
    # Save report
    output_path = Path("logs/quick_test_report.md")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report generated in {report_time:.2f}s")
    print(f"📁 Saved to: {output_path}\n")
    
    # Total time
    total_time = time.time() - start_time
    print("="*80)
    print(f"⏱️  TOTAL TIME: {total_time:.2f}s")
    print("="*80 + "\n")
    
    if total_time < 60:
        print("✅ Performance: GOOD (under 1 minute)")
    elif total_time < 120:
        print("⚠️  Performance: ACCEPTABLE (1-2 minutes)")
    else:
        print("❌ Performance: SLOW (over 2 minutes)")
    
    print()


if __name__ == "__main__":
    main()
