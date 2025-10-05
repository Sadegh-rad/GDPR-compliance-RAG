"""
Example usage scripts for GDPR RAG system
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import yaml
from rag.gdpr_rag import GDPRRAGSystem
from violation_finder.violation_finder import GDPRViolationFinder


def example_basic_query():
    """Example: Basic GDPR query"""
    print("\n" + "="*80)
    print("Example 1: Basic GDPR Query")
    print("="*80 + "\n")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    rag = GDPRRAGSystem(config)
    
    query = "What are the main principles of GDPR?"
    result = rag.query(query, top_k=3)
    
    print(f"Query: {query}\n")
    print(f"Answer:\n{result['answer']}\n")
    print(f"Sources: {len(result.get('sources', []))}")


def example_article_specific():
    """Example: Query about specific GDPR article"""
    print("\n" + "="*80)
    print("Example 2: Article-Specific Query")
    print("="*80 + "\n")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    rag = GDPRRAGSystem(config)
    
    # Query with filters for specific article
    query = "What does Article 6 say about legal basis?"
    result = rag.query(
        query,
        top_k=3,
        filters={"article_number": "6"}
    )
    
    print(f"Query: {query}\n")
    print(f"Answer:\n{result['answer']}\n")


def example_violation_analysis():
    """Example: Analyze scenario for violations"""
    print("\n" + "="*80)
    print("Example 3: Violation Analysis")
    print("="*80 + "\n")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    finder = GDPRViolationFinder(config)
    
    scenario = """
    A fitness tracking app collects users' health data, location data, 
    and exercise habits. The app shares this data with advertisers to 
    show personalized ads. Users are not explicitly informed about this 
    data sharing, and there is no option to opt out. The app stores all 
    data indefinitely.
    """
    
    assessment = finder.analyze_scenario(scenario)
    
    print(f"Scenario: {scenario.strip()}\n")
    print(f"Risk Level: {assessment.overall_risk_level}")
    print(f"Risk Score: {assessment.risk_score:.1f}/10")
    print(f"\nViolations Found: {len(assessment.violations)}\n")
    
    for i, violation in enumerate(assessment.violations, 1):
        print(f"{i}. {violation.category} [{violation.severity}]")
        print(f"   Articles: {', '.join(violation.articles)}")
        print(f"   {violation.description}\n")


def example_compliance_check():
    """Example: Check compliance with specific requirement"""
    print("\n" + "="*80)
    print("Example 4: Compliance Check")
    print("="*80 + "\n")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    finder = GDPRViolationFinder(config)
    
    scenario = "We obtain user consent through a pre-checked checkbox on registration"
    requirement = "Article 4(11) - Valid Consent"
    
    result = finder.check_specific_requirement(requirement, scenario)
    
    print(f"Requirement: {requirement}")
    print(f"Scenario: {scenario}\n")
    print(f"Analysis:\n{result['analysis']}\n")


def example_batch_queries():
    """Example: Process multiple queries"""
    print("\n" + "="*80)
    print("Example 5: Batch Queries")
    print("="*80 + "\n")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    rag = GDPRRAGSystem(config)
    
    queries = [
        "What is a Data Protection Impact Assessment?",
        "When do I need to appoint a DPO?",
        "What are the penalties for GDPR violations?"
    ]
    
    results = rag.batch_query(queries, top_k=2)
    
    for i, result in enumerate(results, 1):
        print(f"\nQuery {i}: {result['query']}")
        print(f"Answer: {result['answer'][:200]}...\n")
        print("-" * 80)


def example_report_generation():
    """Example: Generate compliance report"""
    print("\n" + "="*80)
    print("Example 6: Compliance Report Generation")
    print("="*80 + "\n")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    finder = GDPRViolationFinder(config)
    
    scenario = """
    An e-commerce website collects customer purchase history, payment 
    information, and browsing behavior. The website uses cookies without 
    obtaining prior consent. Customer data is transferred to servers in 
    countries outside the EU without adequate safeguards. The website 
    does not have a clear privacy policy, and customers cannot easily 
    access or delete their data.
    """
    
    assessment = finder.analyze_scenario(scenario)
    report = finder.generate_compliance_report(scenario, assessment, format="markdown")
    
    # Save report
    output_file = Path("example_compliance_report.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Scenario analyzed and report generated")
    print(f"Report saved to: {output_file}")
    print(f"\nRisk Level: {assessment.overall_risk_level}")
    print(f"Violations: {len(assessment.violations)}")
    print(f"Recommendations: {len(assessment.recommendations)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GDPR RAG System Examples")
    parser.add_argument(
        '--example',
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help='Example number to run (1-6), or run all if not specified'
    )
    
    args = parser.parse_args()
    
    examples = [
        example_basic_query,
        example_article_specific,
        example_violation_analysis,
        example_compliance_check,
        example_batch_queries,
        example_report_generation
    ]
    
    if args.example:
        examples[args.example - 1]()
    else:
        print("Running all examples...")
        for example_func in examples:
            try:
                example_func()
            except Exception as e:
                print(f"Error in {example_func.__name__}: {e}")
