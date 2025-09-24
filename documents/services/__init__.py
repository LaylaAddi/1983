# documents/services/__init__.py

# Import all the refactored services
from .violation_analysis_service import ViolationAnalysisService
from .template_matching_service import TemplateMatchingService
from .section_generation_service import SectionGenerationService
from .document_orchestrator_service import DocumentOrchestratorService

# Import the legacy service for backwards compatibility
from ..document_services import LegalDocumentPopulator

# Expose all services at package level
__all__ = [
    'ViolationAnalysisService',
    'TemplateMatchingService', 
    'SectionGenerationService',
    'DocumentOrchestratorService',
    'LegalDocumentPopulator',  # Keep for backwards compatibility
]