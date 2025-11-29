# Learning Pathway LMS

A modern Learning Management System built with Django and PostgreSQL, featuring a beautiful modern UI, role-based access control, course management, assignments, quizzes, and comprehensive dashboards.

## ✨ Features

### 🎨 Modern UI
- Beautiful modern design inspired by contemporary LMS platforms
- Smooth animations and transitions
- Fully responsive layout
- Dark mode support (coming soon)
- Clean, intuitive interface

### 👨‍🏫 For Instructors
- Create and manage courses, modules, and lessons
- Create assignments with due dates and file attachments
- Build quizzes with multiple-choice questions
- Grade student submissions with feedback
- Award badges to students
- View student progress and analytics

### 👨‍🎓 For Students
- Browse and enroll in courses
- Access course content (modules and lessons)
- Submit assignments with text and file uploads
- Take quizzes with instant feedback
- View grades and feedback
- Earn badges for achievements
- Track progress across courses

### 🔧 Technical Features
- PostgreSQL database for production-ready performance
- Role-based access control
- File upload capabilities
- Secure authentication system
- RESTful URL structure

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd learning_pathway
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup PostgreSQL**
```bash
# Create database
psql -U postgres
CREATE DATABASE learning_pathway_db;
\q
```

4. **Configure environment**
```bash
# Copy example env file
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

8. **Start the server**
```bash
python manage.py runserver
```

Visit http://localhost:8000 to see your Learning Pathway LMS!

## 🔍 Testing Your Setup

After installation, run these diagnostic scripts:

```bash
# Test database connection and basic functionality
python test_setup.py

# Test registration form validation
python check_registration.py
```

## 🐛 Troubleshooting

If sign-up/login isn't working:

1. **Check database connection**:
   ```bash
   python test_setup.py
   ```

2. **Verify migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Check for errors**: Look at terminal output when submitting the form

4. **Read detailed guide**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

Common issues:
- PostgreSQL not running → Start PostgreSQL service
- Wrong password in settings.py → Update database credentials
- Migrations not run → Run `python manage.py migrate`

## 📁 Project Structure

```
learning_pathway/
├── lms/                      # Main application
│   ├── models.py             # Database models
│   ├── views.py              # Main views
│   ├── views_modules.py      # Module/lesson views
│   ├── views_assignments.py  # Assignment views
│   ├── views_quizzes.py      # Quiz views
│   ├── forms.py              # Form definitions
│   ├── urls.py               # URL routing
│   └── management/commands/  # Custom commands
├── templates/lms/            # HTML templates
├── static/                   # Static assets
│   ├── css/style.css         # Modern EduNexus styles
│   └── js/main.js            # JavaScript
├── media/                    # User uploads
├── learning_pathway/         # Project settings
│   └── settings.py           # Django configuration
├── requirements.txt          # Python dependencies
├── SETUP.md                  # Detailed setup guide
└── README.md                 # This file
```

## 🛠️ Technologies

- **Backend**: Django 5.2.8
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Modern UI with contemporary styling
- **Image Processing**: Pillow

## 📖 Documentation

For detailed setup instructions, see [SETUP.md](SETUP.md)

## 🎯 Key Improvements

- ✅ Migrated from SQLite to PostgreSQL
- ✅ Modern UI design with contemporary styling
- ✅ Improved form layouts with split-screen design
- ✅ Enhanced button styles with gradients
- ✅ Better responsive design
- ✅ Cleaner navigation
- ✅ Professional color scheme
- ✅ Smooth animations and transitions

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.