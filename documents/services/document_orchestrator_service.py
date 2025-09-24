# documents/services/document_orchestrator_service.py
from .violation_analysis_service import ViolationAnalysisService
from .template_matching_service import TemplateMatchingService
from .section_generation_service import SectionGenerationService

# Coordinates all three services for complete document generation
# Provides enhanced analysis without generating sections
# Offers preview functionality to see what would be generated
# Supports selective updates for individual sections
# Better return data with detailed results


class DocumentOrchestratorService:
    """
    Modern orchestrator service that coordinates the modular services
    to automatically populate legal documents
    """

    def __init__(self, document):
        self.document = document

    def auto_populate_document(self):
        """
        Main method to populate document with appropriate legal templates
        Uses the new modular services for better separation of concerns
        """
        # Step 1: Analyze the document to determine violation and location types
        violation_type = ViolationAnalysisService.analyze_violation_type(
            self.document.description
        )
        location_type = ViolationAnalysisService.analyze_location_type(
            self.document.incident_location
        )

        # Step 2: Find matching templates
        templates = TemplateMatchingService.find_templates(violation_type, location_type)

        # Step 3: Prepare context data for template rendering
        context_data = TemplateMatchingService.prepare_document_context(self.document)

        # Step 4: Generate sections from templates
        results = SectionGenerationService.bulk_generate_sections(
            self.document, templates, context_data
        )

        # Step 5: Ensure proper section ordering
        SectionGenerationService.reorder_sections(self.document)

        # Return comprehensive results
        return {
            'violation_type': violation_type,
            'location_type': location_type,
            'templates_found': templates.count(),
            'sections_created': len([r for r in results if r['created']]),
            'sections_updated': len([r for r in results if not r['created']]),
            'sections': [r['section'] for r in results],
            'context_used': context_data,
            'results_detail': results
        }

    def get_document_analysis(self):
        """Get analysis of document without generating sections"""
        violation_type = ViolationAnalysisService.analyze_violation_type(
            self.document.description
        )
        location_type = ViolationAnalysisService.analyze_location_type(
            self.document.incident_location
        )

        templates = TemplateMatchingService.find_templates(violation_type, location_type)
        available_sections = TemplateMatchingService.get_available_sections(
            violation_type, location_type
        )
        section_stats = SectionGenerationService.get_section_statistics(self.document)

        return {
            'violation_type': violation_type,
            'violation_description': ViolationAnalysisService.get_violation_description(violation_type),
            'location_type': location_type,
            'location_description': ViolationAnalysisService.get_forum_description(location_type),
            'available_templates': templates.count(),
            'available_sections': available_sections,
            'current_sections': section_stats['total_sections'],
            'completion_percentage': section_stats['completion_percentage'],
            'missing_sections': section_stats['missing_sections']
        }

    def preview_sections(self):
        """Preview what sections would be generated without creating them"""
        violation_type = ViolationAnalysisService.analyze_violation_type(
            self.document.description
        )
        location_type = ViolationAnalysisService.analyze_location_type(
            self.document.incident_location
        )

        templates = TemplateMatchingService.find_templates(violation_type, location_type)
        previews = []

        for template in templates:
            preview = TemplateMatchingService.preview_template(
                violation_type, location_type, template.section_type, self.document
            )
            if preview:
                previews.append(preview)

        return {
            'violation_type': violation_type,
            'location_type': location_type,
            'section_previews': previews
        }

    def update_specific_section(self, section_type):
        """Update a specific section type with the latest template"""
        violation_type = ViolationAnalysisService.analyze_violation_type(
            self.document.description
        )
        location_type = ViolationAnalysisService.analyze_location_type(
            self.document.incident_location
        )

        template = TemplateMatchingService.get_template_by_section(
            violation_type, location_type, section_type
        )

        if not template:
            return {
                'success': False,
                'error': f'No template found for {section_type}',
                'violation_type': violation_type,
                'location_type': location_type
            }

        context_data = TemplateMatchingService.prepare_document_context(self.document)
        section, created = SectionGenerationService.create_section_from_template(
            self.document, template, context_data
        )

        return {
            'success': True,
            'section': section,
            'created': created,
            'template_used': template,
            'violation_type': violation_type,
            'location_type': location_type
        }