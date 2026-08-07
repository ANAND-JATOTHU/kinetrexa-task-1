from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import HttpResponse, FileResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime

from .models import Student, Attendance, UserProfile
from .forms import StudentForm, CSVUploadForm, AttendanceForm
from .services import handle_csv_upload, export_students_csv, export_attendance_csv, generate_student_pdf

class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = ['admin']

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        profile = getattr(user, 'profile', None)
        if not profile:
            return False
        return profile.role in self.allowed_roles

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'students/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        # Redirect student users directly to their student self-service portal
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_student:
            return redirect('student-portal')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, 'profile', None)
        is_teacher = profile.is_teacher if profile else False
        
        students = Student.objects.all()
        context['total_students'] = students.count()
        context['active_students'] = students.filter(is_active=True).count()
        context['inactive_students'] = students.filter(is_active=False).count()
        
        avg_gpa = students.aggregate(Avg('gpa'))['gpa__avg']
        context['average_gpa'] = round(avg_gpa, 2) if avg_gpa else 0
        
        # Overall Attendance Stats
        total_attendance = Attendance.objects.count()
        present_count = Attendance.objects.filter(status='Present').count()
        late_count = Attendance.objects.filter(status='Late').count()
        
        if total_attendance > 0:
            effective_present = present_count + (late_count * 0.5)
            context['overall_attendance_pct'] = round((effective_present / total_attendance) * 100, 1)
        else:
            context['overall_attendance_pct'] = 0.0

        # Department breakdown
        departments = {}
        for s in students:
            departments[s.department] = departments.get(s.department, 0) + 1
        context['departments'] = departments
        
        # Today's attendance status
        today = timezone.localdate()
        today_attendance = Attendance.objects.filter(date=today)
        context['today_marked_count'] = today_attendance.count()
        context['today_date'] = today
        
        # Recent Attendance logs
        context['recent_attendances'] = Attendance.objects.select_related('student', 'marked_by')[:8]
        context['is_teacher'] = is_teacher
        context['user_profile'] = profile
        
        return context

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        queryset = Student.objects.all().order_by('-created_at')
        search_query = self.request.GET.get('q')
        department = self.request.GET.get('dept')
        
        if search_query:
            queryset = queryset.filter(
                Q(roll_number__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(department__icontains=search_query)
            )
        if department:
            queryset = queryset.filter(department=department)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_dept'] = self.request.GET.get('dept', '')
        context['departments'] = Student.objects.values_list('department', flat=True).distinct()
        profile = getattr(self.request.user, 'profile', None)
        context['is_admin'] = profile.is_admin if profile else self.request.user.is_superuser
        context['is_teacher'] = profile.is_teacher if profile else False
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        context['attendance_stats'] = student.get_attendance_stats()
        context['recent_attendance'] = student.attendance_records.all()[:10]
        profile = getattr(self.request.user, 'profile', None)
        context['is_admin'] = profile.is_admin if profile else self.request.user.is_superuser
        context['is_teacher'] = profile.is_teacher if profile else False
        return context

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

class MarkAttendanceView(LoginRequiredMixin, View):
    template_name = 'students/mark_attendance.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        # Verify user is teacher or admin
        if profile and profile.is_student:
            messages.error(request, "Students are not authorized to mark attendance.")
            return redirect('student-portal')

        # Selected filters
        selected_dept = request.GET.get('department', '')
        if not selected_dept and profile and profile.is_teacher and profile.department:
            selected_dept = profile.department

        date_str = request.GET.get('date', '')
        if date_str:
            try:
                selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.localdate()
        else:
            selected_date = timezone.localdate()

        # Query students
        students = Student.objects.filter(is_active=True).order_by('department', 'roll_number')
        if selected_dept:
            students = students.filter(department=selected_dept)

        # Existing records on this date
        existing_records = {
            att.student_id: att
            for att in Attendance.objects.filter(date=selected_date, student__in=students)
        }

        # Build student roster with current status
        roster = []
        for s in students:
            record = existing_records.get(s.id)
            roster.append({
                'student': s,
                'status': record.status if record else 'Present',
                'remarks': record.remarks if record else '',
                'is_saved': record is not None,
            })

        departments = Student.objects.values_list('department', flat=True).distinct()

        context = {
            'roster': roster,
            'selected_dept': selected_dept,
            'selected_date': selected_date.strftime('%Y-%m-%d'),
            'departments': departments,
            'total_students': len(roster),
            'saved_count': len(existing_records),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_student:
            messages.error(request, "Students are not authorized to mark attendance.")
            return redirect('student-portal')

        date_str = request.POST.get('date')
        selected_dept = request.POST.get('department', '')
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = timezone.localdate()

        student_ids = request.POST.getlist('student_ids')
        saved_count = 0

        for s_id in student_ids:
            try:
                student = Student.objects.get(pk=s_id)
                status = request.POST.get(f'status_{s_id}', 'Present')
                remarks = request.POST.get(f'remarks_{s_id}', '').strip()

                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user
                    }
                )
                saved_count += 1
            except Student.DoesNotExist:
                continue

        messages.success(request, f"Successfully saved attendance for {saved_count} students on {selected_date.strftime('%b %d, %Y')}.")
        return redirect(f"{reverse_lazy('mark-attendance')}?department={selected_dept}&date={selected_date.strftime('%Y-%m-%d')}")

class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'students/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 20

    def get_queryset(self):
        queryset = Attendance.objects.select_related('student', 'marked_by').order_by('-date', 'student__roll_number')
        
        search_query = self.request.GET.get('q')
        department = self.request.GET.get('dept')
        status = self.request.GET.get('status')
        date_filter = self.request.GET.get('date')

        if search_query:
            queryset = queryset.filter(
                Q(student__roll_number__icontains=search_query) |
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query)
            )
        if department:
            queryset = queryset.filter(student__department=department)
        if status:
            queryset = queryset.filter(status=status)
        if date_filter:
            try:
                d = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(date=d)
            except ValueError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_dept'] = self.request.GET.get('dept', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_date'] = self.request.GET.get('date', '')
        context['departments'] = Student.objects.values_list('department', flat=True).distinct()
        context['status_choices'] = ['Present', 'Absent', 'Late', 'Excused']
        
        profile = getattr(self.request.user, 'profile', None)
        context['is_admin'] = profile.is_admin if profile else self.request.user.is_superuser
        context['is_teacher'] = profile.is_teacher if profile else False
        return context

class StudentPortalView(LoginRequiredMixin, TemplateView):
    template_name = 'students/student_portal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = getattr(user, 'profile', None)
        
        # Identify student object
        student = None
        if profile and profile.student:
            student = profile.student
        else:
            # Try to match student by email
            student = Student.objects.filter(email=user.email).first()
            if not student and (user.is_superuser or (profile and profile.is_admin)):
                # If admin is testing the student portal, show first student
                student = Student.objects.first()

        context['student'] = student
        if student:
            context['attendance_stats'] = student.get_attendance_stats()
            context['attendance_records'] = student.attendance_records.all().order_by('-date')
        return context

@login_required
def upload_csv(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.is_student:
        messages.error(request, "Access restricted.")
        return redirect('student-portal')

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
    department = request.GET.get('dept')
    if search_query:
        queryset = queryset.filter(
            Q(roll_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    if department:
        queryset = queryset.filter(department=department)
    return export_students_csv(queryset)

@login_required
def export_attendance_csv_view(request):
    queryset = Attendance.objects.select_related('student', 'marked_by').order_by('-date', 'student__roll_number')
    
    search_query = request.GET.get('q')
    department = request.GET.get('dept')
    status = request.GET.get('status')
    date_filter = request.GET.get('date')

    if search_query:
        queryset = queryset.filter(
            Q(student__roll_number__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query)
        )
    if department:
        queryset = queryset.filter(student__department=department)
    if status:
        queryset = queryset.filter(status=status)
    if date_filter:
        try:
            d = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
            queryset = queryset.filter(date=d)
        except ValueError:
            pass

    return export_attendance_csv(queryset)

@login_required
def download_pdf(request, pk):
    try:
        student = Student.objects.get(pk=pk)
        # Check permission: if student user, make sure they only download their own
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_student and profile.student and profile.student.pk != student.pk:
            messages.error(request, "You can only download your own ID card.")
            return redirect('student-portal')

        buffer = generate_student_pdf(student)
        return FileResponse(buffer, as_attachment=True, filename=f"student_{student.roll_number}.pdf")
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('student-list')
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('student-detail', pk=pk)
