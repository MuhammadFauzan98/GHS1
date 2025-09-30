from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, Faculty, FacultyMember, PYQP, ContactMessage, ActivityLog
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'faculty_login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Faculty.query.get(int(user_id))

# Allowed extensions
ALLOWED_PDF_EXTENSIONS = {'pdf'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def log_activity(faculty_id, action, details=None, ip_address=None, user_agent=None):
    activity = ActivityLog(
        faculty_id=faculty_id,
        action=action,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.session.add(activity)
    db.session.commit()

# =====================
# PUBLIC ROUTES
# =====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.role.lower() in ['administrator', 'admin']:
            return redirect(url_for('faculty_dashboard'))  # or admin_dashboard if you have it
        elif current_user.role.lower() == 'faculty':
            return redirect(url_for('faculty_dashboard'))
        # You can add student roles or others here
    # Show neutral landing page for unauthenticated users
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faculty')
def faculty():
    faculty_members = FacultyMember.query.all()
    return render_template('faculty.html', faculty_members=faculty_members)

@app.route('/pyqp')
def pyqp():
    papers = PYQP.query.filter_by(is_active=True).order_by(PYQP.year.desc(), PYQP.subject).all()
    subjects = {}
    for paper in papers:
        if paper.subject not in subjects:
            subjects[paper.subject] = []
        subjects[paper.subject].append(paper)
    return render_template('pyqp.html', subjects=subjects)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        phone = request.form.get('phone', '')
        
        new_message = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        db.session.add(new_message)
        db.session.commit()
        
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# =====================
# AUTHENTICATION ROUTES
# =====================

@app.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    if current_user.is_authenticated:
        return redirect(url_for('faculty_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = True if request.form.get('remember') else False

        faculty = Faculty.query.filter_by(username=username).first()
        if faculty and faculty.check_password(password) and faculty.is_active:
            login_user(faculty, remember=remember)
            faculty.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome back, {faculty.name}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('faculty_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('auth/faculty_login.html')

@app.route('/faculty/logout')
@login_required
def faculty_logout():
    log_activity(
        current_user.id,
        'logout',
        f'Faculty {current_user.name} logged out',
        request.remote_addr,
        request.headers.get('User-Agent')
    )
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# =====================
# PROTECTED ROUTES
# =====================

@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    pyqp_count = PYQP.query.filter_by(uploaded_by=current_user.id).count()
    recent_pyqps = PYQP.query.filter_by(uploaded_by=current_user.id).order_by(PYQP.uploaded_at.desc()).limit(5).all()
    recent_activities = ActivityLog.query.filter_by(faculty_id=current_user.id).order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    return render_template('auth/faculty_dashboard.html',
                         pyqp_count=pyqp_count,
                         recent_pyqps=recent_pyqps,
                         recent_activities=recent_activities)

@app.route('/faculty/upload_pyqp', methods=['GET', 'POST'])
@login_required
def faculty_upload_pyqp():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['pdf']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            unique_filename = f"{timestamp}_{filename}"
            
            pyqp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'pyqp')
            os.makedirs(pyqp_dir, exist_ok=True)
            
            file_path = os.path.join('pyqp', unique_filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
            file.save(full_path)
            
            file_size = os.path.getsize(full_path)
            subject = request.form['subject']
            if subject == 'Other' and request.form.get('custom_subject'):
                subject = request.form['custom_subject']
            
            new_pyqp = PYQP(
                subject=subject,
                year=int(request.form['year']),
                filename=filename,
                file_path=file_path,
                description=request.form.get('description', ''),
                uploaded_by=current_user.id,
                file_size=file_size
            )
            db.session.add(new_pyqp)
            db.session.commit()
            
            log_activity(
                current_user.id,
                'upload_pyqp',
                f'Uploaded PYQP: {subject} {request.form["year"]}',
                request.remote_addr,
                request.headers.get('User-Agent')
            )
            
            flash('PYQP uploaded successfully!', 'success')
            return redirect(url_for('faculty_upload_pyqp'))
        else:
            flash('Invalid file type. Please upload PDF files only.', 'error')
    
    total_pyqp = PYQP.query.count()
    recent_pyqps = PYQP.query.filter_by(uploaded_by=current_user.id).order_by(PYQP.uploaded_at.desc()).limit(10).all()
    
    return render_template('auth/faculty_upload_pyqp.html',
                         total_pyqp=total_pyqp,
                         recent_pyqps=recent_pyqps,
                         current_year=datetime.now().year)

@app.route('/faculty/profile', methods=['GET', 'POST'])
@login_required
def faculty_profile():
    activities = ActivityLog.query.filter_by(faculty_id=current_user.id).order_by(ActivityLog.created_at.desc()).limit(20).all()
    
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
        current_user.department = request.form['department']
        
        if request.form['new_password']:
            if current_user.check_password(request.form['current_password']):
                current_user.set_password(request.form['new_password'])
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('faculty_profile'))
        
        db.session.commit()
        
        log_activity(
            current_user.id,
            'update_profile',
            'Updated faculty profile information',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('faculty_profile'))
    
    return render_template('auth/faculty_profile.html', activities=activities)

# =====================
# FILE SERVING ROUTES
# =====================

@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid file path", 400
            
        uploads_dir = app.config['UPLOAD_FOLDER']
        full_path = os.path.join(uploads_dir, filename)
        if not os.path.exists(full_path):
            return redirect('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80')
        if not os.path.isfile(full_path):
            return "Not a file", 400
        return send_from_directory(uploads_dir, filename)
    except Exception as e:
        return redirect('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80')

@app.route('/download_pyqp/<int:paper_id>')
def download_pyqp(paper_id):
    paper = PYQP.query.get_or_404(paper_id)
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], paper.file_path)
    if not os.path.exists(full_path):
        flash('Requested file not found.', 'error')
        return redirect(url_for('pyqp'))
    
    file_dir = os.path.join(app.config['UPLOAD_FOLDER'], os.path.dirname(paper.file_path))
    filename = os.path.basename(paper.file_path)
    
    return send_from_directory(
        file_dir,
        filename,
        as_attachment=True,
        download_name=f"{paper.subject}_{paper.year}.pdf"
    )

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'pyqp'), exist_ok=True)

        # Sample faculty accounts
        if Faculty.query.count() == 0:
            faculty_accounts = [
                {'username': 'admin', 'email': 'admin@globalhighschool.edu.in', 'password': 'admin123', 'name': 'Administrator', 'role': 'System Administrator', 'department': 'Administration', 'is_admin': True},
                {'username': 'principal', 'email': 'principal@globalhighschool.edu.in', 'password': 'principal123', 'name': 'Dr. Rajesh Kumar', 'role': 'Principal', 'department': 'Administration'},
                {'username': 'maths', 'email': 'maths@globalhighschool.edu.in', 'password': 'maths123', 'name': 'Mrs. Sunita Reddy', 'role': 'Mathematics HOD', 'department': 'Mathematics'}
            ]
            for account in faculty_accounts:
                faculty = Faculty(
                    username=account['username'],
                    email=account['email'],
                    name=account['name'],
                    role=account['role'],
                    department=account.get('department', ''),
                    is_admin=account.get('is_admin', False)
                )
                faculty.set_password(account['password'])
                db.session.add(faculty)
            db.session.commit()

        # Sample faculty members
        if FacultyMember.query.count() == 0:
            sample_faculty = [
                FacultyMember(
                    name="Mr. Sami Ullah Khan",
                    role="Principal",
                    qualification="Ph.D. in Education, M.Ed., B.Sc.",
                    description="Leading our institution with vision and dedication towards academic excellence.",
                    image_path="https://scontent.fhyd11-2.fna.fbcdn.net/v/t39.30808-6/519085037_752778251032594_214901603916856522_n.jpg?_nc_cat=104&ccb=1-7&_nc_sid=127cfc&_nc_ohc=XF7uQZu9Ql0Q7kNvwFpYN3b&_nc_oc=AdlUOMHNf1n9kDgfbfGvT8r7v738jpvm60tuW3QYePTOdvHzADep4HqSn0XEKiniDL38xD5C0PH4gSTXMyFm_qop&_nc_zt=23&_nc_ht=scontent.fhyd11-2.fna&_nc_gid=PAJ5iu4dHZ_n0Gqqgm7upA&oh=00_AfbnVN0Kgn-Z-HG5JPPqA84JwzH1wLBpfK_LbTLePYZK9Q&oe=68E16B95",
                    experience="25+ years",
                    specialization="Educational Leadership"
                ),
                FacultyMember(
                    name="Ms. Afreen Sami Ulah Khan", 
                    role="Mathematics HOD",
                    qualification="M.Sc. Mathematics, B.Ed., M.Phil.",
                    description="Specialized in making complex mathematical concepts easy to understand.",
                    image_path="https://images.unsplash.com/photo-1577881590026-6d5fd6c15037?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                    experience="15 years",
                    specialization="Algebra, Calculus"
                )
            ]
            db.session.add_all(sample_faculty)
            db.session.commit()
            
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
