from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from students.models import Student, UserProfile, Attendance
from django.utils import timezone

class MultiRoleAndAttendanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Admin
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpassword', email='admin@test.com')
        UserProfile.objects.create(user=self.admin_user, role='admin')
        
        # Create Teacher
        self.teacher_user = User.objects.create_user(username='teacher', password='teacherpassword', email='teacher@test.com')
        UserProfile.objects.create(user=self.teacher_user, role='teacher', department='Computer Science')

        # Create Student model
        self.student_obj = Student.objects.create(
            roll_number='CS2026001',
            first_name='Sarah',
            last_name='Jenkins',
            email='sarah@test.com',
            department='Computer Science',
            gpa=3.85
        )

        # Create Student User
        self.student_user = User.objects.create_user(username='student', password='studentpassword', email='sarah@test.com')
        UserProfile.objects.create(user=self.student_user, role='student', student=self.student_obj)

    def test_student_auto_redirect_to_portal(self):
        self.client.login(username='student', password='studentpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('student-portal'), response.url)

    def test_student_portal_loads(self):
        self.client.login(username='student', password='studentpassword')
        response = self.client.get(reverse('student-portal'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sarah Jenkins')
        self.assertContains(response, 'CS2026001')

    def test_teacher_dashboard_loads(self):
        self.client.login(username='teacher', password='teacherpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Faculty Portal')

    def test_teacher_marks_attendance(self):
        self.client.login(username='teacher', password='teacherpassword')
        mark_url = reverse('mark-attendance')
        today_str = timezone.localdate().strftime('%Y-%m-%d')
        
        post_data = {
            'date': today_str,
            'department': 'Computer Science',
            'student_ids': [self.student_obj.pk],
            f'status_{self.student_obj.pk}': 'Present',
            f'remarks_{self.student_obj.pk}': 'Great participation'
        }
        
        response = self.client.post(mark_url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify attendance record in DB
        record = Attendance.objects.filter(student=self.student_obj, date=timezone.localdate()).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.status, 'Present')
        self.assertEqual(record.remarks, 'Great participation')

    def test_student_cannot_mark_attendance(self):
        self.client.login(username='student', password='studentpassword')
        response = self.client.get(reverse('mark-attendance'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('student-portal'), response.url)

    def test_attendance_records_list(self):
        self.client.login(username='admin', password='adminpassword')
        # Create an attendance record
        Attendance.objects.create(student=self.student_obj, date=timezone.localdate(), status='Present')
        response = self.client.get(reverse('attendance-records'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CS2026001')

    def test_pdf_id_card_download(self):
        self.client.login(username='student', password='studentpassword')
        response = self.client.get(reverse('student-pdf', kwargs={'pk': self.student_obj.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
