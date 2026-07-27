from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import HttpResponse, FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Student
from .forms import StudentForm, CSVUploadForm
from .services import handle_csv_upload, export_students_csv, generate_student_pdf

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'students/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = Student.objects.all()
        context['total_students'] = students.count()
        context['active_students'] = students.filter(is_active=True).count()
        context['inactive_students'] = students.filter(is_active=False).count()
        
        avg_gpa = students.aggregate(Avg('gpa'))['gpa__avg']
        context['average_gpa'] = round(avg_gpa, 2) if avg_gpa else 0
        
        # Simple department grouping (could use aggregation, keeping it simple)
        departments = {}
        for s in students:
            departments[s.department] = departments.get(s.department, 0) + 1
        context['departments'] = departments
        
        return context

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        queryset = Student.objects.all().order_by('-created_at')
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(roll_number__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(department__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student-list')

    def form_valid(self, form):
        messages.success(self.request, 'Student created successfully!')
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    
    def get_success_url(self):
        return reverse_lazy('student-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Student updated successfully!')
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Student deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            success, message = handle_csv_upload(request.FILES['csv_file'])
            if success:
                messages.success(request, message)
                return redirect('student-list')
            else:
                messages.error(request, message)
    else:
        form = CSVUploadForm()
    
    return render(request, 'students/upload_csv.html', {'form': form})

@login_required
def export_csv(request):
    queryset = Student.objects.all()
    search_query = request.GET.get('q')
    if search_query:
        queryset = queryset.filter(
            Q(roll_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    return export_students_csv(queryset)

@login_required
def download_pdf(request, pk):
    try:
        student = Student.objects.get(pk=pk)
        buffer = generate_student_pdf(student)
        return FileResponse(buffer, as_attachment=True, filename=f"student_{student.roll_number}.pdf")
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('student-list')
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('student-detail', pk=pk)
