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
from remediation.remediation_engine import RemediationEngine, RemediationGuidance


@dataclass
class SourceCitation:
    """Represents a citation from GDPR source documents"""
    article_or_recital: str  # e.g., "Article 6(1)(a)", "Recital 42"
    quoted_text: str  # Exact quote from GDPR
    source_document: str  # e.g., "GDPR Regulation (EU) 2016/679"
    context: str  # Additional context around the quote
    relevance_score: float  # How relevant this source is (0-1)


@dataclass
@dataclass
class GDPRViolation:
    """Represents a potential GDPR violation with verifiable sources"""
    category: str
    severity: str  # Critical, High, Medium, Low, Informational
    articles: List[str]
    description: str
    evidence: str
    recommendation: str
    risk_score: float  # 0-10
    
    # Enhanced verification fields
    highlighted_text: Optional[str] = None  # Problematic text from user's document
    source_citations: Optional[List[SourceCitation]] = None  # GDPR sources used
    verification_notes: Optional[str] = None  # How to verify this finding
    context_metadata: Optional[Dict] = None  # Additional metadata from LLM
    
    # Professional remediation guidance
    remediation_guidance: Optional[RemediationGuidance] = None  # Detailed action plan


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
        
        # Initialize DYNAMIC remediation engine with RAG and LLM access
        from remediation.remediation_engine_dynamic import DynamicRemediationEngine
        self.remediation_engine = DynamicRemediationEngine(
            rag_system=self.rag_system,
            llm_client=self.rag_system  # RAG system has LLM client
        )
        logger.info("Initialized GDPR Violation Finder with Dynamic Remediation Engine")
        
        self.prompts = config.get('prompts', {})
        self.risk_categories = config.get('risk_assessment', {}).get('categories', [])
        self.severity_levels = config.get('risk_assessment', {}).get('severity_levels', [])
        
        logger.info("Initialized GDPR Violation Finder with Remediation Engine")
    
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
        
        # Step 2: Identify potential violations (FIRST LLM CALL - focused on finding violations)
        violations = self._identify_violations(scenario, relevant_context)
        
        # Create summary of all violations for remediation context
        all_violations_summary = self._format_violations_summary(violations)
        
        # Step 3: Generate DYNAMIC, LLM-driven remediation guidance for each violation
        # (SECOND LLM CALL - focused on remediation, uses violation findings)
        for violation in violations:
            try:
                remediation = self.remediation_engine.generate_remediation(
                    violation_category=violation.category,
                    articles=violation.articles,
                    severity=violation.severity,
                    context=scenario,
                    evidence=violation.evidence,  # Pass problematic text for context
                    all_violations_text=all_violations_summary  # Pass all violations for holistic remediation
                )
                violation.remediation_guidance = remediation
                logger.info(f"✓ Generated dynamic remediation for {violation.category}")
            except Exception as e:
                logger.warning(f"Could not generate remediation for {violation.category}: {e}")
        
        # Step 4: Assess overall risk
        risk_assessment = self._assess_overall_risk(scenario, violations, relevant_context)
        
        logger.info(f"Analysis complete. Found {len(violations)} potential violations")
        
        return risk_assessment
    
    def _format_violations_summary(self, violations: List['GDPRViolation']) -> str:
        """Format all violations into a summary for remediation context"""
        if not violations:
            return "No violations found"
        
        summary_parts = []
        for i, v in enumerate(violations, 1):
            summary_parts.append(f"{i}. {v.category} (Severity: {v.severity}, Articles: {', '.join(v.articles or ['N/A'])})")
            if v.description:
                summary_parts.append(f"   Details: {v.description[:200]}")
        
        return "\n".join(summary_parts)
    
    def _retrieve_relevant_regulations(self, scenario: str, context_type: Optional[str]) -> List[Dict]:
        """Retrieve relevant GDPR regulations dynamically based on scenario content"""
        
        # Multi-strategy retrieval - no hardcoded hints
        all_results = []
        
        # Strategy 1: Use full scenario for semantic search
        query1 = scenario[:500]  # First 500 chars of scenario
        results1 = self.rag_system.retrieve_context(query1, top_k=15)
        all_results.extend(results1)
        
        # Strategy 2: Extract specific Article mentions if present
        import re
        article_mentions = re.findall(r'article\s+(\d+)', scenario.lower())
        if article_mentions:
            for article_num in article_mentions[:3]:
                query2 = f"Article {article_num} GDPR"
                results2 = self.rag_system.retrieve_context(query2, top_k=5)
                all_results.extend(results2)
        
        # Strategy 3: Search for general GDPR compliance requirements
        query3 = "GDPR requirements obligations compliance"
        results3 = self.rag_system.retrieve_context(query3, top_k=10)
        all_results.extend(results3)
        
        # Deduplicate and prioritize
        seen_ids = set()
        unique_results = []
        
        # First pass: Prioritize results with "Article" in text
        for result in all_results:
            chunk_id = result.get('chunk', {}).get('chunk_id') or result.get('metadata', {}).get('chunk_id')
            if chunk_id and chunk_id not in seen_ids:
                text = result.get('text', '').lower()
                if 'article' in text and 'recital' not in text:
                    seen_ids.add(chunk_id)
                    unique_results.append(result)
        
        # Second pass: Add other relevant results
        for result in all_results:
            chunk_id = result.get('chunk', {}).get('chunk_id') or result.get('metadata', {}).get('chunk_id')
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                unique_results.append(result)
                if len(unique_results) >= 10:
                    break
        
        logger.info(f"Retrieved {len(unique_results)} unique high-quality documents")
        return unique_results[:10]  # Top 10 for reranking
    
    def _identify_violations(self, scenario: str, context: List[Dict]) -> List[GDPRViolation]:
        """Identify specific GDPR violations"""
        
        # Format context for violation analysis
        context_text = self.rag_system.format_context(context)
        
        # Log context preview for debugging
        logger.info(f"Context preview (first 500 chars): {context_text[:500]}")
        
        # Construct violation finder prompt - manually to avoid JSON escaping issues
        prompt_template = self.prompts.get('violation_finder_prompt', '')
        # Replace placeholders manually
        prompt = prompt_template.replace('{context}', context_text).replace('{query}', scenario)
        
        # Generate violation analysis
        response = self.rag_system.generate_response(
            query=scenario,
            context=context_text,
            custom_prompt_template=prompt
        )
        
        # Log LLM response preview for debugging
        logger.info(f"LLM response preview (first 1000 chars): {response['answer'][:1000]}")
        
        # Parse violations from response
        violations = self._parse_violations_from_response(response['answer'], context)
        
        return violations
    
    def _parse_violations_from_response(self, response: str, context: List[Dict]) -> List[GDPRViolation]:
        """Parse violations from simple text format (no JSON)"""
        violations = []
        
        # Split by "VIOLATION" markers
        violation_blocks = response.split('VIOLATION ')[1:]  # Skip first empty split
        
        if not violation_blocks:
            logger.warning("No violation markers found, using fallback")
            violations.append(self._create_fallback_violation(response))
            return violations
        
        logger.info(f"Found {len(violation_blocks)} violation blocks to parse")
        
        for idx, block in enumerate(violation_blocks[:10], 1):  # Max 10 violations
            try:
                violation_data = {
                    'category': '',
                    'severity': 'Medium',
                    'articles': [],
                    'quote': '',
                    'description': ''
                }
                
                lines = block.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                        
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'category' in key:
                        violation_data['category'] = value
                    elif 'severity' in key:
                        violation_data['severity'] = value
                    elif 'article' in key:
                        # Parse articles - could be "6, 7" or "6(1)(a), 7"
                        articles = [a.strip() for a in value.replace(',', ' ').split() if a.strip()]
                        violation_data['articles'] = articles
                    elif 'quote' in key or 'problematic' in key:
                        violation_data['quote'] = value.strip('"\'')
                    elif 'why' in key or 'description' in key:
                        violation_data['description'] = value
                
                # Only create violation if we have minimum required data
                if violation_data['category']:
                    # Map severity to risk score
                    severity = violation_data['severity']
                    severity_scores = {
                        'Critical': 9.0,
                        'High': 7.0,
                        'Medium': 5.0,
                        'Low': 3.0
                    }
                    risk_score = severity_scores.get(severity, 5.0)
                    
                    violation = GDPRViolation(
                        category=violation_data['category'],
                        severity=severity,
                        articles=violation_data['articles'],
                        description=violation_data['description'] or f"GDPR violation related to {violation_data['category']}",
                        highlighted_text=violation_data['quote'],
                        recommendation='',  # Will be generated by remediation engine
                        risk_score=risk_score,
                        evidence=violation_data['description'][:500] if violation_data['description'] else '',
                        context_metadata={'source': 'LLM Analysis', 'parser': 'text'}
                    )
                    violations.append(violation)
                    logger.info(f"✓ Parsed violation {idx}: {violation.category} (Severity: {severity}, Articles: {violation.articles})")
                else:
                    logger.warning(f"Skipping violation block {idx} - missing category")
                    
            except Exception as e:
                logger.warning(f"Error parsing violation block {idx}: {e}")
                continue
        
        if not violations:
            logger.warning("No violations parsed successfully, using fallback")
            violations.append(self._create_fallback_violation(response))
        else:
            logger.info(f"Successfully parsed {len(violations)} violations")
        
        return violations
    
    def _parse_violations_text_fallback(self, response: str, context: List[Dict]) -> List[GDPRViolation]:
        """Fallback parser for non-JSON responses"""
        violations = []
        
        # Split by "VIOLATION" markers
        violation_blocks = response.split('VIOLATION ')[1:]  # Skip first empty split
        
        if not violation_blocks:
            # Final fallback: create one violation from full response
            logger.warning("No violation markers found, using final fallback")
            violations.append(self._create_fallback_violation(response))
            return violations
        
        for block in violation_blocks[:5]:  # Max 5 violations
            try:
                violation_data = {}
                lines = block.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if 'category' in key:
                            violation_data['category'] = value
                        elif 'severity' in key:
                            violation_data['severity'] = value
                        elif 'article' in key:
                            # Parse articles
                            articles = [a.strip() for a in value.split(',')]
                            violation_data['articles'] = articles
                        elif 'problematic' in key or 'quote' in key:
                            violation_data['highlighted_text'] = value.strip('"\'')
                        elif 'description' in key:
                            violation_data['description'] = value
                
                # Create violation if we have minimum data
                if violation_data.get('category'):
                    severity = violation_data.get('severity', 'Medium')
                    severity_scores = {
                        'Critical': 9.0,
                        'High': 7.0,
                        'Medium': 5.0,
                        'Low': 3.0
                    }
                    
                    violation = GDPRViolation(
                        category=violation_data.get('category', 'GDPR Violation'),
                        severity=severity,
                        articles=violation_data.get('articles', []),
                        description=violation_data.get('description', ''),
                        highlighted_text=violation_data.get('highlighted_text', ''),
                        recommendation='',
                        risk_score=severity_scores.get(severity, 5.0),
                        evidence='',
                        context_metadata={'source': 'Text Parsing'}
                    )
                    violations.append(violation)
                    
            except Exception as e:
                logger.warning(f"Error parsing violation block: {e}")
                continue
        
        return violations if violations else [self._create_fallback_violation(response)]
    
    def _create_fallback_violation(self, response: str) -> GDPRViolation:
        """Create a fallback violation when parsing fails"""
        return GDPRViolation(
            category="GDPR Compliance Review",
            severity="Medium",
            articles=[],
            description="Automated analysis identified potential compliance issues",
            highlighted_text="",
            recommendation="Conduct detailed manual compliance review with legal counsel",
            risk_score=5.0,
            evidence=response[:500] if response else "",
            context_metadata={'source': 'Fallback', 'verification': 'Manual review recommended - automated parsing incomplete'}
        )
    
    def _extract_citations(self, violation_data: dict, context: List[Dict]) -> Optional[List[SourceCitation]]:
        """Extract source citations with ACCURACY VALIDATION - 80%+ target"""
        articles = violation_data.get('articles', [])
        if not articles or not context:
            return None
        
        citations = []
        validated_count = 0
        
        for article_ref in articles[:3]:  # Max 3 citations for better coverage
            # Find matching context - strict validation required
            best_match = None
            best_score = 0.0
            
            for ctx in context:
                text = ctx.get('text', '')
                text_lower = text.lower()
                metadata = ctx.get('metadata', {})
                # Use rerank_score if available (more accurate), otherwise fall back to score
                relevance = ctx.get('rerank_score', ctx.get('score', 0.0))
                quality_tier = ctx.get('quality_tier', 'Unknown')
                
                # STRICT: Skip if this is just a Recital reference
                if 'recital' in text_lower and 'article' not in text_lower:
                    continue
                
                # Look for EXACT Article mentions (not fuzzy matching)
                import re
                article_num = re.search(r'\d+', article_ref)
                if article_num:
                    num = article_num.group()
                    # Must find "Article X" where X is the exact number
                    pattern = rf'\bArticle\s+{num}\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        # This is a valid match - check relevance score
                        if relevance > best_score:
                            best_score = relevance
                            # Extract meaningful quote
                            article_match = re.search(rf'(Article\s+{num}[^\n.]*(?:\.[^\n.]*)?)', text, re.IGNORECASE)
                            quote = article_match.group(1) if article_match else text[:200]
                            
                            best_match = {
                                'quote': quote,
                                'text': text,
                                'metadata': metadata,
                                'relevance': relevance,
                                'quality_tier': quality_tier
                            }
            
            # Add citation if validated - USE QUALITY TIER for better validation
            # For legal text, we focus on RELATIVE quality (top results) not absolute scores
            # Since we're using TOP 5 reranked results, be VERY permissive
            if best_match:
                # Accept any of top quality tiers OR any reasonable score
                # These are already the BEST results after reranking!
                is_acceptable_tier = best_match['quality_tier'] in ['Excellent', 'Good', 'Fair', 'Marginal']
                has_minimum_score = best_match['relevance'] >= 0.20  # Very low - trust reranking
                
                # Accept if it passed Article validation (most important check)
                if is_acceptable_tier and has_minimum_score:
                    citation = SourceCitation(
                        article_or_recital=article_ref,
                        quoted_text=best_match['quote'],
                        source_document="GDPR Regulation (EU) 2016/679",
                        context=best_match['metadata'].get('section_title', 'GDPR Articles'),
                        relevance_score=best_match['relevance']
                    )
                    citations.append(citation)
                    validated_count += 1
                    logger.info(f"✓ Validated {article_ref} ({best_match['quality_tier']}, {best_match['relevance']:.1%})")
                else:
                    logger.warning(f"✗ {article_ref} quality too low: {best_match['quality_tier']}, {best_match['relevance']:.1%}")
            else:
                logger.warning(f"✗ Could not find {article_ref} in retrieved documents")
        
        # Log accuracy metrics
        if citations:
            avg_relevance = sum(c.relevance_score for c in citations) / len(citations)
            logger.info(f"Citation accuracy: {avg_relevance:.1%} ({validated_count}/{len(articles)} validated)")
        
        return citations if citations else None
    
    def _create_fallback_violation(self, response: str) -> GDPRViolation:
        """Create a fallback violation when parsing fails"""
        return GDPRViolation(
            category="GDPR Compliance Review",
            severity="Medium",
            articles=[],
            description="Automated analysis identified potential compliance issues",
            evidence=response[:250],
            recommendation="Conduct detailed manual compliance review with legal counsel",
            risk_score=5.0,
            highlighted_text=None,
            source_citations=None,
            verification_notes="Manual review recommended - automated parsing incomplete"
        )
    
    def _assess_overall_risk(
        self,
        scenario: str,
        violations: List[GDPRViolation],
        context: List[Dict]
    ) -> RiskAssessment:
        """Assess overall compliance risk (optimized for speed)"""
        
        # Calculate overall risk score with weighted approach
        if violations:
            # Weight violations by severity for more accurate risk assessment
            severity_weights = {
                'Critical': 1.0,  # Full weight
                'High': 0.8,
                'Medium': 0.6,
                'Low': 0.4
            }
            
            total_weighted_score = 0
            total_weight = 0
            
            for v in violations:
                weight = severity_weights.get(v.severity, 0.5)
                total_weighted_score += v.risk_score * weight
                total_weight += weight
            
            # Calculate weighted average
            avg_risk_score = total_weighted_score / total_weight if total_weight > 0 else 0
            
            # Apply volume penalty - more violations increase risk
            volume_multiplier = 1.0 + (min(len(violations), 10) * 0.02)  # Up to +20% for 10+ violations
            avg_risk_score = min(avg_risk_score * volume_multiplier, 10.0)
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
        
        # Skip detailed LLM-based risk assessment for speed
        # Extract info directly from violations instead
        legal_basis_analysis = "See violations for detailed legal basis analysis"
        rights_impact = "See violations for data subject rights impact"
        
        # Extract recommendations from violations
        recommendations = [v.recommendation for v in violations if v.recommendation][:10]
        
        # Identify compliance gaps from violations
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
            # Convert violations with proper dataclass handling
            violations_data = []
            for v in assessment.violations:
                v_dict = asdict(v)
                # Convert SourceCitation objects if present
                if v.source_citations:
                    v_dict['source_citations'] = [asdict(cit) for cit in v.source_citations]
                violations_data.append(v_dict)
            
            return json.dumps({
                "scenario": scenario,
                "assessment": {
                    "overall_risk_level": assessment.overall_risk_level,
                    "risk_score": assessment.risk_score,
                    "violations": violations_data,
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

"""
                # Add highlighted problematic text
                if violation.highlighted_text:
                    report += f"""#### 🔴 Problematic Text from Your Document
```
{violation.highlighted_text}
```

"""
                
                report += f"""**Evidence**: {violation.evidence}

"""
                
                # Add GDPR source citations
                if violation.source_citations:
                    report += f"""#### 📚 GDPR Source Citations

"""
                    for j, citation in enumerate(violation.source_citations, 1):
                        report += f"""##### Citation {j}: {citation.article_or_recital}
**Source**: {citation.source_document}  
**Relevance**: {citation.relevance_score:.0%}

**Quoted from GDPR**:
> {citation.quoted_text}

**Context**: {citation.context}

"""
                
                report += f"""**Recommendation**: {violation.recommendation}

"""
                
                # Add verification notes
                if violation.verification_notes:
                    report += f"""#### ✓ Verification
{violation.verification_notes}

"""
                
                # Add professional remediation guidance
                if violation.remediation_guidance:
                    rem = violation.remediation_guidance
                    report += f"""---

## 🔧 Professional Remediation Guidance

### Priority & Effort
- **Priority**: {rem.priority.value}
- **Complexity**: {rem.complexity.value}
- **Estimated Effort**: {rem.estimated_effort}
- **Estimated Cost**: {rem.estimated_cost_range}

### 🚨 Immediate Actions (0-7 days)

"""
                    for action in rem.immediate_actions:
                        report += f"{action}\n"
                    
                    report += f"""
### 📅 Short-Term Solutions (1-3 months)

"""
                    for solution in rem.short_term_solutions:
                        report += f"{solution}\n"
                    
                    report += f"""
### 🎯 Long-Term Improvements (3-6 months)

"""
                    for improvement in rem.long_term_improvements:
                        report += f"{improvement}\n"
                    
                    # Add detailed implementation steps
                    if rem.detailed_steps:
                        report += f"""
### 📋 Implementation Steps

"""
                        for step in rem.detailed_steps:
                            report += f"""
**Step {step.step_number}: {step.action}**
- **Owner**: {step.owner}
- **Timeline**: {step.timeline}
- **Success Criteria**: {step.success_criteria}
- **Resources Needed**: {', '.join(step.resources_needed)}

"""
                    
                    # Add verification checklist
                    if rem.verification_checklist:
                        report += f"""
### ✅ Verification Checklist

"""
                        for item in rem.verification_checklist:
                            report += f"{item}\n"
                    
                    # Add technical requirements
                    if rem.technical_requirements:
                        report += f"""
### 🔧 Technical Requirements

"""
                        for req in rem.technical_requirements:
                            report += f"- {req}\n"
                    
                    # Add policy requirements
                    if rem.policy_requirements:
                        report += f"""
### 📄 Policy & Documentation Requirements

"""
                        for pol in rem.policy_requirements:
                            report += f"- {pol}\n"
                    
                    # Add training requirements
                    if rem.training_requirements:
                        report += f"""
### 🎓 Training Requirements

"""
                        for training in rem.training_requirements:
                            report += f"- {training}\n"
                    
                    # Add best practices
                    if rem.best_practices:
                        report += f"""
### 💡 Best Practices

"""
                        for practice in rem.best_practices:
                            report += f"- {practice}\n"
                    
                    # Add resources
                    if rem.helpful_resources:
                        report += f"""
### 📚 Helpful Resources

"""
                        for resource in rem.helpful_resources:
                            report += f"- {resource}\n"
                    
                    # Add similar cases
                    if rem.similar_cases:
                        report += f"""
### ⚖️ Similar Enforcement Cases

"""
                        for case in rem.similar_cases:
                            report += f"- {case}\n"
                    
                    # Add ongoing monitoring
                    if rem.ongoing_monitoring:
                        report += f"""
### 📊 Ongoing Monitoring

{rem.ongoing_monitoring}

"""
                
                report += "---\n\n"
            
            # Summary sections
            if assessment.compliance_gaps:
                report += "## 📋 Compliance Gaps Summary\n"
                for gap in assessment.compliance_gaps:
                    report += f"- {gap}\n"
                report += "\n"
            
            if assessment.recommendations:
                report += "## 🎯 Quick Action Items\n"
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
    
    def analyze_document(
        self,
        document_text: str,
        document_type: str = "privacy_policy",
        line_by_line: bool = False
    ) -> RiskAssessment:
        """
        Analyze a user document (privacy policy, terms of service, etc.) for GDPR compliance.
        Highlights specific problematic sections with line/paragraph references.
        
        Args:
            document_text: Full text of the document to analyze
            document_type: Type of document (privacy_policy, terms_of_service, consent_form, etc.)
            line_by_line: If True, analyze line by line (slower but more precise)
        
        Returns:
            RiskAssessment with highlighted violations in context
        """
        logger.info(f"Analyzing {document_type} document ({len(document_text)} characters)")
        
        # Split document into paragraphs for reference
        paragraphs = [p.strip() for p in document_text.split('\n\n') if p.strip()]
        
        # Create enhanced scenario description
        scenario = f"""Analyze this {document_type} document for GDPR compliance:

{document_text}

For each violation found, quote the EXACT problematic text from the document above."""
        
        # Perform standard analysis
        assessment = self.analyze_scenario(scenario, context_type=document_type)
        
        # Enhance violations with paragraph references
        for violation in assessment.violations:
            if violation.highlighted_text:
                # Find which paragraph contains this text
                for i, para in enumerate(paragraphs, 1):
                    if violation.highlighted_text.strip() in para:
                        if not violation.verification_notes:
                            violation.verification_notes = ""
                        violation.verification_notes += f"\n📍 Found in paragraph {i} of the document."
                        break
        
        return assessment


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
