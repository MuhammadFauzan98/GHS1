from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))

# Use different database paths for Vercel vs local
if os.environ.get('VERCEL'):
    # Vercel environment - use /tmp for SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/school.db'
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
else:
    # Local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'faculty_login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# Database Models
class Faculty(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with uploaded PYQPs
    pyqps = db.relationship('PYQP', backref='uploader', lazy=True)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<Faculty {self.username}>'

class FacultyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    experience = db.Column(db.String(100))
    specialization = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PYQP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    file_size = db.Column(db.Integer)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    replied_at = db.Column(db.DateTime)
    reply_message = db.Column(db.Text)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship('Faculty', backref='activity_logs')

@login_manager.user_loader
def load_user(user_id):
    return Faculty.query.get(int(user_id))

# Allowed extensions
ALLOWED_PDF_EXTENSIONS = {'pdf'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def log_activity(faculty_id, action, details=None, ip_address=None, user_agent=None):
    try:
        activity = ActivityLog(
            faculty_id=faculty_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        db.session.rollback()

# =====================
# PUBLIC ROUTES
# =====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.role.lower() in ['administrator', 'admin']:
            return redirect(url_for('faculty_dashboard'))
        elif current_user.role.lower() == 'faculty':
            return redirect(url_for('faculty_dashboard'))
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
        try:
            db.session.add(new_message)
            db.session.commit()
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('There was an error sending your message. Please try again.', 'error')
        
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
            
            log_activity(
                faculty.id,
                'login',
                f'Faculty {faculty.name} logged in',
                request.remote_addr,
                request.headers.get('User-Agent')
            )
            
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
    try:
        pyqp_count = PYQP.query.filter_by(uploaded_by=current_user.id).count()
        recent_pyqps = PYQP.query.filter_by(uploaded_by=current_user.id).order_by(PYQP.uploaded_at.desc()).limit(5).all()
        recent_activities = ActivityLog.query.filter_by(faculty_id=current_user.id).order_by(ActivityLog.created_at.desc()).limit(10).all()
        
        return render_template('auth/faculty_dashboard.html',
                             pyqp_count=pyqp_count,
                             recent_pyqps=recent_pyqps,
                             recent_activities=recent_activities)
    except Exception as e:
        flash('Error loading dashboard. Please try again.', 'error')
        return redirect(url_for('index'))

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
            
            try:
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
                
            except Exception as e:
                db.session.rollback()
                flash('Error uploading file. Please try again.', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload PDF files only.', 'error')
    
    try:
        total_pyqp = PYQP.query.count()
        recent_pyqps = PYQP.query.filter_by(uploaded_by=current_user.id).order_by(PYQP.uploaded_at.desc()).limit(10).all()
    except Exception as e:
        total_pyqp = 0
        recent_pyqps = []
    
    return render_template('auth/faculty_upload_pyqp.html',
                         total_pyqp=total_pyqp,
                         recent_pyqps=recent_pyqps,
                         current_year=datetime.now().year)

@app.route('/faculty/profile', methods=['GET', 'POST'])
@login_required
def faculty_profile():
    try:
        activities = ActivityLog.query.filter_by(faculty_id=current_user.id).order_by(ActivityLog.created_at.desc()).limit(20).all()
    except Exception as e:
        activities = []
    
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
        
        try:
            db.session.commit()
            
            log_activity(
                current_user.id,
                'update_profile',
                'Updated faculty profile information',
                request.remote_addr,
                request.headers.get('User-Agent')
            )
            
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
        
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
        
        # On Vercel, files might not persist, so return a placeholder
        if not os.path.exists(full_path):
            return redirect('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80')
        
        if not os.path.isfile(full_path):
            return "Not a file", 400
            
        return send_from_directory(uploads_dir, filename)
    except Exception as e:
        return redirect('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80')

@app.route('/download_pyqp/<int:paper_id>')
def download_pyqp(paper_id):
    try:
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
    except Exception as e:
        flash('Error downloading file. Please try again.', 'error')
        return redirect(url_for('pyqp'))

# =====================
# DATABASE INITIALIZATION
# =====================

def init_db():
    with app.app_context():
        try:
            # Create upload directories
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'pyqp'), exist_ok=True)
            
            # Create tables
            db.create_all()

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
                        image_path="https://scontent.fhyd11-2.fna.fbcdn.net/v/t39.30808-6/519085037_752778251032594_214901603916856522_n.jpg",
                        experience="25+ years",
                        specialization="Educational Leadership"
                    ),
                    FacultyMember(
                        name="Ms. Afreen Sami Ulah Khan", 
                        role="Mathematics HOD",
                        qualification="M.Sc. Mathematics, B.Ed., M.Phil.",
                        description="Specialized in making complex mathematical concepts easy to understand.",
                        image_path="https://images.unsplash.com/photo-1577881590026-6d5fd6c15037",
                        experience="15 years",
                        specialization="Algebra, Calculus"
                    )
                ]
                db.session.add_all(sample_faculty)
                db.session.commit()
                
            print("Database initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.session.rollback()

# =====================
# ERROR HANDLERS
# =====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# =====================
# APPLICATION STARTUP
# =====================

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # For Vercel deployment
    init_db()