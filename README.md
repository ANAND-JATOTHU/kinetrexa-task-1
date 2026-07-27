# Student Management System

> A comprehensive Django-based Student Management System for educational institutions. Features include a modern dashboard, secure authentication, CRUD operations, bulk CSV imports, Excel exports, and PDF ID card generation, built with Tailwind CSS.

## 📸 Project Showcase

### 1. Dashboard Overview
The system features a clean, responsive dashboard built with Tailwind CSS that provides administrators with a quick glance at key metrics. It displays the total number of students, average GPA across the institution, and active vs. inactive student counts, along with a breakdown of students by department.

![Dashboard Overview](screenshots/dashboard.png)

### 2. Student Directory
The main directory allows administrators to view, search, and manage all student records. It includes dynamic search functionality to filter by Roll No, Name, or Department. Each student has a profile picture and quick action buttons for viewing, editing, or deleting their record.

![Student Directory](screenshots/directory.png)

### 3. Bulk CSV Import
To make data entry efficient, the system includes a bulk import feature. Administrators can upload a `.csv` or Excel file containing student data, and the system will automatically parse and create the records in the database.

![Import CSV](screenshots/import.png)

### 4. Excel Export
The system provides a seamless export feature. Administrators can export the currently filtered list of students directly to a `.csv` file, which opens perfectly formatted in Excel for reporting and external data analysis.

![Excel Export](screenshots/export.png)

---

## 🚀 Features

- **Authentication System:** Secure login/logout functionality for administrators.
- **Analytics Dashboard:** High-level metrics and department breakdowns.
- **Full CRUD Operations:** Create, Read, Update, and Delete student records.
- **Dynamic Search:** Filter students by name, roll number, or department.
- **Bulk CSV Import:** Quickly add hundreds of students via `.csv` upload.
- **CSV/Excel Export:** Download student data for external use.
- **PDF ID Cards:** Automatically generate and download printable PDF ID cards for students.
- **Modern UI:** Built with Tailwind CSS and FontAwesome for a premium user experience.

## 🛠️ Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, Tailwind CSS, FontAwesome
- **Database:** SQLite (default Django DB)
- **File Handling:** Pandas, OpenPyXL (for Excel/CSV)
- **PDF Generation:** ReportLab
- **Images:** Pillow

## ⚙️ Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ANAND-JATOTHU/kinetrexa-task-1.git
   cd kinetrexa-task-1
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000/`.

### 🔐 Admin Credentials

The system is secured so that only authenticated users can manage student records. You can log in using the following default admin credentials:

- **Username:** `admin`
- **Password:** `admin`

> [!TIP]
> **Testing CSV Import:** You can create a simple Excel or CSV file with the headers `roll_number, first_name, last_name, email, department, gpa` and import it directly into the system using the "Import CSV" button on the dashboard!

## 👨‍💻 Author
Built by Anand Jatothu for Kinetrexa Task 1.
