# documents/urls.py
from django.urls import path
from . import views_main
from .views import section_views

urlpatterns = [
    # Document CRUD
    path('', views_main.document_list, name='document_list'),
    path('create/', views_main.document_create, name='document_create'),
    path('<int:pk>/', views_main.document_detail, name='document_detail'),
    path('<int:pk>/edit/', views_main.document_edit, name='document_edit'),
    path('<int:pk>/delete/', views_main.document_delete, name='document_delete'),
    
    # Document status update
    path('<int:pk>/status/', views_main.document_status_update, name='document_status_update'),
    
    # Legal sections
    path('<int:pk>/auto-populate/', views_main.auto_populate_legal_sections, name='auto_populate_legal'),
    path('<int:pk>/generate-default/', views_main.generate_default_sections, name='generate_default_sections'),
    path('<int:pk>/sections/', section_views.manage_document_sections, name='manage_document_sections'),
    path('<int:pk>/sections/template/', section_views.insert_template_section, name='insert_template_section'),
    path('<int:pk>/sections/blank/', section_views.add_blank_section, name='add_blank_section'),
    
    # Document preview
    path('<int:pk>/preview/', views_main.document_preview, name='document_preview'),
]