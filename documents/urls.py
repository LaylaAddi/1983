# documents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.document_create, name='document_create'),
    path('list/', views.document_list, name='document_list'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
    path('<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('<int:pk>/status/', views.document_status_update, name='document_status_update'),
    path('documents/<int:pk>/auto-populate/', views.auto_populate_legal_sections, name='auto_populate_legal'),

]