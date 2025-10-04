# documents/views/__init__.py

# all existing views from the main views.py file
from .voice_views import voice_recorder_view
from .voice_views import voice_recorder_view, voice_create_document


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