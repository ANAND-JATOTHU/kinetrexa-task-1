from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('portal/', views.StudentPortalView.as_view(), name='student-portal'),
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('student/new/', views.StudentCreateView.as_view(), name='student-create'),
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('student/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student-update'),
    path('student/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    path('student/<int:pk>/pdf/', views.download_pdf, name='student-pdf'),
    path('attendance/mark/', views.MarkAttendanceView.as_view(), name='mark-attendance'),
    path('attendance/records/', views.AttendanceListView.as_view(), name='attendance-records'),
    path('attendance/export/', views.export_attendance_csv_view, name='export-attendance-csv'),
    path('upload-csv/', views.upload_csv, name='upload-csv'),
    path('export-csv/', views.export_csv, name='export-csv'),
]
