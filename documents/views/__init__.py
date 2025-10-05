# documents/views/__init__.py

# all existing views from the main views.py file
from .voice_views import voice_recorder_view
from .voice_views import voice_recorder_view, voice_create_document

# Transcript views
# from .transcript_views import extract_transcript_mock
from .whisper_views import extract_transcript_whisper


from ..views_main import (
    document_create,
    document_list, 
    document_detail,
    document_edit,
    document_delete,
    document_status_update,
    auto_populate_legal_sections,
    document_preview,
)

# section views
from .section_views import (
    manage_document_sections,
    insert_template_section,
    add_blank_section,
)


from documents.views_main import (
    document_create,
    document_list, 
    document_detail,
    document_edit,
    document_delete,
    document_status_update,
    auto_populate_legal_sections,
    document_preview,
    generate_default_sections, 
    DocumentPDFView,
)


from .evidence_views import (
    evidence_manager,
    extract_evidence_segment,
    update_evidence_segment,
    delete_evidence_segment,
    add_manual_segment,
    generate_facts_from_evidence,
    preview_facts_from_evidence,
)