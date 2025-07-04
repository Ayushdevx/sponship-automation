# 🚀 Deployment Guide - Hackfinity Platform

This guide covers deployment options for the Hackfinity Platform, from local development to production environments.

## 📋 Table of Contents

- [Quick Local Setup](#quick-local-setup)
- [Development Environment](#development-environment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Configuration](#environment-configuration)
- [Security Considerations](#security-considerations)
- [Monitoring & Maintenance](#monitoring--maintenance)

## 🏃‍♂️ Quick Local Setup

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- MongoDB 4.4+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/hackfinity-platform.git
cd hackfinity-platform
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configurations

python server.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🛠 Development Environment

### Backend Development
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Run tests
python test_backend.py
pytest tests/ -v

# Code formatting
black .
flake8 .
```

### Frontend Development
```bash
# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build

# Linting
npm run lint
npm run format
```

### Database Setup
```bash
# Start MongoDB locally
mongod --dbpath /path/to/your/db

# Or use MongoDB Atlas (cloud)
# Update MONGO_URL in .env with connection string
```

## 🌐 Production Deployment

### Server Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+ 
- **Storage**: 20GB+ SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+

### 1. Server Setup (Ubuntu)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3.9-dev -y

# Install Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Install Nginx
sudo apt install nginx -y

# Install PM2 for process management
sudo npm install -g pm2
```

### 2. Application Deployment
```bash
# Clone repository
cd /opt
sudo git clone https://github.com/yourusername/hackfinity-platform.git
sudo chown -R $USER:$USER hackfinity-platform
cd hackfinity-platform

# Backend setup
cd backend
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production environment file
cp .env.example .env
# Edit .env with production configurations

# Frontend setup
cd ../frontend
npm ci --only=production
npm run build
```

### 3. Process Management with PM2
```bash
# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'hackfinity-backend',
      script: 'venv/bin/uvicorn',
      args: 'server:app --host 0.0.0.0 --port 8000',
      cwd: '/opt/hackfinity-platform/backend',
      instances: 2,
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
};
EOF

# Start application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 4. Nginx Configuration
```nginx
# /etc/nginx/sites-available/hackfinity
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend
    location / {
        root /opt/hackfinity-platform/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Static files
    location /static/ {
        alias /opt/hackfinity-platform/frontend/build/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/hackfinity /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🐳 Docker Deployment

### 1. Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - DB_NAME=hackfinity_platform
    env_file:
      - ./backend/.env
    depends_on:
      - mongo
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  mongo:
    image: mongo:4.4
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=your_password
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  mongo_data:
```

### 2. Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### 4. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update application
git pull
docker-compose build
docker-compose up -d
```

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance Setup
```bash
# Launch EC2 instance (t3.medium or larger)
# Configure security groups (80, 443, 22, 8000)
# Connect to instance

# Follow production deployment steps above
```

#### 2. RDS for MongoDB Alternative
```bash
# Use Amazon DocumentDB (MongoDB compatible)
# Update MONGO_URL in .env
MONGO_URL=mongodb://username:password@cluster.region.docdb.amazonaws.com:27017/?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred
```

#### 3. S3 for File Storage
```python
# backend/config.py
import boto3

s3_client = boto3.client('s3',
    aws_access_key_id='your_access_key',
    aws_secret_access_key='your_secret_key',
    region_name='us-east-1'
)
```

### Google Cloud Platform

#### 1. App Engine Deployment
```yaml
# app.yaml (for backend)
runtime: python39

env_variables:
  MONGO_URL: "your_mongo_url"
  EMAIL_ADDRESS: "your_email"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

#### 2. Cloud Run Deployment
```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/hackfinity-backend

# Deploy to Cloud Run
gcloud run deploy hackfinity-backend \
    --image gcr.io/PROJECT_ID/hackfinity-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### Azure Deployment

#### 1. App Service Deployment
```bash
# Create resource group
az group create --name hackfinity-rg --location eastus

# Create app service plan
az appservice plan create --name hackfinity-plan --resource-group hackfinity-rg --sku B1 --is-linux

# Create web app
az webapp create --name hackfinity-app --resource-group hackfinity-rg --plan hackfinity-plan --runtime "PYTHON|3.9"
```

## ⚙️ Environment Configuration

### Production Environment Variables
```bash
# Security
DEBUG=False
SECRET_KEY=your-complex-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
MONGO_URL=mongodb://user:password@host:port/database
DB_NAME=hackfinity_production

# Email
EMAIL_ADDRESS=noreply@your-domain.com
EMAIL_PASSWORD=your-production-email-password

# CORS
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/hackfinity/app.log

# SSL
SSL_REDIRECT=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
```

### Frontend Environment
```bash
# frontend/.env.production
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
```

## 🔒 Security Considerations

### 1. Application Security
```python
# backend/security.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2. Database Security
```javascript
// MongoDB with authentication
use admin
db.createUser({
  user: "hackfinity_admin",
  pwd: "strong_password_here",
  roles: [ { role: "readWrite", db: "hackfinity_platform" } ]
})
```

### 3. File Upload Security
```python
# Scan uploaded files
import magic

def validate_file_type(file_content):
    file_type = magic.from_buffer(file_content, mime=True)
    allowed_types = ['text/csv', 'application/vnd.ms-excel']
    return file_type in allowed_types
```

### 4. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/upload")
@limiter.limit("5/minute")
async def upload_file(request: Request):
    # Upload logic
    pass
```

## 📊 Monitoring & Maintenance

### 1. Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": "connected" if db_connected else "disconnected"
    }
```

### 2. Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('/var/log/hackfinity/app.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 3. Database Backup
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --host localhost:27017 --db hackfinity_platform --out /backups/mongo_$DATE
tar -czf /backups/mongo_$DATE.tar.gz /backups/mongo_$DATE
rm -rf /backups/mongo_$DATE
find /backups -name "mongo_*.tar.gz" -mtime +30 -delete
```

### 4. Monitoring with PM2
```bash
# Install PM2 monitoring
pm2 install pm2-server-monit

# Set up monitoring dashboard
pm2 web

# Check application status
pm2 status
pm2 logs
pm2 monit
```

### 5. Performance Monitoring
```python
# Add to server.py
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🔄 Update Procedures

### 1. Application Updates
```bash
#!/bin/bash
# update.sh
cd /opt/hackfinity-platform

# Backup current version
cp -r . ../hackfinity-backup-$(date +%Y%m%d)

# Pull updates
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../frontend
npm ci --only=production
npm run build

# Restart services
pm2 restart all

# Run health check
curl -f http://localhost:8000/health
```

### 2. Database Migrations
```python
# migration script example
async def migrate_database():
    # Add new fields, update schemas, etc.
    await db.sponsors.update_many({}, {"$set": {"created_at": datetime.utcnow()}})
    await db.participants.create_index("email", unique=True)
```

## 🆘 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   ```bash
   # Check MongoDB status
   sudo systemctl status mongod
   
   # Check logs
   sudo tail -f /var/log/mongodb/mongod.log
   ```

2. **Email Sending Failed**
   ```bash
   # Check email configuration
   python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587)"
   ```

3. **High Memory Usage**
   ```bash
   # Monitor processes
   htop
   
   # Check PM2 processes
   pm2 status
   pm2 restart all
   ```

4. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew certificate
   sudo certbot renew
   ```

## 📞 Support

For deployment assistance:
- 📧 Email: devops@hackfinity.com
- 📖 Documentation: https://docs.hackfinity.com/deployment
- 💬 Discord: https://discord.gg/hackfinity

---

**Happy Deploying! 🚀**
