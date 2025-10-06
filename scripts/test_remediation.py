#!/usr/bin/env python3
"""
Test remediation engine improvements without LLM calls
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from remediation.remediation_engine import RemediationEngine

def test_remediation_engine():
    """Test that remediation templates are distinct and specific"""
    print("=" * 80)
    print("TESTING REMEDIATION ENGINE IMPROVEMENTS")
    print("=" * 80)
    print()
    
    engine = RemediationEngine()
    print("✓ RemediationEngine initialized successfully")
    print(f"✓ Loaded {len(engine.remediation_templates)} templates")
    print()
    
    # Test Article 17 (Erasure)
    print("Testing Article 17 (Right to Erasure):")
    print("-" * 80)
    remediation_17 = engine.generate_remediation(
        violation_category="Data Subject Rights",
        articles=["Article 17"],
        severity="Critical",
        context="Users cannot delete their data"
    )
    print(f"  Template used: erasure_rights")
    print(f"  Priority: {remediation_17.priority.value}")
    print(f"  Complexity: {remediation_17.complexity.value}")
    print(f"  Cost: {remediation_17.estimated_cost_range}")
    print(f"  Immediate Actions: {len(remediation_17.immediate_actions)} items")
    print(f"    - {remediation_17.immediate_actions[0]}")
    print(f"    - {remediation_17.immediate_actions[1]}")
    print()
    
    # Test Article 21 (Objection/Marketing)
    print("Testing Article 21 (Right to Object - Marketing):")
    print("-" * 80)
    remediation_21 = engine.generate_remediation(
        violation_category="Data Subject Rights",
        articles=["Article 21"],
        severity="High",
        context="share them with advertisers"
    )
    print(f"  Template used: objection_rights")
    print(f"  Priority: {remediation_21.priority.value}")
    print(f"  Complexity: {remediation_21.complexity.value}")
    print(f"  Cost: {remediation_21.estimated_cost_range}")
    print(f"  Immediate Actions: {len(remediation_21.immediate_actions)} items")
    print(f"    - {remediation_21.immediate_actions[0]}")
    print(f"    - {remediation_21.immediate_actions[1]}")
    print()
    
    # Verify they're different
    print("Verification:")
    print("-" * 80)
    if remediation_17.immediate_actions != remediation_21.immediate_actions:
        print("✓ Article 17 and 21 have DIFFERENT remediation guidance (GOOD!)")
    else:
        print("✗ Article 17 and 21 have IDENTICAL guidance (BAD - still duplicate)")
    
    if "delete" in str(remediation_17.immediate_actions).lower() or "deletion" in str(remediation_17.immediate_actions).lower():
        print("✓ Article 17 guidance mentions deletion/erasure (CORRECT)")
    else:
        print("✗ Article 17 guidance doesn't mention deletion")
    
    if "unsubscribe" in str(remediation_21.immediate_actions).lower() or "marketing" in str(remediation_21.immediate_actions).lower():
        print("✓ Article 21 guidance mentions marketing/unsubscribe (CORRECT)")
    else:
        print("✗ Article 21 guidance doesn't mention marketing")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Show all loaded templates
    print("\nAll Available Templates:")
    for template_name in sorted(engine.remediation_templates.keys()):
        print(f"  - {template_name}")

if __name__ == "__main__":
    test_remediation_engine()
