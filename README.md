# Student Management System

A robust Django-based Student Management System built as part of Kinetrexa Internship Task 1. This system uses object-oriented programming concepts, class-based views, file handling (CSV import/export), and PDF generation.

## Features

- **Object-Oriented Models:** Utilizes inheritance (TimeStampedModel) and custom model managers.
- **Full CRUD functionality:** Managed efficiently with Django Class-Based Views (CBV).
- **Search & Filtering:** Dynamic search using Django `Q` objects to find students quickly.
- **File Handling:**
  - Bulk Import students from CSV/Excel files.
  - Export the current student directory to CSV.
  - Download dynamically generated Student PDF ID Cards (using ReportLab).
- **Beautiful GUI:** Designed with modern aesthetics using Tailwind CSS.
- **Exception Handling:** Robust try-except blocks wrapping all file/database operations with user-friendly alerts using Django's message framework.

## Project Architecture

```
student_system/
├── core/                   # Project settings & URL routing
├── students/               # Main application
│   ├── models.py           # Database schemas & OOP methods
│   ├── views.py            # Class-Based Views (CBVs)
│   ├── forms.py            # Data validation forms
│   ├── services.py         # Business logic & File Handling (CSV/PDF)
│   └── templates/          # Tailwind CSS HTML templates
```

## Setup & Installation

### Prerequisites

- Python 3.8+
- pip

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ANAND-JATOTHU/kinetrexa-task-1.git
   cd kinetrexa-task-1
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\Activate.ps1
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install django pillow pandas openpyxl reportlab
   ```

4. **Run migrations to set up the database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000/`.

### Admin Credentials

The system is secured so that only authenticated users can manage student records. You can log in using the following default admin credentials:

- **Username:** `admin`
- **Password:** `admin`

## Author
Built by Anand Jatothu.
