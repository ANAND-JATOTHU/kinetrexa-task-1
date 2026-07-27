from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, FileResponse

from .models import Student
from .forms import StudentForm, CSVUploadForm
from .services import handle_csv_upload, export_students_csv, generate_student_pdf

class StudentListView(ListView):
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

class StudentDetailView(DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student-list')

    def form_valid(self, form):
        messages.success(self.request, 'Student created successfully!')
        return super().form_valid(form)

class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    
    def get_success_url(self):
        return reverse_lazy('student-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Student updated successfully!')
        return super().form_valid(form)

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Student deleted successfully!')
        return super().delete(request, *args, **kwargs)

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
