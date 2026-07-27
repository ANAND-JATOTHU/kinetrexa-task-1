import csv
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .models import Student

def handle_csv_upload(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            return False, "Unsupported file format."

        required_columns = ['roll_number', 'first_name', 'last_name', 'email', 'department', 'gpa']
        if not all(col in df.columns for col in required_columns):
            return False, f"Missing required columns. Expected: {', '.join(required_columns)}"

        students_to_create = []
        for index, row in df.iterrows():
            if not Student.objects.filter(roll_number=row['roll_number']).exists() and \
               not Student.objects.filter(email=row['email']).exists():
                students_to_create.append(
                    Student(
                        roll_number=row['roll_number'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        department=row['department'],
                        gpa=row['gpa']
                    )
                )

        Student.objects.bulk_create(students_to_create)
        return True, f"Successfully imported {len(students_to_create)} students."
    except Exception as e:
        return False, f"An error occurred during import: {str(e)}"

def export_students_csv(queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Roll Number', 'First Name', 'Last Name', 'Email', 'Department', 'GPA', 'Grade', 'Active'])

    for student in queryset:
        writer.writerow([
            student.roll_number,
            student.first_name,
            student.last_name,
            student.email,
            student.department,
            student.gpa,
            student.get_grade(),
            'Yes' if student.is_active else 'No'
        ])

    return response

def generate_student_pdf(student):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=20
    )
    elements.append(Paragraph("Student Profile Card", title_style))
    
    # Student Data Table
    data = [
        ['Roll Number:', student.roll_number],
        ['Name:', student.get_full_name()],
        ['Email:', student.email],
        ['Department:', student.department],
        ['GPA:', str(student.gpa)],
        ['Grade:', student.get_grade()],
        ['Status:', 'Active' if student.is_active else 'Inactive']
    ]
    
    if student.profile_picture:
        try:
            img = Image(student.profile_picture.path, width=100, height=100)
            data.insert(0, ['Profile Picture:', img])
        except Exception:
            pass
            
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB'))
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
