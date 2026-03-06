"""
Online Job Portal - Flask Backend Application
==============================================
A complete job portal backend with SQLite database,
user authentication, job management, and admin panel.
Optimized for Vercel deployment.
"""

import os
import json
from functools import wraps

# Import Flask and other dependencies
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3

# Flask app configuration
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'job_portal_secret_key_2024')

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path - use /tmp on Vercel for ephemeral filesystem
# In local development, use the local database
if os.environ.get('VERCEL') == '1':
    DB_PATH = os.path.join('/tmp', 'database.db')
else:
    DB_PATH = os.path.join(BASE_DIR, 'backend', 'database.db')

# Configure template and static folders
app.template_folder = os.path.join(BASE_DIR, 'templates')
app.static_folder = os.path.join(BASE_DIR, 'static')

def get_db_connection():
    """Get database connection with row factory"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize database with all required tables"""
    try:
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
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

def seed_sample_data():
    """Insert sample companies and jobs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM companies')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample companies data
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
        
        # Sample jobs data
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
    except Exception as e:
        print(f"Seeding error: {e}")

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
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error in index: {e}")
        return f"Error loading page: {str(e)}", 500

# Jobs page
@app.route('/jobs')
def jobs():
    try:
        return render_template('jobs.html')
    except Exception as e:
        print(f"Error in jobs: {e}")
        return f"Error loading page: {str(e)}", 500

# Companies page
@app.route('/companies')
def companies():
    try:
        return render_template('companies.html')
    except Exception as e:
        print(f"Error in companies: {e}")
        return f"Error loading page: {str(e)}", 500

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
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
    except Exception as e:
        print(f"Error in login: {e}")
        return render_template('login.html', error='Server error occurred'), 500

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
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
    except Exception as e:
        print(f"Error in register: {e}")
        return render_template('register.html', error='Server error occurred'), 500

# Logout
@app.route('/logout')
def logout():
    try:
        session.clear()
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error in logout: {e}")
        return redirect(url_for('index'))

# Apply for job page
@app.route('/apply/<int:job_id>')
def apply_job(job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        job = cursor.fetchone()
        conn.close()
        
        if job:
            return render_template('apply.html', job=job)
        return redirect(url_for('jobs'))
    except Exception as e:
        print(f"Error in apply_job: {e}")
        return redirect(url_for('jobs'))

# ==================== API ENDPOINTS ====================

# Get all jobs
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC')
        jobs = cursor.fetchall()
        conn.close()
        
        jobs_list = [dict(row) for row in jobs]
        return jsonify(jobs_list)
    except Exception as e:
        print(f"Error in get_jobs: {e}")
        return jsonify({'error': 'Failed to fetch jobs'}), 500

# Get single job
@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        job = cursor.fetchone()
        conn.close()
        
        if job:
            return jsonify(dict(job))
        return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        print(f"Error in get_job: {e}")
        return jsonify({'error': 'Failed to fetch job'}), 500

# Add new job
@app.route('/api/add-job', methods=['POST'])
def add_job():
    try:
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
    except Exception as e:
        print(f"Error in add_job: {e}")
        return jsonify({'error': 'Failed to add job'}), 500

# Update job
@app.route('/api/update-job/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    try:
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
    except Exception as e:
        print(f"Error in update_job: {e}")
        return jsonify({'error': 'Failed to update job'}), 500

# Delete job
@app.route('/api/delete-job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Job deleted successfully'})
    except Exception as e:
        print(f"Error in delete_job: {e}")
        return jsonify({'error': 'Failed to delete job'}), 500

# Get all companies
@app.route('/api/companies', methods=['GET'])
def get_companies():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM companies')
        companies = cursor.fetchall()
        conn.close()
        
        companies_list = [dict(row) for row in companies]
        return jsonify(companies_list)
    except Exception as e:
        print(f"Error in get_companies: {e}")
        return jsonify({'error': 'Failed to fetch companies'}), 500

# Add new company
@app.route('/api/add-company', methods=['POST'])
def add_company():
    try:
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
    except Exception as e:
        print(f"Error in add_company: {e}")
        return jsonify({'error': 'Failed to add company'}), 500

# Submit job application
@app.route('/api/apply-job', methods=['POST'])
def apply_for_job():
    try:
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
    except Exception as e:
        print(f"Error in apply_for_job: {e}")
        return jsonify({'error': 'Failed to submit application'}), 500

# Get all applications
@app.route('/api/applications', methods=['GET'])
def get_applications():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM applications ORDER BY applied_at DESC')
        applications = cursor.fetchall()
        conn.close()
        
        applications_list = [dict(row) for row in applications]
        return jsonify(applications_list)
    except Exception as e:
        print(f"Error in get_applications: {e}")
        return jsonify({'error': 'Failed to fetch applications'}), 500

# ==================== ADMIN ROUTES ====================

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
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
    except Exception as e:
        print(f"Error in admin_dashboard: {e}")
        return f"Error: {str(e)}", 500

# Add Job Page
@app.route('/admin/add-job')
@admin_required
def admin_add_job():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM companies')
        companies = cursor.fetchall()
        conn.close()
        return render_template('admin/add_job.html', companies=companies)
    except Exception as e:
        print(f"Error in admin_add_job: {e}")
        return f"Error: {str(e)}", 500

# Manage Jobs Page
@app.route('/admin/manage-jobs')
@admin_required
def admin_manage_jobs():
    try:
        return render_template('admin/manage_jobs.html')
    except Exception as e:
        print(f"Error in admin_manage_jobs: {e}")
        return f"Error: {str(e)}", 500

# View Applications Page
@app.route('/admin/applications')
@admin_required
def admin_applications():
    try:
        return render_template('admin/applications.html')
    except Exception as e:
        print(f"Error in admin_applications: {e}")
        return f"Error: {str(e)}", 500

# ==================== VERCEL HANDLER ====================

def handler(event, context):
    """
    Vercel Python handler function.
    This is the entry point for Vercel's serverless functions.
    """
    # Parse the request
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    query_params = event.get('queryStringParameters', {})
    body = event.get('body', '')
    
    # Handle JSON body
    if body and headers.get('content-type') == 'application/json':
        try:
            body = json.loads(body)
        except:
            body = {}
    
    # Create a mock request object
    class MockRequest:
        def __init__(self, method, path, headers, args, json):
            self.method = method
            self.path = path
            self.headers = headers
            self.args = args
            self._json = json
            self.form = {}
            
        def form_get(self, key, default=None):
            if isinstance(self._json, dict):
                return self._json.get(key, default)
            return default
            
        def get(self, key, default=None):
            if isinstance(self._json, dict):
                return self._json.get(key, default)
            return default
            
        @property
        def json(self):
            return self._json
            
        @property
        def form(self):
            if isinstance(self._json, dict):
                return self._json
            return {}
    
    # Set up the request
    mock_request = MockRequest(http_method, path, headers, query_params, body)
    
    # Store form data for POST requests
    if http_method == 'POST' and isinstance(body, dict):
        for key, value in body.items():
            mock_request.form[key] = value
    
    # Override Flask's request
    from flask import globals as flask_globals
    flask_globals._request_ctx_stack.push(app.test_request_context(
        path=path,
        method=http_method,
        headers=headers,
        query_string='&'.join([f"{k}={v}" for k, v in (query_params or {}).items()])
    ))
    
    try:
        # Dispatch to Flask
        response = app.full_dispatch_request()
        
        # Get response data
        status_code = response.status_code
        response_headers = dict(response.headers)
        response_body = response.get_data(as_text=True)
        
        return {
            'statusCode': status_code,
            'headers': response_headers,
            'body': response_body
        }
    except Exception as e:
        print(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
    finally:
        flask_globals._request_ctx_stack.pop()

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

