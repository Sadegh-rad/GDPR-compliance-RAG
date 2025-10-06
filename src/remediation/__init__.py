"""
Remediation module for GDPR compliance guidance
"""
from .remediation_engine_dynamic import (
    DynamicRemediationEngine,
    RemediationGuidance,
    RemediationStep,
    RemediationPriority,
    RemediationComplexity
)

# Keep backward compatibility
RemediationEngine = DynamicRemediationEngine

__all__ = [
    'DynamicRemediationEngine',
    'RemediationEngine',
    'RemediationGuidance',
    'RemediationStep',
    'RemediationPriority',
    'RemediationComplexity'
]
