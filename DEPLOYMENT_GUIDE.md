# Job Portal - Vercel Deployment Guide

This guide will help you deploy your Flask Job Portal website on Vercel.

---

## Current Project Structure

```
job-portal/
├── api/                          # (Optional - can use backend/ folder)
│   └── app.py                    # Flask application with Vercel handler
├── backend/
│   ├── app.py                    # Main Flask application
│   └── database.db               # SQLite database
├── templates/                    # HTML templates
│   ├── index.html
│   ├── jobs.html
│   ├── companies.html
│   ├── login.html
│   ├── register.html
│   ├── apply.html
│   └── admin/
│       ├── login.html
│       ├── dashboard.html
│       ├── add_job.html
│       ├── manage_jobs.html
│       └── applications.html
├── static/                       # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── requirements.txt              # Python dependencies
├── vercel.json                   # Vercel configuration
└── pyproject.toml               # Project metadata
```

---

## Step 1: Update requirements.txt

Add all required dependencies for Vercel deployment:

```txt
Flask==3.0.0
Werkzeug==3.0.1
bcrypt==4.1.2
gunicorn==21.2.0
```

---

## Step 2: Update vercel.json

The current configuration is good, but let's ensure it's optimized:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/app.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.11",
        "installCommand": "pip install -r requirements.txt"
      }
    },
    {
      "src": "static/",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "backend/app.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
```

---

## Step 3: Database Handling for Vercel

Vercel serverless functions have a **read-only filesystem**. The database is already configured to use `/tmp` on Vercel:

```python
import os

if os.environ.get('VERCEL') == '1':
    DB_PATH = os.path.join('/tmp', 'database.db')
else:
    DB_PATH = os.path.join(BASE_DIR, 'backend', 'database.db')
```

**Important:** The database will be ephemeral on Vercel's free tier. For production:
- Use a cloud database (PostgreSQL, MySQL)
- Or accept that the database resets on each deployment

---

## Step 4: Deploy to Vercel

### Option A: Using Vercel CLI

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy the project:**
```bash
vercel
```

4. **Follow the prompts:**
```
- Set up and deploy? Yes
- Which scope? [your-username]
- Want to modify settings? No
```

5. **For production deployment:**
```bash
vercel --prod
```

### Option B: Using GitHub Integration

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/job-portal.git
git push -u origin main
```

2. Go to [Vercel Dashboard](https://vercel.com/dashboard)

3. Click "Add New..." → "Project"

4. Import your GitHub repository

5. Configure:
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

6. Click "Deploy"

---

## Step 5: Environment Variables

Set environment variables in Vercel Dashboard:

1. Go to your project → Settings → Environment Variables

2. Add these variables:
```
SECRET_KEY=your-secret-key-here
VERCEL=1
```

---

## Step 6: Test Your Deployment

After deployment, test:

- [ ] Homepage loads correctly
- [ ] Jobs page displays job listings
- [ ] Companies page shows companies
- [ ] User registration works
- [ ] User login works
- [ ] Job application form works
- [ ] Admin login at /admin/login
- [ ] Admin dashboard shows statistics
- [ ] Add/Edit/Delete jobs works

---

## Default Credentials

**Admin Panel:**
- URL: `https://your-project.vercel.app/admin/login`
- Email: `admin@jobportal.com`
- Password: `admin123`

---

## Troubleshooting Common Errors

### FUNCTION_INVOCATION_FAILED

**Cause:** Python runtime error or missing dependencies

**Solution:**
1. Check requirements.txt has all dependencies
2. Ensure vercel.json is properly configured
3. Check Vercel function logs in Dashboard

### Static Files Not Loading

**Cause:** Incorrect static file paths

**Solution:** In HTML files, use:
```html
<link rel="stylesheet" href="/static/css/style.css">
<script src="/static/js/script.js"></script>
```

### Database Errors

**Cause:** Database file not found or read-only

**Solution:**
1. Ensure database is in the correct location
2. Use cloud database for production
3. Check `/tmp` path configuration

### 404 Errors on Routes

**Cause:** Incorrect route configuration

**Solution:** Update vercel.json routes:
```json
{
  "src": "/(.*)",
  "dest": "backend/app.py"
}
```

---

## Alternative: Using API Folder Structure

If you prefer the `api/` folder structure:

1. Create `api/` folder
2. Move `backend/app.py` to `api/app.py`
3. Update vercel.json:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/app.py",
      "use": "@vercel/python"
    },
    {
      "src": "static/",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "api/app.py"
    }
  ]
}
```

---

## Production Recommendations

1. **Use a cloud database** (PostgreSQL, MySQL) instead of SQLite
2. **Set a strong SECRET_KEY** in environment variables
3. **Enable HTTPS** (automatic on Vercel)
4. **Configure custom domain** if needed
5. **Set up CI/CD** with GitHub integration

---

## Support

- Vercel Documentation: https://vercel.com/docs
- Flask Documentation: https://flask.palletsprojects.com/
- Vercel Python Runtime: https://vercel.com/docs/serverless-functions/runtimes/python

---

**Happy Deployment! 🚀**

