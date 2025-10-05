"""
GDPR Violation and Risk Finder
Specialized module for identifying GDPR violations and assessing compliance risks
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, List, Optional, Tuple
from loguru import logger
import json
from dataclasses import dataclass, asdict

try:
    import ollama
except ImportError:
    logger.error("Ollama package not installed. Install with: pip install ollama")
    raise

from rag.gdpr_rag import GDPRRAGSystem


@dataclass
class GDPRViolation:
    """Represents a potential GDPR violation"""
    category: str
    severity: str  # Critical, High, Medium, Low, Informational
    articles: List[str]
    description: str
    evidence: str
    recommendation: str
    risk_score: float  # 0-10


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment result"""
    overall_risk_level: str
    risk_score: float  # 0-10
    violations: List[GDPRViolation]
    compliance_gaps: List[str]
    recommendations: List[str]
    legal_basis_analysis: str
    data_subject_rights_impact: str


class GDPRViolationFinder:
    """Identifies GDPR violations and assesses compliance risks"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.rag_system = GDPRRAGSystem(config)
        self.prompts = config.get('prompts', {})
        self.risk_categories = config.get('risk_assessment', {}).get('categories', [])
        self.severity_levels = config.get('risk_assessment', {}).get('severity_levels', [])
        
        logger.info("Initialized GDPR Violation Finder")
    
    def analyze_scenario(self, scenario: str, context_type: Optional[str] = None) -> RiskAssessment:
        """
        Analyze a scenario for GDPR violations and risks
        
        Args:
            scenario: Description of the data processing scenario
            context_type: Optional context (e.g., "data_breach", "processing_activity")
        
        Returns:
            RiskAssessment object with detailed analysis
        """
        logger.info(f"Analyzing scenario for GDPR violations...")
        
        # Step 1: Retrieve relevant GDPR articles and guidelines
        relevant_context = self._retrieve_relevant_regulations(scenario, context_type)
        
        # Step 2: Identify potential violations
        violations = self._identify_violations(scenario, relevant_context)
        
        # Step 3: Assess overall risk
        risk_assessment = self._assess_overall_risk(scenario, violations, relevant_context)
        
        logger.info(f"Analysis complete. Found {len(violations)} potential violations")
        
        return risk_assessment
    
    def _retrieve_relevant_regulations(self, scenario: str, context_type: Optional[str]) -> List[Dict]:
        """Retrieve relevant GDPR regulations and guidelines"""
        
        # Build search queries based on scenario
        queries = [scenario]
        
        # Add category-specific queries
        for category in self.risk_categories:
            if any(keyword in scenario.lower() for keyword in category.lower().split()):
                queries.append(f"{category} GDPR requirements")
        
        # Retrieve context for all queries
        all_results = []
        for query in queries[:3]:  # Limit to avoid too many queries
            results = self.rag_system.retrieve_context(query, top_k=5)
            all_results.extend(results)
        
        # Deduplicate based on chunk_id
        seen_ids = set()
        unique_results = []
        for result in all_results:
            chunk_id = result['chunk'].get('chunk_id')
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                unique_results.append(result)
        
        return unique_results[:10]  # Top 10 most relevant
    
    def _identify_violations(self, scenario: str, context: List[Dict]) -> List[GDPRViolation]:
        """Identify specific GDPR violations"""
        
        # Format context for violation analysis
        context_text = self.rag_system.format_context(context)
        
        # Construct violation finder prompt
        prompt = self.prompts.get('violation_finder_prompt', '').format(
            context=context_text,
            query=scenario
        )
        
        # Generate violation analysis
        response = self.rag_system.generate_response(
            query=scenario,
            context=context_text,
            custom_prompt_template=prompt
        )
        
        # Parse violations from response
        violations = self._parse_violations_from_response(response['answer'], context)
        
        return violations
    
    def _parse_violations_from_response(self, response: str, context: List[Dict]) -> List[GDPRViolation]:
        """Parse structured violations from LLM response"""
        violations = []
        
        # Use LLM to structure the response into JSON
        structure_prompt = f"""Based on the following violation analysis, extract structured information about each violation.

For each violation, provide:
- category: The GDPR category (e.g., "Data Subject Rights", "Data Processing Principles")
- severity: Critical, High, Medium, Low, or Informational
- articles: List of relevant GDPR articles (e.g., ["Article 6", "Article 13"])
- description: Brief description of the violation
- evidence: Evidence from the scenario
- recommendation: How to remediate
- risk_score: Score from 0-10

Analysis:
{response}

Return ONLY a JSON array of violations, no other text."""
        
        try:
            structure_response = ollama.chat(
                model=self.rag_system.model,
                messages=[
                    {'role': 'system', 'content': 'You are a JSON extraction assistant. Return only valid JSON.'},
                    {'role': 'user', 'content': structure_prompt}
                ],
                options={'temperature': 0.1}
            )
            
            # Try to parse JSON
            structured_data = json.loads(structure_response['message']['content'])
            
            for v_data in structured_data:
                violation = GDPRViolation(
                    category=v_data.get('category', 'Unknown'),
                    severity=v_data.get('severity', 'Medium'),
                    articles=v_data.get('articles', []),
                    description=v_data.get('description', ''),
                    evidence=v_data.get('evidence', ''),
                    recommendation=v_data.get('recommendation', ''),
                    risk_score=float(v_data.get('risk_score', 5.0))
                )
                violations.append(violation)
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not parse structured violations: {e}")
            # Fallback: create a single violation from the full response
            violations.append(GDPRViolation(
                category="General Compliance",
                severity="Medium",
                articles=[],
                description="Multiple potential violations identified",
                evidence=response[:500],
                recommendation="Conduct detailed compliance review",
                risk_score=5.0
            ))
        
        return violations
    
    def _assess_overall_risk(
        self,
        scenario: str,
        violations: List[GDPRViolation],
        context: List[Dict]
    ) -> RiskAssessment:
        """Assess overall compliance risk"""
        
        # Calculate overall risk score
        if violations:
            avg_risk_score = sum(v.risk_score for v in violations) / len(violations)
        else:
            avg_risk_score = 0.0
        
        # Determine risk level
        if avg_risk_score >= 8:
            risk_level = "Critical"
        elif avg_risk_score >= 6:
            risk_level = "High"
        elif avg_risk_score >= 4:
            risk_level = "Medium"
        elif avg_risk_score >= 2:
            risk_level = "Low"
        else:
            risk_level = "Minimal"
        
        # Generate comprehensive risk assessment
        context_text = self.rag_system.format_context(context)
        
        assessment_prompt = self.prompts.get('risk_assessment_prompt', '').format(
            context=context_text,
            query=scenario
        )
        
        assessment_response = self.rag_system.generate_response(
            query=scenario,
            context=context_text,
            custom_prompt_template=assessment_prompt
        )
        
        # Extract specific analyses
        legal_basis_analysis = self._extract_section(assessment_response['answer'], "legal basis")
        rights_impact = self._extract_section(assessment_response['answer'], "data subject rights")
        
        # Extract recommendations
        recommendations = self._extract_recommendations(assessment_response['answer'])
        
        # Identify compliance gaps
        compliance_gaps = self._identify_compliance_gaps(violations)
        
        return RiskAssessment(
            overall_risk_level=risk_level,
            risk_score=avg_risk_score,
            violations=violations,
            compliance_gaps=compliance_gaps,
            recommendations=recommendations,
            legal_basis_analysis=legal_basis_analysis,
            data_subject_rights_impact=rights_impact
        )
    
    def _extract_section(self, text: str, section_keyword: str) -> str:
        """Extract a specific section from text"""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            if section_keyword.lower() in line.lower():
                in_section = True
            elif in_section and line.strip() and any(keyword in line.lower() for keyword in ['##', 'risk', 'impact', 'compliance']):
                break
            elif in_section:
                section_lines.append(line)
        
        return '\n'.join(section_lines).strip() if section_lines else "No specific analysis available"
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from text"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered lists, bullet points, or recommendation keywords
            if any(line.startswith(marker) for marker in ['1.', '2.', '3.', '-', '•', '*']):
                if any(keyword in line.lower() for keyword in ['should', 'must', 'recommend', 'ensure', 'implement']):
                    # Clean up the line
                    cleaned = line.lstrip('0123456789.-•* ')
                    if len(cleaned) > 20:  # Minimum length for a meaningful recommendation
                        recommendations.append(cleaned)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _identify_compliance_gaps(self, violations: List[GDPRViolation]) -> List[str]:
        """Identify compliance gaps from violations"""
        gaps = set()
        
        for violation in violations:
            gap = f"{violation.category}: {violation.description}"
            gaps.add(gap)
        
        return list(gaps)
    
    def generate_compliance_report(
        self,
        scenario: str,
        assessment: RiskAssessment,
        format: str = "markdown"
    ) -> str:
        """
        Generate a formatted compliance report
        
        Args:
            scenario: The analyzed scenario
            assessment: RiskAssessment result
            format: Output format ("markdown", "json", "text")
        
        Returns:
            Formatted report
        """
        if format == "json":
            return json.dumps({
                "scenario": scenario,
                "assessment": {
                    "overall_risk_level": assessment.overall_risk_level,
                    "risk_score": assessment.risk_score,
                    "violations": [asdict(v) for v in assessment.violations],
                    "compliance_gaps": assessment.compliance_gaps,
                    "recommendations": assessment.recommendations,
                    "legal_basis_analysis": assessment.legal_basis_analysis,
                    "data_subject_rights_impact": assessment.data_subject_rights_impact
                }
            }, indent=2)
        
        elif format == "markdown":
            report = f"""# GDPR Compliance Risk Assessment Report

## Scenario
{scenario}

## Overall Risk Assessment
- **Risk Level**: {assessment.overall_risk_level}
- **Risk Score**: {assessment.risk_score:.1f}/10

## Identified Violations

"""
            for i, violation in enumerate(assessment.violations, 1):
                report += f"""### {i}. {violation.category}
**Severity**: {violation.severity}  
**Risk Score**: {violation.risk_score}/10  
**Relevant Articles**: {', '.join(violation.articles) if violation.articles else 'N/A'}

**Description**: {violation.description}

**Evidence**: {violation.evidence}

**Recommendation**: {violation.recommendation}

---

"""
            
            report += f"""## Legal Basis Analysis
{assessment.legal_basis_analysis}

## Data Subject Rights Impact
{assessment.data_subject_rights_impact}

## Compliance Gaps
"""
            for gap in assessment.compliance_gaps:
                report += f"- {gap}\n"
            
            report += f"""
## Recommendations
"""
            for i, rec in enumerate(assessment.recommendations, 1):
                report += f"{i}. {rec}\n"
            
            return report
        
        else:  # text format
            report = f"GDPR COMPLIANCE RISK ASSESSMENT\n\n"
            report += f"Scenario: {scenario}\n\n"
            report += f"Risk Level: {assessment.overall_risk_level} ({assessment.risk_score:.1f}/10)\n\n"
            report += f"Violations Found: {len(assessment.violations)}\n\n"
            
            for i, violation in enumerate(assessment.violations, 1):
                report += f"{i}. {violation.category} [{violation.severity}]\n"
                report += f"   {violation.description}\n\n"
            
            return report
    
    def check_specific_requirement(self, requirement: str, scenario: str) -> Dict:
        """
        Check compliance with a specific GDPR requirement
        
        Args:
            requirement: Specific GDPR requirement or article
            scenario: Scenario to check
        
        Returns:
            Dictionary with compliance status and details
        """
        query = f"Does the following scenario comply with {requirement}? Scenario: {scenario}"
        
        result = self.rag_system.query(query, top_k=3)
        
        return {
            "requirement": requirement,
            "scenario": scenario,
            "analysis": result['answer'],
            "relevant_sources": result.get('sources', [])
        }


if __name__ == "__main__":
    import yaml
    
    # Load config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize violation finder
    finder = GDPRViolationFinder(config)
    
    # Example scenario
    scenario = """
    Our company collects email addresses from website visitors without explicit consent.
    We use these emails for marketing purposes and share them with third-party advertisers.
    We don't have a clear privacy policy, and users cannot easily unsubscribe from our emails.
    We store this data indefinitely and don't have any security measures in place.
    """
    
    print("\n" + "="*80)
    print("GDPR Violation Analysis")
    print("="*80 + "\n")
    print(f"Scenario:\n{scenario}\n")
    print("="*80 + "\n")
    
    # Analyze scenario
    assessment = finder.analyze_scenario(scenario)
    
    # Generate report
    report = finder.generate_compliance_report(scenario, assessment, format="markdown")
    print(report)
    
    # Save report
    output_path = Path("violation_analysis_report.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_path}")
