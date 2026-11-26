# SmartLesson

SmartLesson is a Django-based lesson-plan management application for the Kenyan CBC curriculum. It supports teacher plan creation, administrator/ICT review, in-app notifications, coverage reporting, and PDF/Excel exports.

## Overview

SmartLesson provides separate workflows for three roles:

- **Teachers** create and edit lesson plans and view their submission history.
- **Administrators** review submitted plans, return feedback, and approve or reject submissions.
- **ICT officers** can review plans and reports and manage registered users.

Plans include subject, grade level, term, week, strand, learning objectives, resources, lesson activities, assessment, reflection, and CBC-specific fields.

## Key features

- Role-based teacher, administrator, and ICT officer accounts.
- CBC lesson-plan creation for PP1 through JSS Grade 9.
- Teacher lesson lists with search and filters.
- Submitted, approved, and rejected review statuses.
- Administrative feedback and review tracking.
- In-app notifications for submission, resubmission, approval, and rejection.
- Coverage statistics and paginated reporting.
- PDF exports for individual lesson plans and coverage reports.
- Excel exports for coverage reports.
- Password changes and user profile management.
- ICT-officer user search and account management.
- Django administration for registered application models.

## User roles

- **Teacher:** Creates, edits, and submits lesson plans.
- **Administrator:** Reviews all lesson plans, provides feedback, and updates approval status.
- **ICT Officer:** Reviews lesson plans and coverage reports and manages registered users.

Role checks are implemented with a custom `role_required` decorator and direct profile-role checks.

## Technology stack

- Python
- Django 5.2.7
- SQLite
- Django Template Language
- `django-widget-tweaks`
- ReportLab
- OpenPyXL
- Pillow
- Tailwind CSS loaded from a CDN
- Alpine.js loaded from a CDN
- Django built-in authentication

## Project structure

```text
SmartLesson/
├── requirements.txt
├── notes.txt
└── SmartLesson/
    ├── manage.py
    ├── SmartLesson/          # Project settings and root URLs
    ├── core/                # Home page, dashboard, and support
    ├── accounts/            # Profiles, roles, authentication, users, notifications
    └── lessonplans/         # Lesson plans, review, reports, and exports
```

## Installation and setup

### Prerequisites

- Python 3
- `pip`

### 1. Clone the repository

```bash
git clone https://github.com/DannyDuke77/SmartLesson.git
cd SmartLesson
```

### 2. Create a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run migrations

```bash
cd SmartLesson
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

The Django admin interface is available at `/admin/` after starting the server.

### 6. Start the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Environment configuration

The project does not read environment variables. Settings are written directly in `SmartLesson/SmartLesson/settings.py`:

- Database: SQLite at `BASE_DIR / 'db.sqlite3'`
- Time zone: `Africa/Nairobi`
- Language: `en-us`
- Debug mode: enabled
- `ALLOWED_HOSTS`: empty

A Django development secret key is stored in the source. Replace it and keep it private outside local development.

No external API keys or required environment variables are referenced by the code.

## Usage

- Teachers register or log in, create lesson plans, and track their status.
- Administrators and ICT officers review, approve, or reject plans and provide feedback.
- Teachers receive notifications after review or when plans require revision.
- Administrators and ICT officers can filter coverage reports and export them as PDF or Excel.
- Individual lesson plans can be downloaded as PDF documents.

## Known limitations

- The project uses development settings and a checked-in development secret key.
- SQLite is used directly and no production database configuration is provided.
- Test modules contain no substantive test cases.
- Tailwind CSS and Alpine.js are loaded through CDNs.
- Some authorization logic should be reviewed before deployment.

## License

No licence file or licence metadata is present in the repository, so no licence is asserted.
