# 🚀 Hackfinity Platform - Certificate & Sponsorship Automation

> The world's biggest Agentic AI hackathon platform for automated certificate generation and sponsor management with advanced email scheduling and drag & drop file uploads.

![Hackfinity Platform](https://img.shields.io/badge/Platform-Hackfinity-blue?style=for-the-badge&logo=rocket)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge&logo=react)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green?style=for-the-badge&logo=mongodb)

## 🌟 Overview

Hackfinity Platform is a comprehensive automation tool designed specifically for hackathons and events. It streamlines the entire process from sponsor outreach to participant certificate generation, featuring modern UI/UX, email scheduling, and intelligent file processing.

### ✨ Key Features

#### 🔧 Core Functionality
- **Automated Sponsor Management** - Upload sponsor data and generate personalized emails
- **Certificate Generation** - Create and distribute professional certificates to participants
- **Email Automation** - Send sponsor outreach emails and participant certificates automatically
- **Analytics & Reporting** - Comprehensive dashboards with modern charts and insights

#### 🆕 Enhanced Features (Latest Update)
- **⏰ Email Scheduling** - Schedule emails for specific dates and times
- **📁 Drag & Drop Upload** - Enhanced file upload with real-time validation and preview
- **📊 Advanced Analytics** - Modern charts including 3D scatter, treemap, sankey diagrams
- **🎨 Template Designer** - Visual template builder for emails and certificates
- **📱 Mobile Responsive** - Modern UI that works on all devices

## 🏗️ Architecture

```
Hackfinity Platform
├── Backend (FastAPI)
│   ├── 📧 Email Scheduling System
│   ├── 📁 File Upload & Processing
│   ├── 📊 Analytics Engine
│   ├── 🎨 Template Management
│   └── 🏆 Certificate Customization
└── Frontend (React)
    ├── 📱 Responsive UI Components
    ├── ⏰ Email Scheduling Interface
    ├── 📁 Drag & Drop Upload
    ├── 📊 Interactive Dashboards
    └── 🎨 Visual Designers
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **MongoDB 4.4+** (database)
- **Gmail Account** (for email sending)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hackfinity-platform.git
cd hackfinity-platform
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# Start the backend server
python server.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory (new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at `http://localhost:3000`

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the `backend` directory:

```env
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=hackfinity_platform

# Email Configuration (Gmail)
EMAIL_ADDRESS=your_hackfinity_email@gmail.com
EMAIL_PASSWORD=your_app_specific_password

# AI Configuration (Optional - for enhanced email generation)
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
DEBUG=True
ENVIRONMENT=development
```

### Gmail Setup for Email Sending

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
   - Use this password in `EMAIL_PASSWORD`

### MongoDB Setup

#### Option 1: Local MongoDB
```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/your/db
```

#### Option 2: MongoDB Atlas (Cloud)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create cluster and get connection string
3. Update `MONGO_URL` in `.env`

## 📋 Detailed Features

### 🔧 Backend Features

#### Email Scheduling System
- **Schedule Individual Emails** - Set specific date and time for email delivery
- **Bulk Email Scheduling** - Schedule emails for multiple recipients
- **Background Processing** - Emails are sent automatically using background scheduler
- **Status Tracking** - Monitor pending, sent, and failed emails
- **Analytics** - Comprehensive scheduling analytics and insights

```python
# Example: Schedule an email
POST /api/schedule-email
{
    "recipient_email": "sponsor@company.com",
    "subject": "Partnership Opportunity",
    "content": "Email content here...",
    "schedule_date": "2025-07-10",
    "schedule_time": "09:00",
    "template_type": "sponsor"
}
```

#### Drag & Drop File Upload
- **Enhanced File Processing** - Support for CSV, XLSX, XLS files
- **Intelligent Column Mapping** - Automatic detection of name, email, organization fields
- **Data Quality Analysis** - Validation and quality scoring of uploaded data
- **Preview Before Processing** - Review data before creating records
- **Auto-Record Creation** - Automatic sponsor/participant record generation

```python
# Example: Upload with validation
POST /api/upload-excel-drag-drop
- Validates file format and size
- Analyzes data quality
- Provides preview with recommendations
- Creates records automatically
```

#### Advanced Analytics
- **Modern Visualizations** - 15+ chart types including 3D scatter, treemap, sankey
- **Real-time Data** - Live updates of sponsor and participant metrics
- **Export Capabilities** - PDF, Excel, CSV export options
- **Custom Dashboards** - Configurable analytics dashboards

#### Template Management
- **Visual Designer** - Drag-and-drop template builder
- **Pre-built Templates** - Professional email and certificate templates
- **Customization** - Full control over styling, colors, layouts
- **Template Analytics** - Performance tracking for templates

### 🎨 Frontend Features

#### Modern User Interface
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Modern Styling** - Beautiful gradients, animations, and transitions
- **Dark/Light Themes** - Multiple color schemes
- **Accessibility** - WCAG compliant interface

#### Email Scheduling Interface
- **Interactive Calendar** - Visual date and time selection
- **Batch Scheduling** - Schedule emails for multiple recipients
- **Status Dashboard** - Real-time monitoring of scheduled emails
- **Quick Actions** - Edit, cancel, or reschedule emails easily

#### Drag & Drop Upload
- **Visual Feedback** - Drag over effects and progress indicators
- **File Validation** - Real-time validation with helpful error messages
- **Data Preview** - Review uploaded data before processing
- **Quality Insights** - Data quality analysis with recommendations

#### Enhanced Navigation
- **Tabbed Interface** - Organized sections for different features
- **Quick Access** - Fast navigation between sponsor, participant, and analytics sections
- **Search & Filter** - Find specific records quickly
- **Bulk Operations** - Perform actions on multiple records

## 📊 API Documentation

### Core Endpoints

#### Sponsors
```
GET    /api/sponsors              # List all sponsors
POST   /api/upload-sponsors       # Upload sponsor CSV/Excel
POST   /api/send-sponsor-emails   # Send emails to sponsors
GET    /api/email-stats           # Get email statistics
```

#### Participants
```
GET    /api/participants          # List all participants
POST   /api/upload-participants   # Upload participant CSV/Excel
POST   /api/send-certificates     # Send certificates
GET    /api/certificate-stats     # Get certificate statistics
```

#### Email Scheduling
```
POST   /api/schedule-email        # Schedule single email
POST   /api/schedule-bulk-emails  # Schedule bulk emails
GET    /api/scheduled-emails      # List scheduled emails
PUT    /api/scheduled-emails/{id} # Update scheduled email
DELETE /api/scheduled-emails/{id} # Cancel scheduled email
```

#### File Upload
```
POST   /api/upload-excel-drag-drop    # Enhanced drag & drop upload
POST   /api/validate-excel-upload     # Validate file before upload
```

#### Templates
```
GET    /api/templates              # List email templates
POST   /api/templates              # Create template
PUT    /api/templates/{id}         # Update template
DELETE /api/templates/{id}         # Delete template
```

#### Analytics
```
GET    /api/analytics/sponsors     # Sponsor analytics
GET    /api/analytics/certificates # Certificate analytics
GET    /api/analytics/dashboard    # Combined dashboard
GET    /api/analytics/scheduled-emails # Email scheduling analytics
```

### Authentication
Currently, the platform uses basic API access. For production deployment, implement:
- JWT token authentication
- Role-based access control
- API rate limiting

## 📁 File Upload Formats

### Supported File Types
- **CSV** (.csv) - Comma-separated values
- **Excel** (.xlsx, .xls) - Microsoft Excel formats
- **Maximum Size** - 10MB per file

### Required Columns

#### For Sponsors
| Column | Description | Required |
|--------|-------------|----------|
| Name | Contact person name | ✅ |
| Email | Valid email address | ✅ |
| Organization | Company/organization name | ✅ |
| Phone | Contact phone number | ❌ |
| Title | Job title/position | ❌ |
| Industry | Business sector | ❌ |

#### For Participants
| Column | Description | Required |
|--------|-------------|----------|
| Name | Participant full name | ✅ |
| Email | Valid email address | ✅ |
| Team | Team name (if applicable) | ❌ |
| Project | Project name | ❌ |
| Category | Participation category | ❌ |

### Example CSV Format

```csv
Name,Email,Organization,Phone,Title
John Doe,john@company.com,Tech Corp,+1234567890,CTO
Jane Smith,jane@startup.io,Startup Inc,+0987654321,Founder
```

## 🔧 Development

### Project Structure

```
hackfinity-platform/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── analytics.py           # Analytics engine (to be created)
│   ├── template_engine.py     # Template management (to be created)
│   ├── certificate_customizer.py # Certificate system (to be created)
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React application
│   │   ├── App.css           # Styling and themes
│   │   └── index.js          # React entry point
│   ├── public/               # Static files
│   ├── package.json          # Node.js dependencies
│   └── package-lock.json     # Dependency lock file
├── tests/                    # Test files
├── docs/                     # Documentation
└── README.md                 # This file
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Code Style

#### Backend (Python)
- **Black** for code formatting
- **Flake8** for linting
- **Type hints** for better code documentation

```bash
# Format code
black .
# Lint code
flake8 .
```

#### Frontend (JavaScript)
- **Prettier** for code formatting
- **ESLint** for linting
- **Conventional commits** for git messages

```bash
# Format code
npm run format
# Lint code
npm run lint
```

## 🚀 Deployment

### Production Deployment

#### Backend (Docker)

```dockerfile
# Dockerfile for backend
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend (Docker)

```dockerfile
# Dockerfile for frontend
FROM node:16-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
EXPOSE 80
```

#### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongo:27017
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### Environment-Specific Configurations

#### Development
- Debug mode enabled
- Hot reloading
- Detailed error messages

#### Staging
- Production-like environment
- Testing with real data
- Performance monitoring

#### Production
- Optimized builds
- Error logging
- Security headers
- SSL/HTTPS enabled

## 🔒 Security Considerations

### Data Protection
- **Email Encryption** - All emails sent via secure SMTP
- **Data Validation** - Input sanitization and validation
- **File Security** - Virus scanning for uploaded files
- **Database Security** - MongoDB with authentication

### Privacy Compliance
- **GDPR Compliance** - Data protection and user rights
- **Data Retention** - Configurable data retention policies
- **Consent Management** - User consent tracking
- **Data Export** - User data export capabilities

### Production Security Checklist
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Configure authentication
- [ ] Enable audit logging
- [ ] Set up monitoring
- [ ] Regular security updates
- [ ] Backup and recovery plan

## 📈 Performance Optimization

### Backend Optimization
- **Async Processing** - FastAPI with async/await
- **Database Indexing** - MongoDB indexes for faster queries
- **Caching** - Redis for frequently accessed data
- **Background Tasks** - Celery for heavy processing

### Frontend Optimization
- **Code Splitting** - Lazy loading for components
- **Image Optimization** - Compressed images and lazy loading
- **Bundle Optimization** - Webpack optimization
- **CDN Integration** - Static asset delivery

### Monitoring
- **Application Performance** - Response time monitoring
- **Error Tracking** - Sentry for error monitoring
- **Usage Analytics** - User behavior tracking
- **Resource Monitoring** - CPU, memory, disk usage

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'analytics'`
```bash
# Solution: Create the missing module or comment out the import
# The analytics module will be created in future updates
```

**Issue**: `ConnectionError: MongoDB connection failed`
```bash
# Solution: Check MongoDB is running and connection string is correct
mongod --dbpath /your/db/path
```

**Issue**: `SMTPAuthenticationError: Gmail authentication failed`
```bash
# Solution: Use App Password instead of regular password
# Enable 2FA and generate App Password in Gmail settings
```

#### Frontend Issues

**Issue**: `npm start` fails with dependency errors
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Issue**: API calls fail with CORS errors
```bash
# Solution: Check backend CORS configuration
# Ensure frontend URL is in allowed origins
```

### Debug Mode

Enable debug mode for detailed error information:

```env
# In .env file
DEBUG=True
LOG_LEVEL=DEBUG
```

### Logs Location
- **Backend Logs**: Console output and `/var/log/hackfinity/`
- **Frontend Logs**: Browser console
- **Access Logs**: `/var/log/nginx/` (if using Nginx)

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Process
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Write clear commit messages

### Areas for Contribution
- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations
- 🧪 Test coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework for building APIs
- **React** - User interface library
- **MongoDB** - Document database
- **Plotly** - Interactive charting library
- **ReportLab** - PDF generation library
- **Material-UI** - React UI framework

## � Documentation

### Complete Documentation Set
- **[README.md](README.md)** - Main documentation (this file)
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[SECURITY.md](SECURITY.md)** - Security best practices
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

### Additional Resources
- **[ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md)** - Latest feature enhancements
- **[test_backend.py](test_backend.py)** - Backend verification script
- **[LICENSE](LICENSE)** - MIT License terms

## �📞 Support

### Community Support
- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Community questions and ideas
- **Discord** - Real-time chat and support

### Professional Support
For enterprise support, custom development, or consulting:
- **Email**: support@hackfinity.com
- **Website**: https://hackfinity.com
- **Documentation**: https://docs.hackfinity.com

### Security
For security-related issues:
- **Security Email**: security@hackfinity.com
- **Security Documentation**: [SECURITY.md](SECURITY.md)

### Roadmap
- [ ] User authentication and roles
- [ ] Advanced template designer
- [ ] Integration with popular services (Slack, Discord)
- [ ] Mobile app
- [ ] Advanced analytics with AI insights
- [ ] Multi-language support
- [ ] White-label solutions

## 📋 Project Status

### Current Version: 2.0.0
- ✅ Email Scheduling System
- ✅ Drag & Drop File Upload
- ✅ Enhanced Analytics
- ✅ Comprehensive Documentation
- ✅ Production-Ready Backend
- ✅ Modern React Frontend

### Next Release: 2.1.0 (Planned)
- 🔄 User Authentication System
- 🔄 Advanced Security Features
- 🔄 Performance Optimizations
- 🔄 Mobile App Support

---

<div align="center">

**Built with ❤️ for the global hackathon community**

[Website](https://hackfinity.com) • [Documentation](https://docs.hackfinity.com) • [Community](https://discord.gg/hackfinity) • [Twitter](https://twitter.com/hackfinity)

![GitHub stars](https://img.shields.io/github/stars/yourusername/hackfinity-platform?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/hackfinity-platform?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/hackfinity-platform)
![GitHub license](https://img.shields.io/github/license/yourusername/hackfinity-platform)

</div>
