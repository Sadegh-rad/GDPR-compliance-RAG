"""
Remediation Engine - Professional GDPR Compliance Solutions
Provides actionable recommendations, implementation guidance, and real-world solutions
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


class RemediationPriority(Enum):
    """Priority levels for remediation actions"""
    CRITICAL = "Critical"      # Must fix immediately (legal exposure)
    HIGH = "High"              # Fix within 30 days
    MEDIUM = "Medium"          # Fix within 90 days
    LOW = "Low"                # Ongoing improvement


class RemediationComplexity(Enum):
    """Implementation complexity"""
    SIMPLE = "Simple"          # 1-2 days, minimal resources
    MODERATE = "Moderate"      # 1-2 weeks, some development
    COMPLEX = "Complex"        # 1-3 months, significant resources
    MAJOR = "Major"            # 3+ months, organizational change


@dataclass
class RemediationStep:
    """Single remediation step with details"""
    step_number: int
    action: str                     # What to do
    owner: str                      # Who should do it
    timeline: str                   # When to complete
    success_criteria: str           # How to verify completion
    resources_needed: List[str]     # What's required


@dataclass
class RemediationGuidance:
    """Comprehensive remediation guidance for a violation"""
    
    # Basic information
    violation_category: str
    affected_articles: List[str]
    
    # Priority and effort
    priority: RemediationPriority
    complexity: RemediationComplexity
    estimated_effort: str           # e.g., "2-4 weeks"
    
    # Solutions
    immediate_actions: List[str]     # Quick fixes (0-7 days)
    short_term_solutions: List[str]  # 1-3 months
    long_term_improvements: List[str] # 3-6 months
    
    # Implementation
    detailed_steps: List[RemediationStep]
    technical_requirements: List[str]
    policy_requirements: List[str]
    training_requirements: List[str]
    
    # Costs and resources
    estimated_cost_range: str       # e.g., "$5k-$15k"
    required_roles: List[str]       # Who needs to be involved
    
    # Validation
    verification_checklist: List[str]
    documentation_needed: List[str]
    ongoing_monitoring: str
    
    # References
    best_practices: List[str]
    helpful_resources: List[str]
    similar_cases: List[str]        # Real-world examples


class RemediationEngine:
    """
    Professional remediation guidance engine
    Provides real-world, actionable solutions for GDPR violations
    """
    
    def __init__(self):
        self.remediation_templates = self._load_remediation_templates()
    
    def generate_remediation(
        self,
        violation_category: str,
        articles: List[str],
        severity: str,
        context: str
    ) -> RemediationGuidance:
        """
        Generate comprehensive remediation guidance
        
        Args:
            violation_category: Type of violation
            articles: Affected GDPR articles
            severity: Violation severity
            context: Additional context
        
        Returns:
            Complete remediation guidance
        """
        # Get template based on violation type
        template_key = self._map_to_template(violation_category, articles)
        template = self.remediation_templates.get(template_key)
        
        if not template:
            return self._generate_generic_remediation(violation_category, articles, severity)
        
        # Customize based on severity and context
        return self._customize_remediation(template, severity, context)
    
    def _load_remediation_templates(self) -> Dict:
        """Load professional remediation templates"""
        return {
            'consent_violation': self._get_consent_remediation(),
            'data_subject_rights': self._get_dsr_remediation(),
            'erasure_rights': self._get_erasure_remediation(),
            'objection_rights': self._get_objection_remediation(),
            'access_rights': self._get_access_remediation(),
            'portability_rights': self._get_portability_remediation(),
            'data_breach': self._get_breach_remediation(),
            'transparency': self._get_transparency_remediation(),
            'data_transfer': self._get_transfer_remediation(),
            'security': self._get_security_remediation(),
            'accountability': self._get_accountability_remediation(),
            'legal_basis': self._get_legal_basis_remediation(),
            'data_retention': self._get_retention_remediation(),
            'dpo_requirement': self._get_dpo_remediation(),
        }
    
    def _get_consent_remediation(self) -> Dict:
        """Remediation for consent violations"""
        return {
            'priority': RemediationPriority.CRITICAL,
            'complexity': RemediationComplexity.MODERATE,
            'estimated_effort': '2-4 weeks',
            'estimated_cost': '$10k-$30k',
            
            'immediate_actions': [
                '🚨 Stop all processing without valid consent immediately',
                '📧 Audit current data collection mechanisms',
                '🔍 Identify all data collected without consent',
                '⚠️ Assess legal exposure and consult legal counsel',
            ],
            
            'short_term': [
                '✅ Implement consent management platform (CMP)',
                '📝 Design clear, granular consent forms',
                '🔧 Add consent withdrawal mechanisms',
                '📊 Create consent records database',
                '🔐 Implement consent verification workflows',
            ],
            
            'long_term': [
                '🎯 Regular consent refresh campaigns',
                '📈 Implement consent analytics and monitoring',
                '🔄 Automated consent expiry and renewal',
                '🌍 Multi-jurisdiction consent management',
                '📚 Staff training on consent requirements',
            ],
            
            'technical_steps': [
                RemediationStep(
                    step_number=1,
                    action='Implement consent collection UI',
                    owner='Frontend Developer + UX Designer',
                    timeline='Week 1-2',
                    success_criteria='Users can provide explicit, informed consent before data collection',
                    resources_needed=['Consent management library', 'UI components', 'Database schema']
                ),
                RemediationStep(
                    step_number=2,
                    action='Build consent storage and tracking system',
                    owner='Backend Developer + DBA',
                    timeline='Week 2-3',
                    success_criteria='All consent records logged with timestamp, IP, and consent details',
                    resources_needed=['Database (PostgreSQL/MongoDB)', 'Audit logging', 'API endpoints']
                ),
                RemediationStep(
                    step_number=3,
                    action='Implement consent withdrawal functionality',
                    owner='Full Stack Developer',
                    timeline='Week 3-4',
                    success_criteria='Users can withdraw consent easily; processing stops automatically',
                    resources_needed=['User portal', 'Backend logic', 'Data deletion workflows']
                ),
                RemediationStep(
                    step_number=4,
                    action='Create consent verification checks',
                    owner='Backend Developer',
                    timeline='Week 4',
                    success_criteria='All data processing checks for valid consent before execution',
                    resources_needed=['Middleware/interceptors', 'Authorization system', 'Testing suite']
                ),
            ],
            
            'technical_requirements': [
                'Consent Management Platform (CMP) - Recommended: OneTrust, Cookiebot, or custom',
                'Database for consent records (PostgreSQL with audit logging)',
                'Frontend consent widgets (cookie banner, preference center)',
                'Backend consent verification middleware',
                'API for consent management (CRUD operations)',
                'Integration with existing authentication system',
            ],
            
            'policy_requirements': [
                'Updated Privacy Policy with clear consent sections',
                'Consent policy document (internal)',
                'Data processing procedures requiring consent checks',
                'Consent withdrawal process documentation',
                'Record-keeping policy for consent evidence',
            ],
            
            'training_requirements': [
                'Legal team: GDPR consent requirements and case law',
                'Developers: Technical implementation of consent mechanisms',
                'Marketing: Consent-compliant marketing practices',
                'Support: Handling consent withdrawal requests',
                'Management: Consent compliance importance and liability',
            ],
            
            'verification_checklist': [
                '☐ Consent is freely given (no forced acceptance)',
                '☐ Consent is specific (granular per purpose)',
                '☐ Consent is informed (clear language, no legalese)',
                '☐ Consent is unambiguous (clear affirmative action)',
                '☐ Easy withdrawal mechanism available',
                '☐ Consent records stored with timestamp and details',
                '☐ Re-consent process for changed purposes',
                '☐ No pre-ticked boxes or implied consent',
                '☐ Processing stops immediately upon withdrawal',
                '☐ Regular consent audits scheduled',
            ],
            
            'documentation': [
                'Consent form designs and copies',
                'Consent records database schema',
                'Consent processing workflows (flowcharts)',
                'Legal basis assessment documentation',
                'Consent withdrawal procedure',
                'Staff training records',
                'Consent audit reports',
            ],
            
            'monitoring': 'Monthly consent audit: verify new consents are valid, check withdrawal requests processed within 24h, review consent records completeness',
            
            'best_practices': [
                'Use clear, plain language (not legal jargon)',
                'Separate consent from T&Cs (unbundling)',
                'Provide granular options (marketing, analytics, etc.)',
                'Make withdrawal as easy as giving consent',
                'Keep consent records for proof of compliance',
                'Regularly review and refresh consent',
                'Use double opt-in for email marketing',
            ],
            
            'resources': [
                'ICO Guidance on Consent: https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/consent/',
                'EDPB Guidelines on Consent: https://edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en',
                'Consent Management Platform comparison',
                'Sample consent forms and templates',
            ],
            
            'similar_cases': [
                'Google Ireland €90M fine (2022) - Invalid consent mechanisms',
                'IAB Europe €250k fine (2022) - Transparency & Consent Framework',
                'Amazon €746M fine (2021) - Cookie consent violations',
            ],
        }
    
    def _get_dsr_remediation(self) -> Dict:
        """Remediation for Data Subject Rights violations"""
        return {
            'priority': RemediationPriority.HIGH,
            'complexity': RemediationComplexity.COMPLEX,
            'estimated_effort': '1-3 months',
            'estimated_cost': '$20k-$50k',
            
            'immediate_actions': [
                '📋 Create manual DSR request handling process immediately',
                '📧 Set up dedicated email for DSR requests (e.g., privacy@company.com)',
                '⏰ Implement 30-day response deadline tracking',
                '📊 Audit all systems storing personal data',
            ],
            
            'short_term': [
                '🔧 Build automated DSR request portal',
                '🔍 Implement data discovery and mapping',
                '🗑️ Create data deletion workflows',
                '📦 Build data export functionality (JSON/CSV)',
                '📝 Design DSR verification procedures',
            ],
            
            'long_term': [
                '🤖 Automated DSR processing (AI-assisted)',
                '🌐 Multi-system data orchestration',
                '📈 DSR analytics and reporting',
                '🔄 Continuous data mapping updates',
                '🎯 Proactive data minimization',
            ],
            
            'technical_steps': [
                RemediationStep(
                    step_number=1,
                    action='Implement data export (portability) API',
                    owner='Backend Developer + Data Engineer',
                    timeline='Week 1-3',
                    success_criteria='Users can download all their data in machine-readable format (JSON/CSV)',
                    resources_needed=['Data export service', 'Format converters', 'API endpoints']
                ),
                RemediationStep(
                    step_number=2,
                    action='Build data deletion workflow',
                    owner='Backend Developer + DBA',
                    timeline='Week 3-6',
                    success_criteria='Complete data erasure across all systems within 30 days of request',
                    resources_needed=['Deletion scripts', 'Cross-system orchestration', 'Audit logging']
                ),
                RemediationStep(
                    step_number=3,
                    action='Create DSR request portal',
                    owner='Full Stack Developer',
                    timeline='Week 6-8',
                    success_criteria='Users can submit and track DSR requests through self-service portal',
                    resources_needed=['Frontend UI', 'Request management system', 'Status tracking']
                ),
                RemediationStep(
                    step_number=4,
                    action='Implement identity verification for DSRs',
                    owner='Security Engineer',
                    timeline='Week 8-10',
                    success_criteria='Robust verification prevents unauthorized access to personal data',
                    resources_needed=['2FA system', 'ID verification service', 'Security protocols']
                ),
            ],
            
            'technical_requirements': [
                'DSR management platform or custom portal',
                'Data discovery and mapping tools',
                'Cross-system data deletion orchestration',
                'Data export/portability functionality',
                'Identity verification system (2FA, ID checks)',
                'Secure data transmission (encryption)',
                'Audit logging for all DSR actions',
            ],
            
            'policy_requirements': [
                'Data Subject Rights policy document',
                'DSR request handling procedures',
                'Identity verification procedures',
                'Data retention and deletion policy',
                'Escalation procedures for complex requests',
                'Response templates for each DSR type',
            ],
            
            'training_requirements': [
                'Support team: Handling DSR requests professionally',
                'Legal team: Complex DSR scenarios and exceptions',
                'IT team: Technical implementation of data deletion',
                'Management: Legal obligations and timelines',
            ],
            
            'verification_checklist': [
                '☐ DSR request portal accessible and functional',
                '☐ Response within 30 days (or communicate extension)',
                '☐ Identity verification for all requests',
                '☐ Data export in machine-readable format',
                '☐ Complete data deletion across ALL systems',
                '☐ Confirmation sent to data subject',
                '☐ Audit log of all DSR actions',
                '☐ Exceptions properly documented and justified',
                '☐ Third-party processors notified of deletion',
                '☐ Backups handled appropriately',
            ],
            
            'documentation': [
                'DSR request logs and responses',
                'Identity verification records',
                'Data deletion confirmation certificates',
                'System inventory for data discovery',
                'DSR processing workflows',
                'Training materials and records',
            ],
            
            'monitoring': 'Weekly DSR tracking: check response times, verify deletions complete, review rejection reasons, analyze trends',
            
            'best_practices': [
                'Respond promptly (under 30 days)',
                'Make submission easy (online portal, email, mail)',
                'Verify identity securely (prevent fraud)',
                'Provide free DSR processing (first request)',
                'Export data in common formats (JSON, CSV, PDF)',
                'Delete thoroughly (including backups where feasible)',
                'Communicate clearly throughout process',
            ],
            
            'resources': [
                'ICO Guidance on Individual Rights: https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/',
                'EDPB Guidelines on Right to Erasure',
                'DSR automation platforms comparison',
                'Sample DSR request forms',
            ],
            
            'similar_cases': [
                'British Airways €22.5M fine (2020) - Failed to implement DSR properly',
                'H&M €35.3M fine (2020) - Inadequate data deletion',
            ],
        }
    
    def _get_erasure_remediation(self) -> Dict:
        """Specific remediation for Article 17 - Right to Erasure"""
        return {
            'priority': RemediationPriority.CRITICAL,
            'complexity': RemediationComplexity.COMPLEX,
            'estimated_effort': '2-6 weeks',
            'estimated_cost': '$15k-$40k',
            
            'immediate_actions': [
                '🚨 Create emergency data deletion process (manual if needed)',
                '📧 Set up privacy@company email for deletion requests',
                '🔍 Audit all systems storing personal data',
                '⏰ Track 30-day deadline for each request',
            ],
            
            'short_term': [
                '🗑️ Build automated data deletion workflow',
                '🔍 Implement data discovery tools (find all user data)',
                '📱 Add "Delete My Data" button to user accounts',
                '✅ Create deletion verification process',
                '📝 Set up deletion confirmation emails',
            ],
            
            'long_term': [
                '🤖 AI-powered data discovery across systems',
                '🔄 Automated deletion propagation to third parties',
                '📊 Deletion analytics and compliance reporting',
                '🎯 Proactive data minimization',
            ],
            
            'technical_steps': [
                RemediationStep(
                    step_number=1,
                    action='Build data deletion API and workflows',
                    owner='Backend Developer + DBA',
                    timeline='Week 1-3',
                    success_criteria='Complete data erasure across databases within 30 days',
                    resources_needed=['Deletion scripts', 'Cross-system orchestration', 'Backup handling'],
                ),
                RemediationStep(
                    step_number=2,
                    action='Implement user-facing deletion interface',
                    owner='Frontend Developer',
                    timeline='Week 2-4',
                    success_criteria='Users can request and track deletion through self-service portal',
                    resources_needed=['UI components', 'API integration', 'Status tracking'],
                ),
            ],
            
            'technical_requirements': [
                'Data deletion orchestration system',
                'Cross-database deletion scripts (SQL, NoSQL, etc.)',
                'Third-party notification system (processors, partners)',
                'Backup and archive handling procedures',
                'Deletion audit logging',
                'Identity verification before deletion',
            ],
            
            'policy_requirements': [
                'Data deletion policy (timelines, exceptions)',
                'Third-party processor agreements (deletion clauses)',
                'Backup retention vs. deletion balance',
                'Legal hold procedures (if applicable)',
            ],
            
            'training_requirements': [
                'Support: Handling deletion requests sensitively',
                'IT: Technical deletion execution',
                'Legal: Exceptions and legal obligations',
            ],
            
            'verification_checklist': [
                '☐ Deletion completed within 30 days',
                '☐ All systems checked (production, backups, logs)',
                '☐ Third parties notified of deletion',
                '☐ Confirmation sent to user',
                '☐ Deletion audit trail maintained',
                '☐ Exceptions properly documented (legal requirements)',
            ],
            
            'documentation': [
                'Deletion request logs',
                'Deletion confirmation records',
                'Exceptions log (with legal justification)',
            ],
            
            'monitoring': 'Weekly deletion request tracking: response times, completion rates, exceptions',
            
            'best_practices': [
                'Delete data, not just mark as deleted',
                'Include backups where feasible',
                'Notify third parties within 7 days',
                'Make deletion as easy as signup',
                'Provide deletion confirmation',
            ],
            
            'resources': [
                'ICO Guidance on Right to Erasure',
                'EDPB Guidelines on Right to Erasure',
            ],
            
            'similar_cases': [
                'Google Spain SL case (2014) - Established "right to be forgotten"',
                'H&M €35.3M fine (2020) - Inadequate deletion practices',
            ],
        }
    
    def _get_objection_remediation(self) -> Dict:
        """Specific remediation for Article 21 - Right to Object (especially marketing)"""
        return {
            'priority': RemediationPriority.HIGH,
            'complexity': RemediationComplexity.MODERATE,
            'estimated_effort': '1-3 weeks',
            'estimated_cost': '$5k-$20k',
            
            'immediate_actions': [
                '📧 Add unsubscribe link to ALL marketing emails immediately',
                '🚨 Stop processing for objected users',
                '📋 Create manual opt-out tracking system',
                '🔍 Audit all marketing channels',
            ],
            
            'short_term': [
                '🎯 Build preference center (granular opt-outs)',
                '🔧 Implement automated suppression lists',
                '📱 Add opt-out to mobile apps and SMS',
                '✅ Create objection confirmation workflow',
                '🔄 Sync opt-outs across all marketing tools',
            ],
            
            'long_term': [
                '🤖 Automated objection detection (unsubscribe, complaints)',
                '📊 Preference analytics and respect metrics',
                '🌍 Multi-channel unified preference management',
                '🎯 Proactive preference updates',
            ],
            
            'technical_steps': [
                RemediationStep(
                    step_number=1,
                    action='Implement marketing suppression system',
                    owner='Marketing Engineer + Backend Dev',
                    timeline='Week 1-2',
                    success_criteria='Objections honored within 24h across all channels',
                    resources_needed=['Suppression database', 'Marketing platform integration', 'API endpoints'],
                ),
                RemediationStep(
                    step_number=2,
                    action='Build user preference center',
                    owner='Full Stack Developer',
                    timeline='Week 2-3',
                    success_criteria='Users can manage all marketing preferences in one place',
                    resources_needed=['Frontend UI', 'Backend API', 'Marketing tool integrations'],
                ),
            ],
            
            'technical_requirements': [
                'Marketing suppression database',
                'Real-time sync across marketing platforms (email, SMS, ads, etc.)',
                'Unsubscribe link generator',
                'Preference center interface',
                'Objection audit logging',
            ],
            
            'policy_requirements': [
                'Marketing objection policy (24h processing)',
                'Preference retention policy',
                'Third-party advertiser contracts (objection clauses)',
            ],
            
            'training_requirements': [
                'Marketing: Respecting objections and preferences',
                'Sales: Not contacting opted-out users',
                'Support: Handling objection requests',
            ],
            
            'verification_checklist': [
                '☐ Unsubscribe link in every marketing email',
                '☐ One-click unsubscribe (no login required)',
                '☐ Objection honored within 24 hours',
                '☐ All marketing channels respect objections',
                '☐ Clear confirmation sent to user',
                '☐ No re-targeting after objection',
            ],
            
            'documentation': [
                'Objection request logs',
                'Suppression list records',
                'Marketing channel sync confirmations',
            ],
            
            'monitoring': 'Daily: Check unsubscribe processing time, verify suppression list sync, monitor complaints',
            
            'best_practices': [
                'One-click unsubscribe (CAN-SPAM compliant)',
                'Honor objections immediately (max 24h)',
                'Granular preferences (not all-or-nothing)',
                'Easy to find preference center',
                'Respect objections permanently',
            ],
            
            'resources': [
                'ICO Guidance on Right to Object',
                'EDPB Guidelines on Article 21',
                'CAN-SPAM Act compliance (for US)',
            ],
            
            'similar_cases': [
                'WhatsApp €225M fine (2021) - Inadequate info on processing, including objection rights',
                'Google €50M fine (2019) - Lack of transparency for ads personalization',
            ],
        }
    
    def _get_access_remediation(self) -> Dict:
        """Specific remediation for Article 15 - Right of Access"""
        return {
            'priority': RemediationPriority.HIGH,
            'complexity': RemediationComplexity.MODERATE,
            'estimated_effort': '2-4 weeks',
            'estimated_cost': '$10k-$25k',
            
            'immediate_actions': [
                '📧 Create manual data export process',
                '📝 Set up access request email',
                '⏰ Track 30-day response deadline',
                '🔍 Audit what data you hold',
            ],
            
            'short_term': [
                '📦 Build automated data export functionality',
                '🎯 Create "Download My Data" feature',
                '📄 Format exports as JSON/CSV',
                '✅ Add identity verification',
            ],
            
            'long_term': [
                '📊 Real-time data dashboard for users',
                '🔄 Automated data aggregation',
                '🤖 AI-assisted data discovery',
            ],
            
            'technical_steps': [],
            'technical_requirements': [
                'Data export API',
                'Multiple format support (JSON, CSV, PDF)',
                'Identity verification',
            ],
            'policy_requirements': ['Access request procedures'],
            'training_requirements': ['Support team: Handling access requests'],
            'verification_checklist': [
                '☐ Response within 30 days',
                '☐ All personal data included',
                '☐ Machine-readable format',
            ],
            'documentation': ['Access request logs'],
            'monitoring': 'Monthly access request tracking',
            'best_practices': ['Respond promptly', 'Provide complete data'],
            'resources': ['ICO Guidance on Right of Access'],
            'similar_cases': [],
        }
    
    def _get_portability_remediation(self) -> Dict:
        """Specific remediation for Article 20 - Right to Data Portability"""
        return {
            'priority': RemediationPriority.MEDIUM,
            'complexity': RemediationComplexity.MODERATE,
            'estimated_effort': '2-4 weeks',
            'estimated_cost': '$10k-$25k',
            
            'immediate_actions': [
                '📦 Create manual export process in portable format',
                '📝 Document current data formats',
            ],
            
            'short_term': [
                '🔧 Build structured export (JSON/CSV)',
                '📱 Add "Export to Another Service" feature',
            ],
            
            'long_term': [
                '🔄 Direct transfer to other controllers',
                '🤖 Automated portable format conversion',
            ],
            
            'technical_steps': [],
            'technical_requirements': ['Structured data export', 'Common formats (JSON, CSV)'],
            'policy_requirements': ['Data portability policy'],
            'training_requirements': [],
            'verification_checklist': [
                '☐ Structured, machine-readable format',
                '☐ Commonly used format',
            ],
            'documentation': [],
            'monitoring': 'Quarterly portability request review',
            'best_practices': ['Use standard formats', 'Include all user-provided data'],
            'resources': [],
            'similar_cases': [],
        }
    
    def _get_transparency_remediation(self) -> Dict:
        """Remediation for transparency violations"""
        return {
            'priority': RemediationPriority.HIGH,
            'complexity': RemediationComplexity.MODERATE,
            'estimated_effort': '3-6 weeks',
            'estimated_cost': '$5k-$20k',
            
            'immediate_actions': [
                '📝 Create basic privacy notice immediately',
                '🔍 Audit all data collection points',
                '📧 Identify all communications needing privacy info',
                '⚠️ Add temporary privacy notices to high-risk areas',
            ],
            
            'short_term': [
                '📄 Comprehensive privacy policy (GDPR-compliant)',
                '🎨 Privacy notices at all collection points',
                '📱 Mobile app privacy screens',
                '🍪 Cookie notice and preference center',
                '📊 Data processing records (Article 30)',
            ],
            
            'long_term': [
                '🌍 Multi-language privacy notices',
                '♿ Accessible formats (audio, easy-read)',
                '📈 Privacy dashboard for users',
                '🔄 Automated privacy notice updates',
                '🎯 Just-in-time privacy notices',
            ],
            
            'verification_checklist': [
                '☐ Identity and contact details of controller',
                '☐ Data Protection Officer contact (if applicable)',
                '☐ Purposes of processing clearly stated',
                '☐ Legal basis for each purpose',
                '☐ Legitimate interests explained (if applicable)',
                '☐ Recipients or categories of recipients',
                '☐ International transfers disclosed',
                '☐ Retention periods specified',
                '☐ Data subject rights listed',
                '☐ Right to withdraw consent explained',
                '☐ Right to lodge complaint',
                '☐ Automated decision-making disclosed',
                '☐ Source of data (if not from subject)',
            ],
            
            'best_practices': [
                'Use plain language (8th-grade reading level)',
                'Layer information (summary + detailed)',
                'Make easily accessible (prominent links)',
                'Update regularly and notify changes',
                'Provide multiple formats (web, PDF, print)',
                'Include last updated date',
                'Test readability with users',
            ],
        }
    
    def _get_breach_remediation(self) -> Dict:
        """Remediation for data breach violations"""
        return {
            'priority': RemediationPriority.CRITICAL,
            'complexity': RemediationComplexity.MAJOR,
            'estimated_effort': 'Immediate + ongoing',
            'estimated_cost': '$50k-$200k+',
            
            'immediate_actions': [
                '🚨 STOP THE BREACH - Contain immediately',
                '📞 Notify supervisory authority within 72 hours',
                '📧 Notify affected individuals if high risk',
                '🔍 Preserve evidence for investigation',
                '⚖️ Engage legal counsel and cyber insurance',
                '📊 Begin incident documentation',
            ],
            
            'short_term': [
                '🔒 Implement immediate security fixes',
                '🔍 Full forensic investigation',
                '📢 Transparent communication with stakeholders',
                '🛡️ Credit monitoring for affected individuals (if applicable)',
                '📝 Detailed incident report to DPA',
                '🔧 Remediate root cause vulnerabilities',
            ],
            
            'long_term': [
                '🏢 Comprehensive security overhaul',
                '🎯 Implement breach prevention controls',
                '📚 Staff security training program',
                '🔄 Regular penetration testing',
                '📈 Security monitoring and SIEM',
                '🤝 Incident response plan and drills',
            ],
            
            'technical_requirements': [
                'Incident response platform',
                'Forensic analysis tools',
                'Security monitoring (SIEM)',
                'Encryption for data at rest and in transit',
                'Access controls and authentication',
                'Breach notification system',
                'Backup and recovery systems',
            ],
            
            'verification_checklist': [
                '☐ Breach contained and stopped',
                '☐ DPA notified within 72 hours',
                '☐ Individuals notified if high risk',
                '☐ Full extent of breach determined',
                '☐ Root cause identified',
                '☐ Remediation implemented',
                '☐ Evidence preserved',
                '☐ All required parties notified',
                '☐ Lessons learned documented',
                '☐ Prevention measures implemented',
            ],
            
            'best_practices': [
                'Notify DPA within 72 hours (even if investigation ongoing)',
                'Document everything (timeline, actions, decisions)',
                'Be transparent (don\'t downplay severity)',
                'Offer assistance to affected individuals',
                'Work with DPA cooperatively',
                'Learn and improve security posture',
                'Regular incident response drills',
            ],
        }
    
    def _map_to_template(self, category: str, articles: List[str]) -> str:
        """Map violation to remediation template with article-specific guidance"""
        category_lower = category.lower()
        
        # Prioritize article-specific mapping first for more accurate guidance
        articles_str = ' '.join(articles)
        
        # Specific article mappings (most specific first)
        if 'Article 17' in articles_str:
            return 'erasure_rights'  # Right to erasure/deletion
        elif 'Article 21' in articles_str:
            return 'objection_rights'  # Right to object (especially marketing)
        elif 'Article 15' in articles_str:
            return 'access_rights'  # Right to access
        elif 'Article 20' in articles_str:
            return 'portability_rights'  # Data portability
        elif 'Article 6' in articles_str or 'Article 7' in articles_str:
            return 'consent_violation'
        elif 'Article 33' in articles_str or 'Article 34' in articles_str:
            return 'data_breach'
        elif 'Article 13' in articles_str or 'Article 14' in articles_str:
            return 'transparency'
        elif 'Article 32' in articles_str:
            return 'security'
        
        # Category-based fallback (less specific)
        if 'consent' in category_lower:
            return 'consent_violation'
        elif 'erasure' in category_lower or 'deletion' in category_lower:
            return 'erasure_rights'
        elif 'objection' in category_lower or 'marketing' in category_lower:
            return 'objection_rights'
        elif 'access' in category_lower:
            return 'access_rights'
        elif 'breach' in category_lower:
            return 'data_breach'
        elif 'transparency' in category_lower or 'information' in category_lower:
            return 'transparency'
        elif 'transfer' in category_lower:
            return 'data_transfer'
        elif 'security' in category_lower:
            return 'security'
        
        return 'data_subject_rights'  # Generic DSR fallback
    
    def _customize_remediation(self, template: Dict, severity: str, context: str) -> RemediationGuidance:
        """Customize template based on severity and context"""
        # Adjust priority based on severity
        if severity.lower() == 'critical':
            priority = RemediationPriority.CRITICAL
        elif severity.lower() == 'high':
            priority = RemediationPriority.HIGH
        elif severity.lower() == 'medium':
            priority = RemediationPriority.MEDIUM
        else:
            priority = RemediationPriority.LOW
        
        return RemediationGuidance(
            violation_category=template.get('category', 'GDPR Violation'),
            affected_articles=template.get('articles', []),
            priority=template.get('priority', priority),
            complexity=template.get('complexity', RemediationComplexity.MODERATE),
            estimated_effort=template.get('estimated_effort', '2-4 weeks'),
            immediate_actions=template.get('immediate_actions', []),
            short_term_solutions=template.get('short_term', []),
            long_term_improvements=template.get('long_term', []),
            detailed_steps=template.get('technical_steps', []),
            technical_requirements=template.get('technical_requirements', []),
            policy_requirements=template.get('policy_requirements', []),
            training_requirements=template.get('training_requirements', []),
            estimated_cost_range=template.get('estimated_cost', 'Variable'),
            required_roles=self._extract_roles(template.get('technical_steps', [])),
            verification_checklist=template.get('verification_checklist', []),
            documentation_needed=template.get('documentation', []),
            ongoing_monitoring=template.get('monitoring', ''),
            best_practices=template.get('best_practices', []),
            helpful_resources=template.get('resources', []),
            similar_cases=template.get('similar_cases', []),
        )
    
    def _extract_roles(self, steps: List[RemediationStep]) -> List[str]:
        """Extract unique roles from steps"""
        roles = set()
        for step in steps:
            if hasattr(step, 'owner'):
                roles.add(step.owner)
        return list(roles)
    
    def _generate_generic_remediation(self, category: str, articles: List[str], severity: str) -> RemediationGuidance:
        """Generate generic remediation for unknown violations"""
        return RemediationGuidance(
            violation_category=category,
            affected_articles=articles,
            priority=RemediationPriority.HIGH,
            complexity=RemediationComplexity.MODERATE,
            estimated_effort='2-4 weeks',
            immediate_actions=[
                '🔍 Conduct detailed compliance assessment',
                '⚖️ Consult with legal counsel',
                '📊 Audit affected systems and processes',
                '📝 Document current state and gaps',
            ],
            short_term_solutions=[
                '🔧 Implement technical controls',
                '📄 Update policies and procedures',
                '🎓 Train staff on requirements',
                '✅ Verify compliance',
            ],
            long_term_improvements=[
                '📈 Ongoing monitoring and auditing',
                '🔄 Continuous improvement program',
                '🎯 Proactive compliance measures',
            ],
            detailed_steps=[],
            technical_requirements=[],
            policy_requirements=[],
            training_requirements=[],
            estimated_cost_range='Variable',
            required_roles=['Legal Counsel', 'Compliance Officer', 'IT Team'],
            verification_checklist=[],
            documentation_needed=[],
            ongoing_monitoring='Regular compliance audits',
            best_practices=[],
            helpful_resources=[],
            similar_cases=[],
        )
    
    def _get_transfer_remediation(self) -> Dict:
        """Remediation for international data transfer violations"""
        return self._get_generic_template('International Data Transfer')
    
    def _get_security_remediation(self) -> Dict:
        """Remediation for security violations"""
        return self._get_generic_template('Data Security')
    
    def _get_accountability_remediation(self) -> Dict:
        """Remediation for accountability violations"""
        return self._get_generic_template('Accountability')
    
    def _get_legal_basis_remediation(self) -> Dict:
        """Remediation for legal basis violations"""
        return self._get_generic_template('Legal Basis')
    
    def _get_retention_remediation(self) -> Dict:
        """Remediation for data retention violations"""
        return self._get_generic_template('Data Retention')
    
    def _get_dpo_remediation(self) -> Dict:
        """Remediation for DPO requirement violations"""
        return self._get_generic_template('Data Protection Officer')
    
    def _get_generic_template(self, category: str) -> Dict:
        """Generic template for violations without specific guidance"""
        return {
            'category': category,
            'articles': [],
            'priority': RemediationPriority.HIGH,
            'complexity': RemediationComplexity.MODERATE,
            'estimated_effort': '2-4 weeks',
            'estimated_cost': '$10k-$30k',
            
            'immediate_actions': [
                '🔍 Conduct detailed compliance assessment',
                '⚖️ Consult with legal counsel',
                '📊 Audit affected systems and processes',
                '📝 Document current state and gaps',
            ],
            
            'short_term': [
                '🔧 Implement technical controls',
                '📄 Update policies and procedures',
                '🎓 Train staff on requirements',
                '✅ Verify compliance',
            ],
            
            'long_term': [
                '📈 Ongoing monitoring and auditing',
                '🔄 Continuous improvement program',
                '🎯 Proactive compliance measures',
            ],
            
            'technical_steps': [],
            'technical_requirements': [],
            'policy_requirements': [],
            'training_requirements': [],
            'verification_checklist': [],
            'documentation': [],
            'monitoring': 'Regular compliance audits',
            'best_practices': [],
            'resources': [],
            'similar_cases': [],
        }
