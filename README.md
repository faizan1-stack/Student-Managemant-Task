# ESS (Expert Student System)

A Django-based Educational Management System with automated enrollment handling and teacher notifications.

## Features

- **Teacher Registration & Authentication** with OTP verification
- **Student Enrollment Management** with automated processing
- **Course Management** with teacher approval system
- **Automated Email Notifications** for students and teachers
- **Celery-based Background Tasks** for enrollment expiration and reminders
- **JWT Authentication** with access and refresh tokens

## Project Structure

```
expert/
├── expert/               # Main project directory
│   ├── settings.py      # Django settings
│   ├── celery.py        # Celery configuration
│   └── urls.py          # Main URL configuration
├── ess/                 # Core application
│   ├── models.py        # User, Student, Course models
│   ├── serializers.py   # API serializers
│   └── tasks.py         # ESS-specific Celery tasks
├── Teacher/             # Teacher application
│   ├── views.py         # Teacher API views
│   ├── tasks.py         # Teacher-specific Celery tasks
│   └── management/      # Management commands
├── Course/              # Course management
├── Enroll/              # Enrollment handling

```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ess
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install django djangorestframework redis celery django-celery-beat django-celery-results djangorestframework-simplejwt
   ```



4. **Database setup:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Setup Celery tasks:**
   ```bash
   python manage.py setup_celery_tasks
   ```

## Running the Application

1. **Start Django development server:**
   ```bash
   python manage.py runserver
   ```



3. **Start Celery worker:**
   ```bash
   celery -A expert worker -l info --pool=solo
   ```

4. **Start Celery Beat scheduler:**
   ```bash
   celery -A expert beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

## API Endpoints

### Teacher Authentication
- `POST /teacher/register/` - Teacher registration with OTP
- `POST /teacher/verify-otp/` - OTP verification
- `POST /teacher/login/` - Teacher login

### Teacher Management
- `GET /teacher/` - List all teachers
- `GET /teacher/{id}/` - Get specific teacher
- `PUT /teacher/{id}/` - Update teacher
- `DELETE /teacher/{id}/` - Delete teacher

### Manual Tasks
- `GET /teacher/manual-discard/` - Manually trigger enrollment discard

## Automated Features

### Background Tasks (Celery)

1. **Enrollment Expiration (Every 1 minute):**
   - Auto-discards pending enrollments older than 1 minute
   - Sends notification emails to affected students
   - Deletes courses with no remaining enrollments

2. **Teacher Reminders (Every 5 minutes):**
   - Sends reminder emails to teachers about pending approvals
   - Counts pending enrollment requests per teacher

### Email Notifications

- **OTP Verification:** Sent during teacher registration
- **Enrollment Discarded:** Notifies students when requests expire
- **Pending Approvals:** Reminds teachers to review enrollments

## Environment Variables

Create a `.env` file with:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Configuration

### Celery Settings
- **Broker:** Redis (redis://127.0.0.1:6379/0)
- **Result Backend:** Django Database
- **Timezone:** Asia/Karachi
- **Serializer:** JSON

### Django Settings
- **Database:** SQLite (development)
- **Authentication:** JWT with 30-minute access tokens
- **Email Backend:** Gmail SMTP

## Development

### Adding New Tasks

1. Create task in appropriate `tasks.py`:
   ```python
   @shared_task(bind=True, name='app.task_name')
   def my_task(self):
       # Task logic here
       pass
   ```

2. Register periodic task:
   ```bash
   python manage.py shell
   from django_celery_beat.models import PeriodicTask, IntervalSchedule
   # Create schedule and task
   ```

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### Celery Issues
- Ensure Redis is running
- Use `--pool=solo` on Windows
- Check task registration in worker logs

### Email Issues
- Verify Gmail App Password
- Check EMAIL_HOST_USER in settings
- Test email configuration

### Database Issues
- Run migrations for django_celery_beat
- Check INSTALLED_APPS includes all required apps

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

This project is licensed under the MIT License.
