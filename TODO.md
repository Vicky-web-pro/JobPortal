# Job Portal Project - TODO List

## Project Overview
Build a complete Online Job Portal Website with HTML, CSS, JS frontend and Python Flask backend with SQLite database.

## Phase 1: Project Structure Setup
- [x] Create main project directory structure
- [x] Create backend/ folder with app.py
- [x] Create templates/ folder for HTML files
- [x] Create templates/admin/ folder for admin pages
- [x] Create static/css/ folder for styles
- [x] Create static/js/ folder for scripts
- [x] Create static/images/ folder for images

## Phase 2: Backend Development
- [x] Create Flask app (app.py) with configuration
- [x] Set up SQLite database connection
- [x] Create database tables (users, companies, jobs, applications)
- [x] Implement user authentication (register, login, logout)
- [x] Create API endpoints for jobs (/api/jobs, /api/add-job, etc.)
- [x] Create API endpoints for companies
- [x] Create API endpoints for applications
- [x] Create admin routes for dashboard
- [x] Add duplicate sample data for companies and jobs

## Phase 3: Frontend - Main Pages
- [x] Create index.html (Home page with hero, search, featured companies)
- [x] Create jobs.html (Job listings page)
- [x] Create companies.html (Companies listing page)
- [x] Create login.html (User login page)
- [x] Create register.html (User registration page)
- [x] Create apply.html (Job application form)

## Phase 4: Frontend - Admin Pages
- [x] Create admin/dashboard.html (Admin dashboard)
- [x] Create admin/add_job.html (Add new job)
- [x] Create admin/manage_jobs.html (Edit/Delete jobs)
- [x] Create admin/applications.html (View applications)

## Phase 5: CSS Styling
- [x] Create style.css (Main styles with modern UI/UX)
- [x] Create admin.css (Admin panel styles)
- [x] Include responsive design
- [x] Add hover animations
- [x] Implement gradient backgrounds

## Phase 6: JavaScript Functionality
- [x] Create script.js (Main JS for navigation, forms)
- [x] Create jobs.js (Dynamic job loading with fetch API)
- [x] Create admin.js (Admin functionality)

## Phase 7: Testing & Verification
- [x] Install Flask and dependencies
- [x] Run the application
- [x] Test all pages load correctly
- [x] Test job listing loads dynamically
- [x] Test user registration and login
- [x] Test admin functionality

## Technology Stack
- Frontend: HTML5, CSS3, JavaScript
- Backend: Python Flask
- Database: SQLite

## Database Tables
1. users (id, name, email, password)
2. companies (id, name, industry, location, email, description, logo, image)
3. jobs (id, title, company, department, job_role, location, salary, job_type, description, company_email)
4. applications (id, name, email, mobile, department, job_role, job_id, resume, message)

## Sample Data Requirements
- 6+ companies (Google, Amazon, Microsoft, TCS, Infosys, Wipro)
- 10+ jobs across different roles (Software Developer, Python Developer, Web Developer, Data Analyst, UI/UX Designer)

