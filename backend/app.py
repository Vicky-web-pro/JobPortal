"""
Online Job Portal - Flask Backend Application
==============================================
A complete job portal backend with SQLite database,
user authentication, job management, and admin panel.
Optimized for Vercel deployment.
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

# Import Flask and other dependencies
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import bcrypt

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

# Email configuration (configure these with your SMTP settings)
# For demo purposes, we'll simulate email sending
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true'
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@jobportal.com')

def send_confirmation_email(to_email, applicant_name, job_title, company_name):
    """
    Send job application confirmation email to the applicant.
    Returns True if email sent successfully, False otherwise.
    """
    if not EMAIL_ENABLED:
        # Log the email instead of sending (for demo purposes)
        print(f"[DEMO EMAIL] To: {to_email}")
        print(f"[DEMO EMAIL] Subject: Job Application Confirmation")
        print(f"[DEMO EMAIL] Body: Dear {applicant_name}, Thank you for applying for {job_title} at {company_name}...")
        return True
    
    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = FROM_EMAIL
        message['To'] = to_email
        message['Subject'] = 'Job Application Confirmation'
        
        # Email body
        body = f"""Dear {applicant_name},

Thank you for applying for the position of {job_title} at {company_name}.

We have successfully received your application. Our recruitment team will review your application and contact you if your profile matches the requirements.

Best regards,
Recruitment Team
{company_name}

---
This is an automated email. Please do not reply to this message.
"""
        
        message.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, message.as_string())
        server.quit()
        
        print(f"Confirmation email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

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
    """Insert 20+ sample companies and 40+ jobs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM companies')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample companies data - 20+ companies
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
            ('TCS', 'Information Technology', 'Mumbai, Maharashtra', 'recruit@tcs.com',
             'Tata Consultancy Services is an Indian multinational IT services company.',
             'https://upload.wikimedia.org/wikipedia/commons/4/4f/TCS_%28Tata_Consultancy_Services%29_logo.svg',
             'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800'),
            ('Infosys', 'Information Technology', 'Bangalore, Karnataka', 'careers@infosys.com',
             'Infosys Limited is an Indian multinational IT company.',
             'https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg',
             'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800'),
            ('Wipro', 'Information Technology', 'Bangalore, Karnataka', 'jobs@wipro.com',
             'Wipro Limited is an Indian multinational corporation.',
             'https://upload.wikimedia.org/wikipedia/commons/f/fc/Wipro_Primary_Logo.png',
             'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=800'),
            ('HCL Technologies', 'Information Technology', 'Chennai, Tamil Nadu', 'careers@hcl.com',
             'HCL Technologies is an Indian multinational IT services company.',
             'https://upload.wikimedia.org/wikipedia/commons/f/f6/HCL_Technologies_logo.svg',
             'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800'),
            ('Tech Mahindra', 'Information Technology', 'Pune, Maharashtra', 'jobs@techmahindra.com',
             'Tech Mahindra is an Indian multinational IT services company.',
             'https://upload.wikimedia.org/wikipedia/commons/2/29/Tech_Mahindra_Logo.svg',
             'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800'),
            ('Capgemini', 'Information Technology', 'Mumbai, Maharashtra', 'careers@capgemini.com',
             'Capgemini SE is a French multinational corporation.',
             'https://upload.wikimedia.org/wikipedia/commons/6/6e/Capgemini_logo.svg',
             'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800'),
            ('Cognizant', 'Information Technology', 'Chennai, Tamil Nadu', 'jobs@cognizant.com',
             'Cognizant is an American multinational IT services company.',
             'https://upload.wikimedia.org/wikipedia/commons/5/55/Cognizant_logo_2022.svg',
             'https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800'),
            ('Deloitte', 'Consulting', 'Bangalore, Karnataka', 'careers@deloitte.com',
             'Deloitte is a multinational professional services network.',
             'https://upload.wikimedia.org/wikipedia/commons/5/56/Deloitte_Logo.svg',
             'https://images.unsplash.com/photo-1556761175-4b46a572b786?w=800'),
            ('IBM', 'Information Technology', 'Pune, Maharashtra', 'jobs@ibm.com',
             'International Business Machines Corporation is an American multinational.',
             'https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg',
             'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800'),
            ('Accenture', 'Consulting', 'Hyderabad, Telangana', 'careers@accenture.com',
             'Accenture plc is a professional services company.',
             'https://upload.wikimedia.org/wikipedia/commons/c/cd/Accenture_logo.svg',
             'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800'),
        ]
        
        cursor.executemany('''
            INSERT INTO companies (name, industry, location, email, description, logo, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', companies)
        
        # Sample jobs data - 40+ jobs
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
            ('UI/UX Designer', 'Apple', 4, 'UI/UX Design', 'UI/UX Designer', 'Bangalore, Karnataka', '₹15,00,000 - ₹25,00,000', 'Full Time',
             'Design intuitive and beautiful user interfaces.', 'jobs@apple.com'),
            ('React Developer', 'Meta', 5, 'Web Development', 'React Developer', 'Hyderabad, Telangana', '₹16,00,000 - ₹28,00,000', 'Full Time',
             'Build web applications using React and modern technologies.', 'careers@meta.com'),
            ('Backend Engineer', 'Meta', 5, 'Software Development', 'Backend Engineer', 'Hyderabad, Telangana', '₹18,00,000 - ₹32,00,000', 'Full Time',
             'Scale Meta infrastructure and build robust APIs.', 'careers@meta.com'),
            ('Embedded Engineer', 'Tesla', 6, 'Software Development', 'Embedded Engineer', 'Bangalore, Karnataka', '₹20,00,000 - ₹35,00,000', 'Full Time',
             'Work on embedded systems for Tesla vehicles.', 'jobs@tesla.com'),
            ('Data Engineer', 'Tesla', 6, 'Data Science', 'Data Engineer', 'Bangalore, Karnataka', '₹16,00,000 - ₹28,00,000', 'Full Time',
             'Build data pipelines for Tesla energy products.', 'jobs@tesla.com'),
            ('Content Engineer', 'Netflix', 7, 'Software Development', 'Content Engineer', 'Chennai, Tamil Nadu', '₹22,00,000 - ₹40,00,000', 'Full Time',
             'Build Netflix content delivery systems.', 'jobs@netflix.com'),
            ('UX Researcher', 'Adobe', 8, 'UI/UX Design', 'UX Researcher', 'Bangalore, Karnataka', '₹12,00,000 - ₹22,00,000', 'Full Time',
             'Conduct user research to improve Adobe products.', 'careers@adobe.com'),
            ('Database Administrator', 'Oracle', 9, 'Information Technology', 'DBA', 'Hyderabad, Telangana', '₹14,00,000 - ₹24,00,000', 'Full Time',
             'Manage Oracle databases and ensure high availability.', 'jobs@oracle.com'),
            ('Salesforce Developer', 'Salesforce', 10, 'Software Development', 'Salesforce Developer', 'Mumbai, Maharashtra', '₹12,00,000 - ₹20,00,000', 'Full Time',
             'Build custom Salesforce solutions.', 'careers@salesforce.com'),
            ('Data Analyst', 'TCS', 11, 'Business Analytics', 'Data Analyst', 'Mumbai, Maharashtra', '₹6,00,000 - ₹12,00,000', 'Full Time',
             'Analyze data and provide insights to drive business decisions.', 'recruit@tcs.com'),
            ('Network Engineer', 'TCS', 11, 'Networking', 'Network Engineer', 'Mumbai, Maharashtra', '₹5,00,000 - ₹10,00,000', 'Full Time',
             'Manage and maintain network infrastructure.', 'recruit@tcs.com'),
            ('Java Developer', 'TCS', 11, 'Software Development', 'Java Developer', 'Mumbai, Maharashtra', '₹6,00,000 - ₹12,00,000', 'Full Time',
             'Develop Java applications for TCS clients.', 'recruit@tcs.com'),
            ('UI/UX Designer', 'Infosys', 12, 'UI/UX Design', 'UI/UX Designer', 'Bangalore, Karnataka', '₹7,00,000 - ₹14,00,000', 'Full Time',
             'Design intuitive and beautiful user interfaces.', 'careers@infosys.com'),
            ('Business Analyst', 'Infosys', 12, 'Business Analytics', 'Business Analyst', 'Bangalore, Karnataka', '₹8,00,000 - ₹15,00,000', 'Full Time',
             'Analyze business requirements and provide solutions.', 'careers@infosys.com'),
            ('Cloud Developer', 'Infosys', 12, 'Cloud Computing', 'Cloud Developer', 'Bangalore, Karnataka', '₹9,00,000 - ₹16,00,000', 'Full Time',
             'Build cloud-native applications.', 'careers@infosys.com'),
            ('Software Engineer', 'Wipro', 13, 'Software Development', 'Software Engineer', 'Bangalore, Karnataka', '₹10,00,000 - ₹18,00,000', 'Full Time',
             'Build enterprise-grade software solutions.', 'jobs@wipro.com'),
            ('Customer Support', 'Wipro', 13, 'Customer Support', 'Customer Support Executive', 'Bangalore, Karnataka', '₹3,00,000 - ₹6,00,000', 'Full Time',
             'Provide technical support to Wipro clients.', 'jobs@wipro.com'),
            ('Cyber Security Analyst', 'HCL Technologies', 14, 'Cyber Security', 'Security Analyst', 'Chennai, Tamil Nadu', '₹8,00,000 - ₹15,00,000', 'Full Time',
             'Protect HCL systems from security threats.', 'careers@hcl.com'),
            ('QA Engineer', 'Tech Mahindra', 15, 'Software Development', 'QA Engineer', 'Pune, Maharashtra', '₹5,00,000 - ₹10,00,000', 'Full Time',
             'Test and ensure software quality.', 'jobs@techmahindra.com'),
            ('SAP Consultant', 'Capgemini', 16, 'Information Technology', 'SAP Consultant', 'Mumbai, Maharashtra', '₹10,00,000 - ₹18,00,000', 'Full Time',
             'Implement SAP solutions for clients.', 'careers@capgemini.com'),
            ('Healthcare Analyst', 'Cognizant', 17, 'Healthcare', 'Healthcare Analyst', 'Chennai, Tamil Nadu', '₹8,00,000 - ₹14,00,000', 'Full Time',
             'Analyze healthcare data and improve patient outcomes.', 'jobs@cognizant.com'),
            ('Automation Engineer', 'Cognizant', 17, 'DevOps', 'Automation Engineer', 'Chennai, Tamil Nadu', '₹7,00,000 - ₹13,00,000', 'Full Time',
             'Automate business processes using RPA.', 'jobs@cognizant.com'),
            ('Financial Analyst', 'Deloitte', 18, 'Finance', 'Financial Analyst', 'Bangalore, Karnataka', '₹12,00,000 - ₹22,00,000', 'Full Time',
             'Provide financial consulting services.', 'careers@deloitte.com'),
            ('Risk Analyst', 'Deloitte', 18, 'Finance', 'Risk Analyst', 'Bangalore, Karnataka', '₹10,00,000 - ₹18,00,000', 'Full Time',
             'Assess and manage financial risks.', 'careers@deloitte.com'),
            ('Mainframe Developer', 'IBM', 19, 'Software Development', 'Mainframe Developer', 'Pune, Maharashtra', '₹8,00,000 - ₹15,00,000', 'Full Time',
             'Develop and maintain mainframe applications.', 'jobs@ibm.com'),
            ('Strategy Consultant', 'Accenture', 20, 'Business Analytics', 'Strategy Consultant', 'Hyderabad, Telangana', '₹15,00,000 - ₹28,00,000', 'Full Time',
             'Provide strategic consulting to Fortune 500 companies.', 'careers@accenture.com'),
            ('AI Engineer', 'Accenture', 20, 'Artificial Intelligence', 'AI Engineer', 'Hyderabad, Telangana', '₹14,00,000 - ₹25,00,000', 'Full Time',
             'Build AI solutions for Accenture clients.', 'careers@accenture.com'),
            ('Junior Web Developer', 'Google', 1, 'Web Development', 'Junior Web Developer', 'Bangalore, Karnataka', '₹5,00,000 - ₹8,00,000', 'Full Time',
             'Start your career as a Web Developer at Google.', 'careers@google.com'),
            ('Business Development Manager', 'Amazon', 2, 'Marketing', 'BD Manager', 'Hyderabad, Telangana', '₹15,00,000 - ₹25,00,000', 'Full Time',
             'Drive business growth at Amazon.', 'jobs@amazon.com'),
            ('Product Manager', 'Microsoft', 3, 'Business Analytics', 'Product Manager', 'Chennai, Tamil Nadu', '₹20,00,000 - ₹35,00,000', 'Full Time',
             'Lead product development at Microsoft.', 'careers@microsoft.com'),
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
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error in index: {e}")
        return f"Error loading page: {str(e)}", 500

@app.route('/jobs')
def jobs():
    try:
        return render_template('jobs.html')
    except Exception as e:
        print(f"Error in jobs: {e}")
        return f"Error loading page: {str(e)}", 500

@app.route('/companies')
def companies():
    try:
        return render_template('companies.html')
    except Exception as e:
        print(f"Error in companies: {e}")
        return f"Error loading page: {str(e)}", 500

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

@app.route('/logout')
def logout():
    try:
        session.clear()
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error in logout: {e}")
        return redirect(url_for('index'))

@app.route('/apply/<int:job_id>')
def apply_job(job_id):
    try:
        # Check if user is logged in
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
    except Exception as e:
        print(f"Error in apply_job: {e}")
        return redirect(url_for('jobs'))

# ==================== API ENDPOINTS ====================

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
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
    except Exception as e:
        print(f"Error in get_jobs: {e}")
        return jsonify({'error': 'Failed to fetch jobs'}), 500

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

@app.route('/api/add-job', methods=['POST'])
def add_job():
    try:
        data = request.json
        
        # Validate required fields
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
    except Exception as e:
        print(f"Error in add_job: {e}")
        return jsonify({'error': 'Failed to add job'}), 500

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
              data['location'], data['salary'], data['job_type'], data.get('description', ''),
              data['company_email'], job_id))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Job updated successfully'})
    except Exception as e:
        print(f"Error in update_job: {e}")
        return jsonify({'error': 'Failed to update job'}), 500

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
              data.get('description', ''), data.get('logo'), data.get('image')))
        conn.commit()
        company_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'message': 'Company added successfully', 'company_id': company_id})
    except Exception as e:
        print(f"Error in add_company: {e}")
        return jsonify({'error': 'Failed to add company'}), 500

@app.route('/api/apply-job', methods=['POST'])
def apply_for_job():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'email', 'mobile', 'department', 'job_role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO applications (name, email, mobile, department, job_role, job_id, resume, message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['mobile'], data['department'],
              data['job_role'], data.get('job_id'), data.get('resume'), data.get('message')))
        conn.commit()
        
        # Get job details for email
        job_title = data.get('job_title', data.get('job_role', 'Unknown Position'))
        company_name = data.get('company_name', 'The Company')
        
        conn.close()
        
        # Send confirmation email
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
    except Exception as e:
        print(f"Error in apply_for_job: {e}")
        return jsonify({'error': 'Failed to submit application'}), 500

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

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login route with separate admin authentication."""
    try:
        if session.get('admin_logged_in') and session.get('is_admin'):
            return redirect(url_for('admin_dashboard'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                return render_template('admin/login.html', error='Please enter both email and password')
            
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
                        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        cursor.execute('UPDATE users SET password = ? WHERE id = ?', 
                                     (hashed.decode('utf-8'), user['id']))
                        conn.commit()
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
    
    except Exception as e:
        print(f"Error in admin_login: {e}")
        return render_template('admin/login.html', error='Server error occurred'), 500

@app.route('/admin/logout')
def admin_logout():
    try:
        session.clear()
        return redirect(url_for('admin_login'))
    except Exception as e:
        print(f"Error in admin_logout: {e}")
        return redirect(url_for('admin_login'))

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

@app.route('/admin/manage-jobs')
@admin_required
def admin_manage_jobs():
    try:
        return render_template('admin/manage_jobs.html')
    except Exception as e:
        print(f"Error in admin_manage_jobs: {e}")
        return f"Error: {str(e)}", 500

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
    """Vercel Python handler function."""
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    query_params = event.get('queryStringParameters', {})
    body = event.get('body', '')
    
    if body and headers.get('content-type') == 'application/json':
        try:
            body = json.loads(body)
        except:
            body = {}
    
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
    
    mock_request = MockRequest(http_method, path, headers, query_params, body)
    
    if http_method == 'POST' and isinstance(body, dict):
        for key, value in body.items():
            mock_request.form[key] = value
    
    from flask import globals as flask_globals
    flask_globals._request_ctx_stack.push(app.test_request_context(
        path=path,
        method=http_method,
        headers=headers,
        query_string='&'.join([f"{k}={v}" for k, v in (query_params or {}).items()])
    ))
    
    try:
        response = app.full_dispatch_request()
        
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
    # Initialize database (don't delete - keep existing data)
    init_db()
    # Only seed if empty
    seed_sample_data()
    # Run the app
    print("\n" + "="*50)
    print("Job Portal Started Successfully!")
    print("="*50)
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("Admin Login: admin@jobportal.com / admin123")
    print("="*50 + "\n")
    app.run(debug=True)
