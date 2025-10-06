#!/bin/bash

echo "=============================================="
echo "CHECKING IMPROVEMENTS"
echo "=============================================="
echo ""

REPORT="/home/ubuntu-beond/gdpr compliance/GDPR-compliance-RAG/logs/quick_test_report.md"

if [ -f "$REPORT" ]; then
    echo "📄 Latest Report Generated at: $(stat -c %y "$REPORT" | cut -d'.' -f1)"
    echo ""
    
    echo "🔍 CHECKING FOR IMPROVEMENTS:"
    echo ""
    
    # Check for proper Article citations (not Recitals)
    echo "1. Article Citations (should see 'Article 6', 'Article 17', 'Article 21'):"
    grep -i "Relevant Articles:" "$REPORT" | head -3
    echo ""
    
    # Check relevance scores
    echo "2. Relevance Scores (should be >60%):"
    grep -i "Relevance:" "$REPORT" | head -3
    echo ""
    
    # Check for violations detected
    echo "3. Violations Detected:"
    grep -c "^### [0-9]" "$REPORT"
    echo ""
    
    # Show first violation details
    echo "4. First Violation Details:"
    sed -n '/^### 1\./,/^---/p' "$REPORT" | head -20
    echo ""
    
    echo "=============================================="
    echo "✅ Check complete. Full report at: $REPORT"
    echo "=============================================="
else
    echo "❌ Report not found yet. Test may still be running..."
fi
