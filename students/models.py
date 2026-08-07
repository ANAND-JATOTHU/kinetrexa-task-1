from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class StudentManager(models.Manager):
    def get_active_students(self):
        return self.filter(is_active=True)

class Student(TimeStampedModel):
    roll_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = StudentManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_grade(self):
        if self.gpa >= 3.5:
            return 'A'
        elif self.gpa >= 3.0:
            return 'B'
        elif self.gpa >= 2.0:
            return 'C'
        elif self.gpa >= 1.0:
            return 'D'
        else:
            return 'F'

    def get_attendance_stats(self):
        records = self.attendance_records.all()
        total = records.count()
        if total == 0:
            return {
                'total': 0,
                'present': 0,
                'absent': 0,
                'late': 0,
                'excused': 0,
                'percentage': 0.0,
                'is_good': True
            }
        present = records.filter(status='Present').count()
        late = records.filter(status='Late').count()
        absent = records.filter(status='Absent').count()
        excused = records.filter(status='Excused').count()
        
        effective_present = present + (late * 0.5)
        percentage = round((effective_present / total) * 100, 1)
        
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'percentage': percentage,
            'is_good': percentage >= 75.0
        }

    def __str__(self):
        return f"{self.roll_number} - {self.get_full_name()}"


class UserProfile(TimeStampedModel):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    student = models.OneToOneField(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profile')
    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Attendance(TimeStampedModel):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_attendances')
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', 'student__roll_number']

    @property
    def marked_by_name(self):
        if self.marked_by:
            name = self.marked_by.get_full_name()
            return name if name else self.marked_by.username
        return "System"

    def __str__(self):
        return f"{self.student.roll_number} - {self.date} - {self.status}"
