"""
Online Job Portal - Flask Backend Application
==============================================
A complete job portal backend with SQLite database,
user authentication, job management, and admin panel.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
from functools import wraps

# Flask app configuration
app = Flask(__name__)
app.secret_key = 'job_portal_secret_key_2024'

# Get the base directory (parent of backend folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
DB_PATH = os.path.join(BASE_DIR, 'backend', 'database.db')

# Configure template and static folders
app.template_folder = os.path.join(BASE_DIR, 'templates')
app.static_folder = os.path.join(BASE_DIR, 'static')

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Companies table
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
    
    # Jobs table
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
    
    # Applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            department TEXT NOT NULL,
            job_role TEXT NOT NULL,
            job_id INTEGER,
            resume TEXT,
            message TEXT,
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
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM companies')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Sample companies data (duplicate as per requirements)
    companies = [
        ('Google', 'Technology', 'Bangalore, Karnataka', 'careers@google.com', 
         'Google LLC is an American multinational technology company specializing in Internet-related services and products.',
         'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg',
         'https://images.unsplash.com/photo-1554475901-4538ddfbccc2?w=800'),
        ('Amazon', 'E-Commerce', 'Hyderabad, Telangana', 'jobs@amazon.com',
         'Amazon.com, Inc. is an American multinational technology company focusing on e-commerce, cloud computing, and AI.',
         'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg',
         'https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=800'),
        ('Microsoft', 'Technology', 'Chennai, Tamil Nadu', 'careers@microsoft.com',
         'Microsoft Corporation is an American multinational technology corporation that produces software, consumer electronics, and personal computers.',
         'https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg',
         'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800'),
        ('TCS', 'Information Technology', 'Mumbai, Maharashtra', 'recruit@tcs.com',
         'Tata Consultancy Services is an Indian multinational information technology services and consulting company.',
         'https://upload.wikimedia.org/wikipedia/commons/4/4f/TCS_%28Tata_Consultancy_Services%29_logo.svg',
         'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800'),
        ('Infosys', 'Information Technology', 'Pune, Maharashtra', 'careers@infosys.com',
         'Infosys Limited is an Indian multinational information technology company that provides business consulting and services.',
         'https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg',
         'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800'),
        ('Wipro', 'Information Technology', 'Bangalore, Karnataka', 'jobs@wipro.com',
         'Wipro Limited is an Indian multinational corporation that provides information technology consulting and services.',
         'https://upload.wikimedia.org/wikipedia/commons/f/fc/Wipro_Primary_Logo.png',
         'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=800'),
    ]
    
    cursor.executemany('''
        INSERT INTO companies (name, industry, location, email, description, logo, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', companies)
    
    # Sample jobs data (duplicate as per requirements)
    jobs = [
        ('Software Developer', 'Google', 1, 'Engineering', 'Software Developer', 'Bangalore, Karnataka', '₹15,00,000 - ₹25,00,000', 'Full Time',
         'We are looking for a skilled Software Developer to join our team.', 'careers@google.com'),
        ('Python Developer', 'Amazon', 2, 'Engineering', 'Python Developer', 'Hyderabad, Telangana', '₹12,00,000 - ₹20,00,000', 'Full Time',
         'Join our team as a Python Developer and build scalable applications.', 'jobs@amazon.com'),
        ('Web Developer', 'Microsoft', 3, 'Engineering', 'Web Developer', 'Chennai, Tamil Nadu', '₹8,00,000 - ₹15,00,000', 'Full Time',
         'Create stunning web applications with Microsoft technologies.', 'careers@microsoft.com'),
        ('Data Analyst', 'TCS', 4, 'Analytics', 'Data Analyst', 'Mumbai, Maharashtra', '₹6,00,000 - ₹12,00,000', 'Full Time',
         'Analyze data and provide insights to drive business decisions.', 'recruit@tcs.com'),
        ('UI/UX Designer', 'Infosys', 5, 'Design', 'UI/UX Designer', 'Pune, Maharashtra', '₹7,00,000 - ₹14,00,000', 'Full Time',
         'Design intuitive and beautiful user interfaces.', 'careers@infosys.com'),
        ('Software Engineer', 'Wipro', 6, 'Engineering', 'Software Engineer', 'Bangalore, Karnataka', '₹10,00,000 - ₹18,00,000', 'Full Time',
         'Build enterprise-grade software solutions.', 'jobs@wipro.com'),
        ('Junior Python Developer', 'Google', 1, 'Engineering', 'Python Developer', 'Bangalore, Karnataka', '₹5,00,000 - ₹8,00,000', 'Full Time',
         'Start your career as a Python Developer at Google.', 'careers@google.com'),
        ('Full Stack Developer', 'Amazon', 2, 'Engineering', 'Full Stack Developer', 'Hyderabad, Telangana', '₹14,00,000 - ₹22,00,000', 'Full Time',
         'Work on both frontend and backend technologies.', 'jobs@amazon.com'),
        ('Machine Learning Engineer', 'Microsoft', 3, 'Engineering', 'ML Engineer', 'Chennai, Tamil Nadu', '₹18,00,000 - ₹30,00,000', 'Full Time',
         'Build ML models and AI solutions.', 'careers@microsoft.com'),
        ('DevOps Engineer', 'TCS', 4, 'Engineering', 'DevOps Engineer', 'Mumbai, Maharashtra', '₹10,00,000 - ₹16,00,000', 'Full Time',
         'Manage CI/CD pipelines and cloud infrastructure.', 'recruit@tcs.com'),
        ('Frontend Developer', 'Infosys', 5, 'Engineering', 'Frontend Developer', 'Pune, Maharashtra', '₹6,00,000 - ₹12,00,000', 'Full Time',
         'Create responsive web interfaces.', 'careers@infosys.com'),
        ('Backend Developer', 'Wipro', 6, 'Engineering', 'Backend Developer', 'Bangalore, Karnataka', '₹9,00,000 - ₹15,00,000', 'Full Time',
         'Develop server-side applications.', 'jobs@wipro.com'),
    ]
    
    cursor.executemany('''
        INSERT INTO jobs (title, company, company_id, department, job_role, location, salary, job_type, description, company_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', jobs)
    
    # Create admin user (password: admin123)
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
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Jobs page
@app.route('/jobs')
def jobs():
    return render_template('jobs.html')

# Companies page
@app.route('/companies')
def companies():
    return render_template('companies.html')

# Login page
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

# Register page
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

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Apply for job page
@app.route('/apply/<int:job_id>')
def apply_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if job:
        return render_template('apply.html', job=job)
    return redirect(url_for('jobs'))

# ==================== API ENDPOINTS ====================

# Get all jobs
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC')
    jobs = cursor.fetchall()
    conn.close()
    
    jobs_list = [dict(row) for row in jobs]
    return jsonify(jobs_list)

# Get single job
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

# Add new job
@app.route('/api/add-job', methods=['POST'])
def add_job():
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (title, company, company_id, department, job_role, location, salary, job_type, description, company_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['title'], data['company'], data.get('company_id'), data['department'], 
          data['job_role'], data['location'], data['salary'], data['job_type'], 
          data['description'], data['company_email']))
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'message': 'Job added successfully', 'job_id': job_id})

# Update job
@app.route('/api/update-job/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE jobs SET title=?, company=?, department=?, job_role=?, location=?, 
        salary=?, job_type=?, description=?, company_email=?
        WHERE id=?
    ''', (data['title'], data['company'], data['department'], data['job_role'],
          data['location'], data['salary'], data['job_type'], data['description'],
          data['company_email'], job_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Job updated successfully'})

# Delete job
@app.route('/api/delete-job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Job deleted successfully'})

# Get all companies
@app.route('/api/companies', methods=['GET'])
def get_companies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM companies')
    companies = cursor.fetchall()
    conn.close()
    
    companies_list = [dict(row) for row in companies]
    return jsonify(companies_list)

# Add new company
@app.route('/api/add-company', methods=['POST'])
def add_company():
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO companies (name, industry, location, email, description, logo, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['industry'], data['location'], data['email'],
          data['description'], data.get('logo'), data.get('image')))
    conn.commit()
    company_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'message': 'Company added successfully', 'company_id': company_id})

# Submit job application
@app.route('/api/apply-job', methods=['POST'])
def apply_for_job():
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applications (name, email, mobile, department, job_role, job_id, resume, message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['email'], data['mobile'], data['department'],
          data['job_role'], data.get('job_id'), data.get('resume'), data.get('message')))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Application submitted successfully!'})

# Get all applications
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

# Admin Dashboard
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

# Add Job Page
@app.route('/admin/add-job')
@admin_required
def admin_add_job():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM companies')
    companies = cursor.fetchall()
    conn.close()
    return render_template('admin/add_job.html', companies=companies)

# Manage Jobs Page
@app.route('/admin/manage-jobs')
@admin_required
def admin_manage_jobs():
    return render_template('admin/manage_jobs.html')

# View Applications Page
@app.route('/admin/applications')
@admin_required
def admin_applications():
    return render_template('admin/applications.html')

# ==================== MAIN ====================

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Seed sample data
    seed_sample_data()
    # Run the app
    print("\n" + "="*50)
    print("Job Portal Started Successfully!")
    print("="*50)
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("Admin Login: admin@jobportal.com / admin123")
    print("="*50 + "\n")
    app.run(debug=True)

