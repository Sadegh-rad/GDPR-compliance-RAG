#!/usr/bin/env python3
"""
Test script for GDPR Compliance Dashboard API
Tests the full analysis workflow
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5001"

# Test scenario (same as the successful CLI test)
TEST_SCENARIO = """
Mobile App Location Tracking Implementation:
Our fitness app continuously tracks user location in the background to provide route mapping and activity statistics. 
The app collects GPS coordinates every 30 seconds and stores them indefinitely for "service improvement" purposes. 
Location data is shared with third-party advertising partners and analytics providers. 
Users must enable location tracking to use any app features, even those that don't require location data like the calorie calculator. 
The privacy policy mentions data collection but doesn't specify the exact types of data collected or how long it's retained.
"""

def test_health_check():
    """Test if the API is running"""
    print("\n" + "="*80)
    print("1. Testing Health Check...")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_analyze_scenario():
    """Test the scenario analysis endpoint"""
    print("\n" + "="*80)
    print("2. Testing Scenario Analysis...")
    print("="*80)
    
    try:
        print("Submitting test scenario...")
        print(f"Scenario length: {len(TEST_SCENARIO)} characters\n")
        
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"scenario": TEST_SCENARIO},
            timeout=300  # 5 minutes timeout for LLM processing
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*80)
            print("ANALYSIS RESULTS")
            print("="*80)
            
            print(f"\n📊 Overall Risk Score: {result.get('risk_score', 'N/A')}/10")
            print(f"🚨 Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"🔍 Total Violations Found: {result.get('total_violations', 0)}")
            print(f"📅 Analysis ID: {result.get('analysis_id', 'N/A')}")
            
            violations = result.get('violations', [])
            
            if violations:
                print("\n" + "="*80)
                print(f"DETECTED VIOLATIONS ({len(violations)})")
                print("="*80)
                
                for i, violation in enumerate(violations, 1):
                    print(f"\n[{i}] {violation.get('category', 'Unknown')}")
                    print(f"    Severity: {violation.get('severity', 'N/A')}")
                    print(f"    Risk Score: {violation.get('risk_score', 0)}/10")
                    print(f"    GDPR Articles: {', '.join(violation.get('articles', []))}")
                    print(f"    Evidence: {violation.get('evidence', 'N/A')[:150]}...")
                    print(f"    Recommendation: {violation.get('recommendation', 'N/A')[:150]}...")
                    
                    # Check remediation guidance
                    remediation = violation.get('remediation', {})
                    if remediation:
                        print(f"\n    📋 Remediation Plan:")
                        print(f"       Priority: {remediation.get('priority', 'N/A')}")
                        print(f"       Complexity: {remediation.get('complexity', 'N/A')}")
                        print(f"       Estimated Effort: {remediation.get('estimated_effort', 'N/A')}")
                        print(f"       Estimated Cost: {remediation.get('estimated_cost', 'N/A')}")
                        
                        immediate = remediation.get('immediate_actions', [])
                        if immediate:
                            print(f"\n       🚀 Immediate Actions ({len(immediate)}):")
                            for action in immediate[:2]:
                                print(f"          • {action}")
                        
                        short_term = remediation.get('short_term_solutions', [])
                        if short_term:
                            print(f"\n       📅 Short-term Solutions ({len(short_term)}):")
                            for solution in short_term[:2]:
                                print(f"          • {solution}")
                        
                        long_term = remediation.get('long_term_improvements', [])
                        if long_term:
                            print(f"\n       🎯 Long-term Improvements ({len(long_term)}):")
                            for improvement in long_term[:2]:
                                print(f"          • {improvement}")
                
                print("\n" + "="*80)
                print("✅ ANALYSIS COMPLETED SUCCESSFULLY!")
                print("="*80)
                
                return True
            else:
                print("\n⚠️  No violations detected (unexpected)")
                return False
                
        else:
            print(f"\n❌ Error Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (LLM processing may take longer)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("GDPR COMPLIANCE DASHBOARD - API TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Scenario: Mobile App Location Tracking")
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Make sure the Flask server is running.")
        print("   Start it with: cd web_ui && python app.py")
        return
    
    # Test 2: Scenario analysis
    print("\n⏳ Starting scenario analysis (this may take 1-3 minutes)...")
    test_analyze_scenario()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)

if __name__ == "__main__":
    main()
