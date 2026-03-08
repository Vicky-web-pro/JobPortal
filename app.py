"""
Online Job Portal - Flask Backend Application
==============================================
A complete job portal backend with SQLite database,
user authentication, job management, and admin panel.
Running locally on localhost.
"""

import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

# Import Flask and other dependencies
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import bcrypt

# Flask app configuration - use templates and static from root directory
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'job_portal_secret_key_2024'

# Database path - local database in project root
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

# Email configuration (configure these with your SMTP settings)
# For demo purposes, we'll simulate email sending
EMAIL_ENABLED = False
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = ''
SMTP_PASSWORD = ''
FROM_EMAIL = 'noreply@jobportal.com'

def send_confirmation_email(to_email, applicant_name, job_title, company_name):
    """Send job application confirmation email."""
    if not EMAIL_ENABLED:
        print(f"[DEMO EMAIL] To: {to_email}")
        print(f"[DEMO EMAIL] Subject: Job Application Confirmation")
        print(f"[DEMO EMAIL] Body: Dear {applicant_name}, Thank you for applying for {job_title} at {company_name}...")
        return True
    
    try:
        message = MIMEMultipart()
        message['From'] = FROM_EMAIL
        message['To'] = to_email
        message['Subject'] = 'Job Application Confirmation'
        
        body = f"""Dear {applicant_name},

Thank you for applying for the position of {job_title} at {company_name}.

We have successfully received your application.

Best regards,
Recruitment Team
{company_name}
"""
        
        message.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, message.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT NOT NULL,
            location TEXT NOT NULL,
            email TEXT NOT NULL,
            description TEXT,
            logo TEXT,
            image TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            company_id INTEGER,
            department TEXT NOT NULL,
            job_role TEXT NOT NULL,
            location TEXT NOT NULL,
            salary TEXT NOT NULL,
            job_type TEXT NOT NULL,
            description TEXT,
            company_email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            department TEXT NOT NULL,
            job_role TEXT NOT NULL,
            job_id INTEGER,
            company_name TEXT,
            resume TEXT,
            message TEXT,
            status TEXT DEFAULT 'Pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def seed_sample_data():
    """Insert sample companies and jobs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM companies')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    companies = [
        ('Google', 'Technology', 'Bangalore, Karnataka', 'careers@google.com', 
         'Google LLC is an American multinational technology company.',
         'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg',
         'https://images.unsplash.com/photo-1554475901-4538ddfbccc2?w=800'),
        ('Amazon', 'E-Commerce', 'Hyderabad, Telangana', 'jobs@amazon.com',
         'Amazon.com, Inc. is an American multinational technology company.',
         'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg',
         'https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=800'),
        ('Microsoft', 'Technology', 'Chennai, Tamil Nadu', 'careers@microsoft.com',
         'Microsoft Corporation is an American multinational technology corporation.',
         'https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg',
         'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800'),
        ('Apple', 'Technology', 'Bangalore, Karnataka', 'jobs@apple.com',
         'Apple Inc. designs, develops, and sells consumer electronics.',
         'https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg',
         'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800'),
        ('Meta', 'Technology', 'Hyderabad, Telangana', 'careers@meta.com',
         'Meta Platforms, Inc. is an American technology conglomerate.',
         'https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_logo.svg',
         'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800'),
        ('Tesla', 'Automotive', 'Bangalore, Karnataka', 'jobs@tesla.com',
         'Tesla, Inc. is an American electric vehicle and clean energy company.',
         'https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg',
         'https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800'),
        ('Netflix', 'Entertainment', 'Chennai, Tamil Nadu', 'jobs@netflix.com',
         'Netflix, Inc. is an American over-the-top content platform.',
         'https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg',
         'https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=800'),
        ('Adobe', 'Technology', 'Bangalore, Karnataka', 'careers@adobe.com',
         'Adobe Inc. is an American multinational computer software company.',
         'https://upload.wikimedia.org/wikipedia/commons/4/4c/Adobe_Creative_Cloud_rainbow_icon.svg',
         'https://images.unsplash.com/photo-1534972195531-d756b9bfa9f2?w=800'),
        ('Oracle', 'Technology', 'Hyderabad, Telangana', 'jobs@oracle.com',
         'Oracle Corporation is an American multinational computer technology corporation.',
         'https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg',
         'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800'),
        ('Salesforce', 'Technology', 'Mumbai, Maharashtra', 'careers@salesforce.com',
         'Salesforce, Inc. is an American cloud-based software company.',
         'https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce_logo.svg',
         'https://images.unsplash.com/photo-1551434678-e076c223a692?w=800'),
    ]
    
    cursor.executemany('''
        INSERT INTO companies (name, industry, location, email, description, logo, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', companies)
    
    jobs = [
        ('Software Developer', 'Google', 1, 'Information Technology', 'Software Developer', 'Bangalore, Karnataka', '₹15,00,000 - ₹25,00,000', 'Full Time',
         'We are looking for a skilled Software Developer to join our team.', 'careers@google.com'),
        ('Machine Learning Engineer', 'Google', 1, 'Artificial Intelligence', 'ML Engineer', 'Bangalore, Karnataka', '₹20,00,000 - ₹35,00,000', 'Full Time',
         'Build cutting-edge ML models and AI solutions at Google.', 'careers@google.com'),
        ('Cloud Engineer', 'Google', 1, 'Cloud Computing', 'Cloud Engineer', 'Bangalore, Karnataka', '₹18,00,000 - ₹30,00,000', 'Full Time',
         'Work on Google Cloud Platform and build scalable solutions.', 'careers@google.com'),
        ('Python Developer', 'Amazon', 2, 'Software Development', 'Python Developer', 'Hyderabad, Telangana', '₹12,00,000 - ₹20,00,000', 'Full Time',
         'Join our team as a Python Developer and build scalable applications.', 'jobs@amazon.com'),
        ('Full Stack Developer', 'Amazon', 2, 'Software Development', 'Full Stack Developer', 'Hyderabad, Telangana', '₹14,00,000 - ₹22,00,000', 'Full Time',
         'Work on both frontend and backend technologies at Amazon.', 'jobs@amazon.com'),
        ('Data Scientist', 'Amazon', 2, 'Data Science', 'Data Scientist', 'Hyderabad, Telangana', '₹16,00,000 - ₹28,00,000', 'Full Time',
         'Analyze data and build ML models to drive business decisions.', 'jobs@amazon.com'),
        ('Web Developer', 'Microsoft', 3, 'Web Development', 'Web Developer', 'Chennai, Tamil Nadu', '₹8,00,000 - ₹15,00,000', 'Full Time',
         'Create stunning web applications with Microsoft technologies.', 'careers@microsoft.com'),
        ('DevOps Engineer', 'Microsoft', 3, 'DevOps', 'DevOps Engineer', 'Chennai, Tamil Nadu', '₹15,00,000 - ₹25,00,000', 'Full Time',
         'Manage CI/CD pipelines and cloud infrastructure.', 'careers@microsoft.com'),
        ('Security Analyst', 'Microsoft', 3, 'Cyber Security', 'Security Analyst', 'Chennai, Tamil Nadu', '₹12,00,000 - ₹20,00,000', 'Full Time',
         'Protect Microsoft systems from cyber threats.', 'careers@microsoft.com'),
        ('iOS Developer', 'Apple', 4, 'Software Development', 'iOS Developer', 'Bangalore, Karnataka', '₹18,00,000 - ₹30,00,000', 'Full Time',
         'Build amazing iOS applications for Apple devices.', 'jobs@apple.com'),
    ]
    
    cursor.executemany('''
        INSERT INTO jobs (title, company, company_id, department, job_role, location, salary, job_type, description, company_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', jobs)
    
    cursor.execute('''
        INSERT INTO users (name, email, password, is_admin)
        VALUES (?, ?, ?, ?)
    ''', ('Admin', 'admin@jobportal.com', 'admin123', 1))
    
    conn.commit()
    conn.close()
    print("Sample data seeded successfully!")

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jobs')
def jobs():
    return render_template('jobs.html')

@app.route('/companies')
def companies():
    return render_template('companies.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_admin'] = user['is_admin']
            
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                          (name, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Email already exists')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/apply/<int:job_id>')
def apply_job(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if job:
        return render_template('apply.html', job=job)
    return redirect(url_for('jobs'))

# ==================== API ENDPOINTS ====================

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    keyword = request.args.get('keyword', '')
    department = request.args.get('department', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM jobs WHERE 1=1'
    params = []
    
    if keyword:
        query += ' AND (title LIKE ? OR company LIKE ? OR job_role LIKE ?)'
        keyword_pattern = f'%{keyword}%'
        params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
    
    if department:
        query += ' AND department = ?'
        params.append(department)
    
    if job_type:
        query += ' AND job_type = ?'
        params.append(job_type)
    
    if location:
        query += ' AND location LIKE ?'
        params.append(f'%{location}%')
    
    query += ' ORDER BY created_at DESC'
    
    cursor.execute(query, params)
    jobs = cursor.fetchall()
    conn.close()
    
    jobs_list = [dict(row) for row in jobs]
    return jsonify(jobs_list)

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if job:
        return jsonify(dict(job))
    return jsonify({'error': 'Job not found'}), 404

@app.route('/api/add-job', methods=['POST'])
def add_job():
    data = request.json
    
    required_fields = ['title', 'company', 'department', 'job_role', 'location', 'salary', 'job_type', 'company_email']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (title, company, company_id, department, job_role, location, salary, job_type, description, company_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['title'], data['company'], data.get('company_id'), data['department'], 
          data['job_role'], data['location'], data['salary'], data['job_type'], 
          data.get('description', ''), data['company_email']))
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'message': 'Job added successfully', 'job_id': job_id})

@app.route('/api/delete-job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Job deleted successfully'})

@app.route('/api/companies', methods=['GET'])
def get_companies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM companies')
    companies = cursor.fetchall()
    conn.close()
    
    companies_list = [dict(row) for row in companies]
    return jsonify(companies_list)

@app.route('/api/apply-job', methods=['POST'])
def apply_for_job():
    data = request.json
    
    required_fields = ['name', 'email', 'mobile', 'department', 'job_role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Get user_id from session if logged in
    user_id = session.get('user_id')
    
    # Get current timestamp for applied_at
    applied_at = datetime.now()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applications (user_id, name, email, mobile, department, job_role, job_id, company_name, resume, message, applied_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, data['name'], data['email'], data['mobile'], data['department'],
          data['job_role'], data.get('job_id'), data.get('company_name'), data.get('resume'), 
          data.get('message'), applied_at, 'Applied'))
    conn.commit()
    
    job_title = data.get('job_title', data.get('job_role', 'Unknown Position'))
    company_name = data.get('company_name', 'The Company')
    
    conn.close()
    
    email_sent = send_confirmation_email(
        to_email=data['email'],
        applicant_name=data['name'],
        job_title=job_title,
        company_name=company_name
    )
    
    return jsonify({
        'message': 'Application submitted successfully!',
        'email_sent': email_sent
    })

@app.route('/api/applications', methods=['GET'])
def get_applications():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM applications ORDER BY applied_at DESC')
    applications = cursor.fetchall()
    conn.close()
    
    applications_list = [dict(row) for row in applications]
    return jsonify(applications_list)

# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in') and session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND is_admin = 1', (email,))
        user = cursor.fetchone()
        
        if user:
            stored_password = user['password']
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    password_valid = True
                else:
                    password_valid = False
            except Exception:
                if stored_password == password:
                    password_valid = True
                else:
                    password_valid = False
            
            if password_valid:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['is_admin'] = user['is_admin']
                session['admin_logged_in'] = True
                conn.close()
                return redirect(url_for('admin_dashboard'))
        
        conn.close()
        return render_template('admin/login.html', error='Invalid admin credentials')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    jobs_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM companies')
    companies_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM applications')
    applications_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    users_count = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                           jobs_count=jobs_count,
                           companies_count=companies_count,
                           applications_count=applications_count,
                           users_count=users_count)

@app.route('/admin/add-job')
@admin_required
def admin_add_job():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM companies')
    companies = cursor.fetchall()
    conn.close()
    return render_template('admin/add_job.html', companies=companies)

@app.route('/admin/manage-jobs')
@admin_required
def admin_manage_jobs():
    return render_template('admin/manage_jobs.html')

@app.route('/admin/applications')
@admin_required
def admin_applications():
    return render_template('admin/applications.html')

# ==================== USER DASHBOARD ROUTES ====================

@app.route('/my-applications')
@login_required
def my_applications():
    """User's job applications page - only for regular users, not admins"""
    
    # Redirect admins to admin dashboard - My Applications is for users only
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, j.title as job_title, j.location as job_location, j.salary as job_salary
        FROM applications a
        LEFT JOIN jobs j ON a.job_id = j.id
        WHERE a.user_id = ?
        ORDER BY a.applied_at DESC
    ''', (user_id,))
    applications = cursor.fetchall()
    conn.close()
    
    # Convert date strings to datetime objects for strftime in template
    applications_list = []
    for app in applications:
        app_dict = dict(app)
        if app_dict.get('applied_at'):
            try:
                app_dict['applied_at'] = datetime.strptime(app_dict['applied_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If date format is different, try parsing with just date part
                try:
                    app_dict['applied_at'] = datetime.strptime(app_dict['applied_at'][:10], '%Y-%m-%d')
                except ValueError:
                    pass  # Keep original string if parsing fails
        applications_list.append(app_dict)
    
    return render_template('my_applications.html', applications=applications_list)

# ==================== API FOR STATUS UPDATE ====================

@app.route('/api/update-application-status', methods=['POST'])
@admin_required
def update_application_status():
    """API endpoint for admin to update application status"""
    data = request.json
    application_id = data.get('application_id')
    new_status = data.get('status')
    
    if not application_id or not new_status:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # New recruitment status workflow
    valid_statuses = ['Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected']
    if new_status not in valid_statuses:
        return jsonify({'error': 'Invalid status value'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE applications SET status = ? WHERE id = ?', (new_status, application_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Status updated successfully', 'status': new_status})

# ==================== MAIN ====================

if __name__ == "__main__":
    # Initialize database and seed data
    init_db()
    seed_sample_data()
    
    # Run the Flask development server
    print("\n" + "="*50)
    print("🎉 Job Portal is running!")
    print("📍 Open your browser and visit: http://127.0.0.1:5000")
    print("👤 Admin Login: admin@jobportal.com / admin123")
    print("="*50 + "\n")
    
    app.run(debug=True)

