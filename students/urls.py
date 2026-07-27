from django.urls import path
from . import views

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student-list'),
    path('student/new/', views.StudentCreateView.as_view(), name='student-create'),
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('student/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student-update'),
    path('student/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    path('student/<int:pk>/pdf/', views.download_pdf, name='student-pdf'),
    path('upload-csv/', views.upload_csv, name='upload-csv'),
    path('export-csv/', views.export_csv, name='export-csv'),
]
