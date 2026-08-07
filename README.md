# Academia - Role-Based Student & Attendance Management System

> **Short Description (Max 250 characters for LinkedIn / GitHub):**
> *A full-featured Django & Tailwind CSS Student Management System featuring Role-Based Access Control (Admin, Teacher, Student), interactive daily attendance allocation, self-service student portals, analytics, and instant PDF ID card generation.*

---

## 📸 Visual Showcase & System Tour

### 1. Multi-Role Authentication & Quick Access
The login portal features role-based access control with one-click demo pre-fill buttons for instant access to **Admin**, **Teacher**, and **Student** workspaces.

![Multi-Role Authentication](screenshots/login_portal.png)

---

### 2. Administrator Workspace & Institutional Analytics
The Administrator dashboard provides high-level institution metrics, total enrollment, average GPA, overall attendance compliance rate, department distribution breakdown, and full student CRUD management.

![Administrator Workspace](screenshots/admin_dashboard.png)

---

### 3. Faculty / Teacher Portal
Teachers have access to a specialized faculty dashboard tailored to their assigned department, displaying class attendance averages, daily roster shortcuts, and live submission logs.

![Faculty Portal](screenshots/teacher_dashboard.png)

---

### 4. Student Academic Self-Service Portal
Students log into their dedicated academic portal to track cumulative GPA, academic standing grade, live attendance compliance gauge ($\ge 75\%$ requirement), chronological session activity history, and download verified PDF ID cards.

![Student Self-Service Portal](screenshots/student_portal.png)

---

### 5. Interactive Student Directory & Attendance Tracking
Search and filter students by Roll Number, Name, or Department with instant profile previews, GPA/Grade breakdown, and live attendance percentages.

![Student Directory](screenshots/teacher_directory.png)

---

### 6. Bulk CSV Data Import & Export Pipeline
Administrators can batch-enroll students by uploading `.csv` or Excel sheets, or export filtered rosters and attendance records for external reporting.

| Bulk CSV Import | Filtered Data Export |
| :---: | :---: |
| ![Import CSV](screenshots/import.png) | ![Excel Export](screenshots/export.png) |

---

## 🌟 Highlights & Key Capabilities

- 🔐 **Role-Based Access Control (RBAC):** Dedicated sessions and tailored navigation for **Admin**, **Teacher (Faculty)**, and **Student** accounts with automated permission routing.
- 📅 **Faculty Attendance Allocation:** Interactive daily class roster marking (Bulk *Present*, *Absent*, *Late*, *Excused*), date picker, and custom session remarks.
- 🎓 **Student Self-Service Portal:** Personalized portal displaying cumulative GPA, academic standing, live attendance compliance gauge ($\ge 75\%$), and chronological session logs.
- 📊 **Real-Time Analytics & Audit Trail:** Interactive institution metrics, department distribution breakdowns, attendance audit logs, and status filtering.
- 🪪 **Vector PDF ID Card Generation:** Direct one-click download of styled, printable student identification badges with attendance stats.
- 📁 **Data Pipeline (CSV Import / Export):** Bulk upload students via CSV, export filtered student records and complete attendance sheets.
- 🎨 **Modern Responsive UI:** Built with Tailwind CSS, FontAwesome icons, glassmorphic badges, and mobile-ready layouts.

---

## 👥 Role Sessions & Permissions

| Role | Access Level | Key Capabilities |
| :--- | :--- | :--- |
| 🛡️ **Administrator** | Full System Access | Analytics overview, complete student CRUD, multi-role management, bulk CSV import/export, attendance audit log. |
| 👨‍🏫 **Teacher / Faculty** | Academic & Roster Access | Department-filtered dashboard, bulk class attendance marker, student directory lookup, attendance export. |
| 🎓 **Student** | Self-Service Portal | Personal profile overview, cumulative GPA & letter grade, live attendance meter ($\ge 75\%$ threshold), session activity history, PDF ID card download. |

---

## 🔑 Demo Login Credentials

For testing and demonstration, use any of the pre-configured role accounts:

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin` | Full management dashboard & controls |
| **Teacher** | `teacher` | `teacher123` | Faculty attendance marking & department view |
| **Student** | `student` | `student123` | Personal student portal (Sarah Jenkins `CS2026001`) |

*(The login screen also includes 1-click credential prefill buttons for instant demo access!)*

---

## 🛠️ Technology Stack

- **Backend:** Python 3.10+, Django 5.x
- **Frontend:** HTML5, Tailwind CSS, FontAwesome 6
- **Database:** SQLite (Relational ORM with foreign key cascades)
- **Data Export / Import:** Pandas, OpenPyXL, Python CSV
- **Document Engine:** ReportLab (Vector PDF Generation)
- **Image Processing:** Pillow

---

## ⚙️ Quickstart & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/ANAND-JATOTHU/kinetrexa-task-1.git
cd kinetrexa-task-1
```

### 2. Activate Virtual Environment
```bash
# Windows:
.\venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Seed Multi-Role Demo Data
Populates the database with default Admin, Teacher, Student accounts, demo profiles, and 14 days of realistic attendance history:
```bash
python seed.py
```

### 6. Start Development Server
```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/` and sign in using `admin`/`admin`, `teacher`/`teacher123`, or `student`/`student123`.

---

## 🧪 Running Automated Tests

Run the full automated test suite verifying RBAC routing, attendance marking, student portals, and PDF generation:
```bash
python manage.py test
```

---

## 👨‍💻 Author
Built with ❤️ by **Anand Jatothu** for Kinetrexa Internship Task 1.
