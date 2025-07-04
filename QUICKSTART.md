# 🚀 Hackfinity Platform - Quick Start Guide

This is a condensed setup guide to get you running quickly. For complete documentation, see [README.md](README.md).

## ⚡ 5-Minute Setup

### 1. Prerequisites Check
```bash
# Check Python (need 3.8+)
python --version

# Check Node.js (need 16+)
node --version

# Check MongoDB (need 4.4+)
mongod --version
```

### 2. Clone & Setup
```bash
git clone <repository-url>
cd hackfinity-platform
```

### 3. Backend Setup (2 minutes)
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
echo "MONGO_URL=mongodb://localhost:27017
DB_NAME=hackfinity_platform
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
GEMINI_API_KEY=optional_ai_key" > .env

# Start backend
python server.py
```

### 4. Frontend Setup (2 minutes)
```bash
# New terminal
cd frontend
npm install
npm start
```

### 5. Access the Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎯 First Steps

### 1. Upload Sponsors
1. Go to "Sponsors" tab
2. Click "Upload Sponsors"
3. Upload a CSV with: Name, Email, Organization
4. Click "Send Emails" to send sponsor outreach

### 2. Upload Participants
1. Go to "Participants" tab
2. Click "Upload Participants" 
3. Upload a CSV with: Name, Email
4. Click "Send Certificates" to generate and send certificates

### 3. Schedule Emails
1. Go to "Email Scheduling" tab
2. Click "Schedule New Email"
3. Fill form and set date/time
4. Email will be sent automatically

### 4. Use Drag & Drop
1. Go to "Drag & Drop" tab
2. Drag files directly onto upload areas
3. Preview data before confirming
4. Files are processed automatically

## 📋 Sample Data

### sponsors.csv
```csv
Name,Email,Organization,Title
John Doe,john@techcorp.com,Tech Corp,CTO
Jane Smith,jane@startup.io,Startup Inc,Founder
Bob Wilson,bob@bigco.com,Big Company,Director
```

### participants.csv
```csv
Name,Email,Team,Project
Alice Johnson,alice@example.com,Team Alpha,AI Assistant
Charlie Brown,charlie@example.com,Team Beta,Blockchain App
Diana Prince,diana@example.com,Solo,FinTech Platform
```

## ⚙️ Essential Configuration

### Gmail Setup (Required for emails)
1. Enable 2-Factor Authentication
2. Go to Google Account → Security → App passwords
3. Generate app password for "Mail"
4. Use this password in `.env` file

### MongoDB Setup
```bash
# Option 1: Local MongoDB
mongod --dbpath ./data

# Option 2: Use MongoDB Atlas (cloud)
# Get connection string from atlas.mongodb.com
# Update MONGO_URL in .env
```

## 🔧 Common Issues

**Backend won't start**: Check Python version and virtual environment
**Frontend errors**: Run `npm install` again
**Email errors**: Check Gmail app password setup
**Database errors**: Ensure MongoDB is running

## 🎨 Key Features Overview

- **📧 Email Automation** - Send personalized sponsor emails
- **🏆 Certificate Generation** - Create and send participant certificates  
- **⏰ Email Scheduling** - Schedule emails for future delivery
- **📁 Drag & Drop Upload** - Enhanced file upload with validation
- **📊 Analytics Dashboard** - View comprehensive statistics
- **🎨 Template Management** - Customize email and certificate templates

## 📞 Need Help?

- **Issues**: Check the main [README.md](README.md) troubleshooting section
- **Features**: Explore the platform UI - it's intuitive!
- **API**: Visit http://localhost:8000/docs for API documentation

---

**🎉 You're ready to go! Start by uploading some sponsor data and sending your first automated emails.**
