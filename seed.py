import os
import shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_system.settings')
django.setup()

from students.models import Student
from django.core.files import File

# Ensure media directory exists
os.makedirs('media/profiles', exist_ok=True)

# Delete existing students to avoid duplicates for the demo
Student.objects.all().delete()

# Dummy data with local paths to the generated images
students_data = [
    {
        'roll_number': 'CS2026001',
        'first_name': 'Sarah',
        'last_name': 'Jenkins',
        'email': 'sarah.jenkins@example.edu',
        'department': 'Computer Science',
        'gpa': 3.8,
        'image_path': r'C:\Users\JATOTHU ANAND\.gemini\antigravity\brain\f05793da-3d37-44ad-999e-0c2317c5ad8e\profile_1_1785174863393.jpg',
        'image_name': 'sarah_jenkins.jpg'
    },
    {
        'roll_number': 'IT2026042',
        'first_name': 'Michael',
        'last_name': 'Chen',
        'email': 'm.chen@example.edu',
        'department': 'Information Technology',
        'gpa': 3.5,
        'image_path': r'C:\Users\JATOTHU ANAND\.gemini\antigravity\brain\f05793da-3d37-44ad-999e-0c2317c5ad8e\profile_2_1785174881609.jpg',
        'image_name': 'michael_chen.jpg'
    },
    {
        'roll_number': 'EE2026015',
        'first_name': 'Emily',
        'last_name': 'Davis',
        'email': 'emily.davis@example.edu',
        'department': 'Electrical Engineering',
        'gpa': 3.9,
        'image_path': r'C:\Users\JATOTHU ANAND\.gemini\antigravity\brain\f05793da-3d37-44ad-999e-0c2317c5ad8e\profile_3_1785174899801.jpg',
        'image_name': 'emily_davis.jpg'
    },
    {
        'roll_number': 'ME2026088',
        'first_name': 'James',
        'last_name': 'Wilson',
        'email': 'j.wilson@example.edu',
        'department': 'Mechanical Engineering',
        'gpa': 3.2,
        'image_path': None,
        'image_name': None
    },
    {
        'roll_number': 'CS2026105',
        'first_name': 'Aisha',
        'last_name': 'Patel',
        'email': 'aisha.p@example.edu',
        'department': 'Computer Science',
        'gpa': 4.0,
        'image_path': None,
        'image_name': None
    }
]

for data in students_data:
    student = Student(
        roll_number=data['roll_number'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        department=data['department'],
        gpa=data['gpa']
    )
    
    if data['image_path'] and os.path.exists(data['image_path']):
        # Copy image to media/profiles to simulate upload
        dest_path = os.path.join('media', 'profiles', data['image_name'])
        shutil.copy(data['image_path'], dest_path)
        with open(dest_path, 'rb') as f:
            student.profile_picture.save(data['image_name'], File(f), save=False)
            
    student.save()

print("Successfully seeded demo data!")
