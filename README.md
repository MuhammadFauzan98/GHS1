# GHS1 - School Management & PYQP Portal

A comprehensive Flask-based web application for school management, faculty authentication, and Previous Year Question Paper (PYQP) repository management.

## 📋 Features

### Public Features
- **Home Page**: Overview of the institution
- **About Page**: Information about the school and faculty members
- **Contact Form**: Get in touch with the school administration
- **PYQP Repository**: Access to previous year question papers organized by subject and year

### Faculty Dashboard (Authenticated)
- **Secure Login**: Faculty authentication with encrypted passwords
- **Profile Management**: Update faculty information and credentials
- **PYQP Upload**: Upload question papers with metadata (subject, year, description)
- **Dashboard**: View and manage uploaded papers
- **Activity Logging**: Track user actions and login history

### Administrative Features
- **Faculty Management**: Manage faculty accounts and roles
- **Content Management**: Upload and organize faculty member profiles
- **User Activity Monitoring**: Track system usage and access logs
- **File Management**: Secure file storage with size limits

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: Flask-Login with password hashing
- **Security**: Werkzeug security utilities
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Vercel (serverless)

## 📦 Installation

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GHS1
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   ```

5. **Initialize the database**
   ```bash
   python create_directories.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```
   
   The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
GHS1/
├── app.py                          # Main Flask application
├── models.py                       # SQLAlchemy database models
├── create_directories.py           # Database initialization script
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment configuration
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── index.html                  # Home page
│   ├── about.html                  # About page
│   ├── faculty.html                # Faculty listing
│   ├── pyqp.html                   # PYQP repository page
│   ├── contact.html                # Contact form
│   ├── 404.html                    # 404 error page
│   ├── 500.html                    # 500 error page
│   └── auth/                       # Authentication templates
│       ├── faculty_login.html      # Faculty login page
│       ├── faculty_dashboard.html  # Faculty dashboard
│       ├── faculty_profile.html    # Faculty profile page
│       └── faculty_upload_pyqp.html# PYQP upload form
│
├── static/                         # Static files
│   ├── css/
│   │   └── styles.css              # Application styles
│   ├── js/
│   │   └── script.js               # Client-side scripts
│   └── uploads/                    # File upload directory
│       └── pyqp/                   # PYQP files storage
│
└── instance/                       # Instance-specific files
```

## 🗄️ Database Models

### Faculty
- User authentication for faculty members
- Stores username, email, password hash, role, and department
- Tracks login activity and administrative status

### FacultyMember
- Public faculty profile information
- Includes qualification, experience, and specialization
- Supports faculty member profile images

### PYQP (Previous Year Question Paper)
- Question paper metadata and storage
- Links papers to uploading faculty
- Tracks upload date and file information

### ContactMessage
- Stores messages from the contact form
- Includes contact information and status tracking
- Supports replies and read status

### ActivityLog
- Tracks user actions and system events
- Records IP addresses and user agents
- Maintains audit trail

## 🔐 Security Features

- **Password Hashing**: Uses Werkzeug security for encrypted password storage
- **Session Security**: Secure, HTTP-only cookies with SameSite protection
- **File Upload Limits**: 16MB maximum file size
- **Secure Filenames**: Prevents directory traversal attacks
- **Authentication Required**: Protected routes require faculty login
- **Environment-based Configuration**: Sensitive data stored in environment variables

## 🚀 Deployment

### Vercel Deployment

The application is configured for Vercel serverless deployment:

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Vercel**
   - Import project on Vercel dashboard
   - Set environment variables:
     - `SECRET_KEY`: Application secret key
     - `VERCEL`: Set to `true` for Vercel environment detection

3. **Deploy**
   - Vercel automatically deploys on push
   - Application uses `/tmp` for database and uploads on Vercel

## 📝 API Routes

### Public Routes
- `GET /` - Home page
- `GET /about` - About page
- `GET /faculty` - Faculty listing
- `GET /pyqp` - PYQP repository
- `GET /contact` - Contact form
- `POST /contact` - Submit contact message

### Faculty Authentication Routes
- `GET/POST /faculty_login` - Faculty login
- `GET /faculty_logout` - Faculty logout
- `GET /faculty_dashboard` - Faculty dashboard (protected)
- `GET /faculty_profile` - Faculty profile (protected)
- `GET/POST /upload_pyqp` - Upload question paper (protected)

## ⚙️ Configuration

Key configuration settings in `app.py`:

```python
# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///school.db'  # Local development

# File uploads
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

## 🐛 Troubleshooting

### Common Issues

**Database Errors**
- Run `python create_directories.py` to initialize the database
- Check that the `instance/` directory has write permissions

**File Upload Issues**
- Verify `static/uploads/` directory exists
- Check file size doesn't exceed 16MB limit
- Ensure proper permissions on uploads directory

**Login Issues**
- Clear browser cookies and try again
- Verify `SECRET_KEY` is set in environment variables
- Check database connection

## 📄 License

This project is proprietary and intended for school use.

## 📧 Support

For issues or questions, please contact the school administration through the contact form.

---

**Last Updated**: December 2025
