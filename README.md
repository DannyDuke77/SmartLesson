# SmartLesson

SmartLesson is a Django-based lesson-plan management application for the Kenyan Competency-Based Curriculum (CBC). It provides a structured workflow for teachers to create and submit lesson plans, administrators to review submissions, and ICT officers to oversee reporting and user management.

## Overview

SmartLesson supports three user roles:

- **Teachers** create and edit lesson plans, submit them for review, and track their submission history.
- **Administrators** review submitted plans, provide feedback, and approve or reject submissions.
- **ICT Officers** review lesson plans and reports and manage registered users.

Lesson plans capture subject, grade level, term, week, strand, learning objectives, resources, lesson activities, assessment, reflection, and other CBC-related details.

## Key Features

- Role-based teacher, administrator, and ICT officer accounts.
- CBC lesson-plan creation from PP1 through JSS Grade 9.
- Lesson-plan search and filtering.
- Submission and review tracking with submitted, approved, and rejected statuses.
- Administrative feedback and review history.
- In-app notifications for submissions, resubmissions, approvals, and rejections.
- Coverage statistics and paginated reports.
- PDF exports for individual lesson plans and coverage reports.
- Excel exports for coverage reports.
- User profile and password management.
- ICT officer user search and account management.
- Django administration for application models.

## User Roles

| Role | Responsibilities |
|---|---|
| Teacher | Creates, edits, and submits lesson plans. Tracks submission status and receives review feedback. |
| Administrator | Reviews lesson plans, provides feedback, and updates approval status. |
| ICT Officer | Reviews lesson plans and coverage reports and manages registered users. |

## Technology Stack

- **Backend:** Python, Django 5.2.7
- **Database:** SQLite
- **Frontend:** Django Template Language, Tailwind CSS, Alpine.js
- **Utilities:** django-widget-tweaks
- **Document generation:** ReportLab, OpenPyXL
- **Image processing:** Pillow
- **Authentication:** Django built-in authentication

Tailwind CSS and Alpine.js are loaded through their respective CDNs.

## Project Structure

```text
SmartLesson/
├── requirements.txt
├── notes.txt
└── SmartLesson/
    ├── manage.py
    ├── SmartLesson/          # Project settings and root URLs
    ├── core/                 # Home page, dashboard, and support
    ├── accounts/             # Profiles, roles, authentication, users, notifications
    └── lessonplans/          # Lesson plans, review, reports, and exports
```

## Installation and Setup

### Prerequisites

- Python 3
- pip

### 1. Clone the repository

```bash
git clone https://github.com/DannyDuke77/SmartLesson.git
cd SmartLesson
```

### 2. Create and activate a virtual environment

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows Command Prompt**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
cd SmartLesson
python manage.py migrate
```

### 5. Create an administrator account

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

The Django administration interface is available at `http://127.0.0.1:8000/admin/`.

## Configuration

The application uses the following default configuration:

- **Database:** SQLite
- **Time zone:** Africa/Nairobi
- **Language:** en-us
- **Debug mode:** Enabled

Project settings are maintained in `SmartLesson/SmartLesson/settings.py`.

For deployment, configure a secure secret key, appropriate allowed hosts, and production-ready settings.

## Usage

1. Teachers register or log in and create lesson plans.
2. Submitted plans become available for administrative review.
3. Administrators and ICT officers review plans and provide feedback.
4. Teachers receive notifications when plans are approved, rejected, or require revision.
5. Administrators and ICT officers can view coverage reports and export them as PDF or Excel documents.
6. Individual lesson plans can be downloaded as PDF documents.

## Development Notes

SmartLesson is configured for local development using SQLite and Django's development settings. A production deployment would require environment-based configuration and an appropriate production database.

## License

No licence file or licence metadata is currently included in the repository.
