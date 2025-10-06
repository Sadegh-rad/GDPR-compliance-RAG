#!/usr/bin/env python3
"""
Test Enhanced Violation Detection with Source Citations
Demonstrates:
1. Highlighted problematic text from user documents
2. Exact GDPR article/recital citations with quotes
3. Source context and verification information
4. Professional compliance reports
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from src.violation_finder.violation_finder import GDPRViolationFinder
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def test_scenario_analysis():
    """Test scenario analysis with enhanced citations"""
    print("\n" + "="*100)
    print("TEST 1: Scenario Analysis with Enhanced Citations")
    print("="*100 + "\n")
    
    # Load config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize violation finder
    finder = GDPRViolationFinder(config)
    
    # Example scenario with clear violations
    scenario = """
    Our mobile app collects the following data from users without any consent mechanism:
    - Email addresses and phone numbers
    - Location data tracked 24/7 in the background
    - Browsing history and app usage patterns
    - Contact lists from users' phones
    
    We share this data with third-party advertisers and data brokers.
    We don't have a privacy policy accessible in the app.
    Users cannot delete their data or request information about processing.
    We store all data indefinitely on servers in the US with no security measures.
    """
    
    print("📄 SCENARIO:")
    print(scenario)
    print("\n" + "-"*100 + "\n")
    
    # Analyze scenario
    print("🔍 Analyzing for GDPR violations...\n")
    assessment = finder.analyze_scenario(scenario)
    
    # Generate report
    report = finder.generate_compliance_report(scenario, assessment, format="markdown")
    
    # Print report
    print(report)
    
    # Save report
    output_path = Path("logs/enhanced_violation_report.md")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {output_path}")
    
    # Also save JSON version
    json_report = finder.generate_compliance_report(scenario, assessment, format="json")
    json_path = Path("logs/enhanced_violation_report.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_report)
    
    print(f"✅ JSON report saved to: {json_path}")
    
    return assessment


def test_document_analysis():
    """Test document analysis with text highlighting"""
    print("\n" + "="*100)
    print("TEST 2: Document Analysis with Text Highlighting")
    print("="*100 + "\n")
    
    # Load config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize violation finder
    finder = GDPRViolationFinder(config)
    
    # Sample privacy policy with issues
    privacy_policy = """
    Privacy Policy - MyCoolApp
    
    By using our app, you agree to let us collect any information we want.
    
    We collect your personal information including your name, email, phone number, location, 
    and we track everything you do in the app. We also access your camera and microphone whenever we want.
    
    We share your data with our partners, advertisers, and anyone who pays us for it.
    
    You cannot delete your account or your data. Once you sign up, we keep it forever.
    
    We may update this policy at any time without telling you.
    
    If you don't like it, don't use our app.
    """
    
    print("📄 DOCUMENT TO ANALYZE (Privacy Policy):")
    print(privacy_policy)
    print("\n" + "-"*100 + "\n")
    
    # Analyze document
    print("🔍 Analyzing privacy policy for GDPR violations...\n")
    assessment = finder.analyze_document(privacy_policy, document_type="privacy_policy")
    
    # Generate report
    report = finder.generate_compliance_report(privacy_policy, assessment, format="markdown")
    
    # Print report
    print(report)
    
    # Save report
    output_path = Path("logs/document_analysis_report.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Document analysis report saved to: {output_path}")
    
    return assessment


def test_specific_requirement():
    """Test checking specific GDPR requirements"""
    print("\n" + "="*100)
    print("TEST 3: Specific Requirement Check")
    print("="*100 + "\n")
    
    # Load config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize violation finder
    finder = GDPRViolationFinder(config)
    
    requirement = "Article 17 (Right to Erasure)"
    scenario = "Our system allows users to delete their account, but we keep their email address and transaction history for marketing purposes indefinitely."
    
    print(f"📋 REQUIREMENT: {requirement}")
    print(f"📄 SCENARIO: {scenario}")
    print("\n" + "-"*100 + "\n")
    
    # Check compliance
    print("🔍 Checking compliance with specific requirement...\n")
    result = finder.check_specific_requirement(requirement, scenario)
    
    print("**ANALYSIS:**")
    print(result['analysis'])
    
    print("\n**RELEVANT SOURCES:**")
    if result.get('relevant_sources'):
        for i, source in enumerate(result['relevant_sources'], 1):
            print(f"{i}. {source}")
    
    return result


def print_statistics(assessment):
    """Print assessment statistics"""
    print("\n" + "="*100)
    print("ASSESSMENT STATISTICS")
    print("="*100 + "\n")
    
    print(f"📊 Overall Risk: {assessment.overall_risk_level} ({assessment.risk_score:.1f}/10)")
    print(f"⚠️  Violations Found: {len(assessment.violations)}")
    
    if assessment.violations:
        print("\n🔍 Violations by Severity:")
        severity_counts = {}
        for v in assessment.violations:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1
        
        for severity, count in sorted(severity_counts.items()):
            print(f"   - {severity}: {count}")
        
        print("\n📚 Citations Found:")
        total_citations = 0
        for v in assessment.violations:
            if v.source_citations:
                total_citations += len(v.source_citations)
                for cit in v.source_citations:
                    print(f"   - {cit.article_or_recital} (Relevance: {cit.relevance_score:.0%})")
        
        print(f"\n✅ Total Source Citations: {total_citations}")
        
        print("\n🎯 Highlighted Issues:")
        for i, v in enumerate(assessment.violations, 1):
            if v.highlighted_text:
                print(f"   {i}. {v.category}: \"{v.highlighted_text[:60]}...\"")


def main():
    """Run all tests"""
    print("\n" + "🔬"*50)
    print("TESTING ENHANCED GDPR VIOLATION DETECTION")
    print("Features: Text Highlighting | Source Citations | Verification")
    print("🔬"*50)
    
    try:
        # Test 1: Scenario analysis
        assessment1 = test_scenario_analysis()
        print_statistics(assessment1)
        
        # Test 2: Document analysis
        assessment2 = test_document_analysis()
        print_statistics(assessment2)
        
        # Test 3: Specific requirement
        result3 = test_specific_requirement()
        
        print("\n" + "✅"*50)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("✅"*50 + "\n")
        
        print("📁 Generated Reports:")
        print("   - logs/enhanced_violation_report.md")
        print("   - logs/enhanced_violation_report.json")
        print("   - logs/document_analysis_report.md")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
