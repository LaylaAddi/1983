# documents/urls.py
from django.urls import path
from . import views
from . import views_main
from django.contrib.auth.decorators import login_required
# from .views import transcript_views
from .views import whisper_views
from .views import evidence_views


urlpatterns = [
    path('create/', views.document_create, name='document_create'),
    path('list/', views.document_list, name='document_list'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
    path('<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('<int:pk>/status/', views.document_status_update, name='document_status_update'),
    path('documents/<int:pk>/auto-populate/', views.auto_populate_legal_sections, name='auto_populate_legal'),
    path('<int:pk>/sections/', views.manage_document_sections, name='manage_document_sections'),
    path('<int:pk>/sections/template/', views.insert_template_section, name='insert_template_section'),
    path('<int:pk>/sections/blank/', views.add_blank_section, name='add_blank_section'),
    path('<int:pk>/preview/', views.document_preview, name='document_preview'),
    path('<int:pk>/generate-defaults/', views.generate_default_sections, name='generate_default_sections'),
    path('voice-recorder/', views.voice_recorder_view, name='voice_recorder'),
    path('api/voice-create/', views.voice_create_document, name='voice_create_document'),
    path('<int:pk>/download-pdf/', login_required(views_main.DocumentPDFView.as_view()), name='download_pdf'),
    # path('api/extract-transcript-mock/', transcript_views.extract_transcript_mock, name='extract_transcript_mock'),
    path('api/extract-transcript/', whisper_views.extract_transcript_whisper, name='extract_transcript_whisper'),


    # Evidence management URLs
    path('<int:pk>/evidence/', evidence_views.evidence_manager, name='evidence_manager'),
    path('<int:pk>/evidence/extract/', evidence_views.extract_evidence_segment, name='extract_evidence_segment'),
    path('<int:pk>/evidence/<int:segment_id>/update/', evidence_views.update_evidence_segment, name='update_evidence_segment'),
    path('<int:pk>/evidence/<int:segment_id>/delete/', evidence_views.delete_evidence_segment, name='delete_evidence_segment'),
    path('<int:pk>/evidence/add-manual/', evidence_views.add_manual_segment, name='add_manual_segment'),
    path('<int:pk>/evidence/generate-facts/', evidence_views.generate_facts_from_evidence, name='generate_facts_from_evidence'),
    path('<int:pk>/evidence/preview-facts/', evidence_views.preview_facts_from_evidence, name='preview_facts_from_evidence'),

    # Person management URLs (for speaker attribution)
    path('<int:pk>/people/', evidence_views.get_document_people, name='get_document_people'),
    path('<int:pk>/people/add/', evidence_views.add_person, name='add_person'),
    path('<int:pk>/people/<int:person_id>/update/', evidence_views.update_person, name='update_person'),
    path('<int:pk>/people/<int:person_id>/delete/', evidence_views.delete_person, name='delete_person'),
    path('<int:pk>/people/sync/', evidence_views.sync_people_from_defendants, name='sync_people_from_defendants'),

    # Transcript quote management URLs (for highlighting and attribution)
    path('<int:pk>/evidence/<int:segment_id>/quotes/', evidence_views.get_segment_quotes, name='get_segment_quotes'),
    path('<int:pk>/evidence/<int:segment_id>/quotes/add/', evidence_views.add_quote, name='add_quote'),
    path('<int:pk>/evidence/<int:segment_id>/quotes/<int:quote_id>/update/', evidence_views.update_quote, name='update_quote'),
    path('<int:pk>/evidence/<int:segment_id>/quotes/<int:quote_id>/delete/', evidence_views.delete_quote, name='delete_quote'),
]


