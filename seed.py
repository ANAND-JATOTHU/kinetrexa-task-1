import os
import shutil
import datetime
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_system.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import Student, UserProfile, Attendance
from django.core.files import File

# Ensure media directory exists
os.makedirs('media/profiles', exist_ok=True)

# 1. Setup Users & Roles
print("Setting up users and role profiles...")

# Admin
admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@academia.edu', 'first_name': 'System', 'last_name': 'Admin', 'is_staff': True, 'is_superuser': True})
admin_user.set_password('admin')
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.save()
UserProfile.objects.update_or_create(user=admin_user, defaults={'role': 'admin', 'designation': 'Chief Administrator'})

# Teacher (Computer Science)
teacher_user, _ = User.objects.get_or_create(username='teacher', defaults={'email': 'alan.turing@academia.edu', 'first_name': 'Alan', 'last_name': 'Turing'})
teacher_user.set_password('teacher123')
teacher_user.save()
UserProfile.objects.update_or_create(user=teacher_user, defaults={'role': 'teacher', 'department': 'Computer Science', 'designation': 'Associate Professor'})

# Student User (Sarah Jenkins)
student_user, _ = User.objects.get_or_create(username='student', defaults={'email': 'sarah.jenkins@example.edu', 'first_name': 'Sarah', 'last_name': 'Jenkins'})
student_user.set_password('student123')
student_user.save()

# 2. Seed Students
print("Seeding student profiles...")
students_data = [
    {
        'roll_number': 'CS2026001',
        'first_name': 'Sarah',
        'last_name': 'Jenkins',
        'email': 'sarah.jenkins@example.edu',
        'department': 'Computer Science',
        'gpa': 3.85,
        'image_path': r'C:\Users\JATOTHU ANAND\.gemini\antigravity\brain\f05793da-3d37-44ad-999e-0c2317c5ad8e\profile_1_1785174863393.jpg',
        'image_name': 'sarah_jenkins.jpg'
    },
    {
        'roll_number': 'IT2026042',
        'first_name': 'Michael',
        'last_name': 'Chen',
        'email': 'm.chen@example.edu',
        'department': 'Information Technology',
        'gpa': 3.50,
        'image_path': r'C:\Users\JATOTHU ANAND\.gemini\antigravity\brain\f05793da-3d37-44ad-999e-0c2317c5ad8e\profile_2_1785174881609.jpg',
        'image_name': 'michael_chen.jpg'
    },
    {
        'roll_number': 'EE2026015',
        'first_name': 'Emily',
        'last_name': 'Davis',
        'email': 'emily.davis@example.edu',
        'department': 'Electrical Engineering',
        'gpa': 3.92,
        'image_path': r'C:\Users\JATOTHU ANAND\.gemini\antigravity\brain\f05793da-3d37-44ad-999e-0c2317c5ad8e\profile_3_1785174899801.jpg',
        'image_name': 'emily_davis.jpg'
    },
    {
        'roll_number': 'ME2026088',
        'first_name': 'James',
        'last_name': 'Wilson',
        'email': 'j.wilson@example.edu',
        'department': 'Mechanical Engineering',
        'gpa': 3.20,
        'image_path': None,
        'image_name': None
    },
    {
        'roll_number': 'CS2026105',
        'first_name': 'Aisha',
        'last_name': 'Patel',
        'email': 'aisha.p@example.edu',
        'department': 'Computer Science',
        'gpa': 4.00,
        'image_path': None,
        'image_name': None
    }
]

created_students = []
for data in students_data:
    student, created = Student.objects.update_or_create(
        roll_number=data['roll_number'],
        defaults={
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'department': data['department'],
            'gpa': data['gpa'],
            'is_active': True
        }
    )
    
    if data['image_path'] and os.path.exists(data['image_path']):
        dest_path = os.path.join('media', 'profiles', data['image_name'])
        shutil.copy(data['image_path'], dest_path)
        with open(dest_path, 'rb') as f:
            student.profile_picture.save(data['image_name'], File(f), save=True)
            
    created_students.append(student)

# Link Sarah Jenkins to the Student user profile
sarah_student = Student.objects.get(roll_number='CS2026001')
UserProfile.objects.update_or_create(
    user=student_user,
    defaults={
        'role': 'student',
        'student': sarah_student,
        'department': 'Computer Science'
    }
)

# 3. Seed Realistic Historical Attendance (Past 14 Days)
print("Seeding attendance records for past 14 days...")
Attendance.objects.all().delete()

today = timezone.localdate()
status_patterns = {
    'CS2026001': ['Present', 'Present', 'Present', 'Late', 'Present', 'Present', 'Present', 'Present', 'Excused', 'Present', 'Present', 'Present', 'Present', 'Present'],
    'IT2026042': ['Present', 'Late', 'Present', 'Absent', 'Present', 'Present', 'Late', 'Present', 'Present', 'Absent', 'Present', 'Present', 'Present', 'Present'],
    'EE2026015': ['Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present'],
    'ME2026088': ['Absent', 'Present', 'Late', 'Present', 'Absent', 'Present', 'Present', 'Late', 'Present', 'Absent', 'Present', 'Late', 'Present', 'Present'],
    'CS2026105': ['Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present', 'Present'],
}

remarks_map = {
    'Late': 'Arrived 10 mins late - lab transit',
    'Absent': 'Unexcused absence',
    'Excused': 'Medical certificate approved',
    'Present': 'On time participation'
}

attendance_entries = []
for day_offset in range(13, -1, -1):
    att_date = today - datetime.timedelta(days=day_offset)
    # Skip weekends (Saturday=5, Sunday=6)
    if att_date.weekday() in [5, 6]:
        continue

    for student in created_students:
        pattern = status_patterns.get(student.roll_number, ['Present'] * 14)
        status = pattern[day_offset % len(pattern)]
        remarks = remarks_map.get(status, '')

        attendance_entries.append(
            Attendance(
                student=student,
                date=att_date,
                status=status,
                marked_by=teacher_user if student.department == 'Computer Science' else admin_user,
                remarks=remarks
            )
        )

Attendance.objects.bulk_create(attendance_entries)
print(f"Successfully seeded {len(attendance_entries)} attendance records across 5 demo students!")
print("Ready for presentation and multi-role testing!")
