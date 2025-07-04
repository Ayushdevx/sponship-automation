# 🔒 Security Guide - Hackfinity Platform

This document outlines security best practices, configurations, and considerations for deploying and maintaining the Hackfinity Platform securely.

## 🛡️ Security Overview

The Hackfinity Platform handles sensitive data including:
- Email addresses and contact information
- Sponsor and participant personal data
- Authentication credentials
- File uploads and document processing

## 🔐 Authentication & Authorization

### Current State
The platform currently operates without authentication for development purposes. **This must be changed for production use.**

### Production Authentication Implementation

#### 1. JWT Token Authentication
```python
# backend/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### 2. Role-Based Access Control (RBAC)
```python
# User roles
class UserRole(str, Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    VIEWER = "viewer"

# Permission decorator
def require_role(required_role: UserRole):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if current_user.role != required_role:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.post("/api/send-sponsor-emails")
@require_role(UserRole.ORGANIZER)
async def send_sponsor_emails():
    # Implementation
    pass
```

## 📧 Email Security

### 1. Gmail App Passwords
**Never use your regular Gmail password in production.**

```bash
# Set up App Password
1. Enable 2-Factor Authentication on Gmail
2. Go to Google Account Settings > Security > 2-Step Verification
3. Generate App Password for "Mail"
4. Use this 16-character password in EMAIL_PASSWORD
```

### 2. Email Content Sanitization
```python
import html
import re
from typing import List

def sanitize_email_content(content: str) -> str:
    """Sanitize email content to prevent injection attacks."""
    # Remove script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove potentially dangerous attributes
    content = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
    
    # Escape HTML entities
    content = html.escape(content)
    
    return content

def validate_email_addresses(emails: List[str]) -> List[str]:
    """Validate email addresses to prevent header injection."""
    valid_emails = []
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    for email in emails:
        if email_pattern.match(email) and '\n' not in email and '\r' not in email:
            valid_emails.append(email)
    
    return valid_emails
```

### 3. Rate Limiting for Email Sending
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/send-sponsor-emails")
@limiter.limit("10/hour")  # Limit to 10 email sends per hour per IP
async def send_sponsor_emails(request: Request):
    # Implementation
    pass
```

## 📁 File Upload Security

### 1. File Type Validation
```python
import magic
from pathlib import Path

ALLOWED_MIME_TYPES = {
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

ALLOWED_EXTENSIONS = {'.csv', '.xls', '.xlsx'}

def validate_file_upload(file_content: bytes, filename: str) -> bool:
    """Validate uploaded file for security."""
    
    # Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check MIME type using python-magic
    try:
        mime_type = magic.from_buffer(file_content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES:
            return False
    except Exception:
        return False
    
    return True
```

### 2. File Size Limits
```python
from fastapi import HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file_size(file: UploadFile):
    """Validate file size."""
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE/1024/1024}MB"
        )
    
    return content
```

### 3. Virus Scanning (Production)
```python
import subprocess

def scan_file_for_viruses(file_path: str) -> bool:
    """Scan file for viruses using ClamAV."""
    try:
        result = subprocess.run(
            ['clamscan', '--quiet', file_path], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # If ClamAV is not available, log warning but allow file
        logging.warning("Virus scanning not available")
        return True
```

## 🗄️ Database Security

### 1. MongoDB Authentication
```javascript
// MongoDB setup with authentication
use admin
db.createUser({
  user: "hackfinity_admin",
  pwd: "strong_random_password_here",
  roles: [
    { role: "readWrite", db: "hackfinity_platform" },
    { role: "dbAdmin", db: "hackfinity_platform" }
  ]
})

// Connection string with authentication
MONGO_URL=mongodb://hackfinity_admin:password@localhost:27017/hackfinity_platform?authSource=admin
```

### 2. Database Connection Security
```python
from motor.motor_asyncio import AsyncIOMotorClient
import ssl

# Secure MongoDB connection
def get_database():
    client = AsyncIOMotorClient(
        MONGO_URL,
        tls=True,
        tlsAllowInvalidCertificates=False,
        serverSelectionTimeoutMS=5000,
        maxPoolSize=50
    )
    return client[DB_NAME]
```

### 3. Data Encryption at Rest
```bash
# MongoDB with encryption at rest
mongod --enableEncryption --encryptionKeyFile /path/to/keyfile
```

## 🌐 Web Application Security

### 1. HTTPS Configuration
```python
# Force HTTPS in production
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 2. Security Headers
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response
```

### 3. CORS Configuration
```python
# Strict CORS configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 4. Input Validation
```python
from pydantic import BaseModel, validator, EmailStr
import re

class SponsorModel(BaseModel):
    name: str
    email: EmailStr
    organization: str
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 100:
            raise ValueError('Name must be between 2 and 100 characters')
        if not re.match(r'^[a-zA-Z\s\-\.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
    
    @validator('organization')
    def validate_organization(cls, v):
        if len(v) < 2 or len(v) > 200:
            raise ValueError('Organization name must be between 2 and 200 characters')
        return v.strip()
```

## 🔑 Secrets Management

### 1. Environment Variables
```bash
# Use strong, unique values
SECRET_KEY=generate_strong_random_string_here_32_chars_min
EMAIL_PASSWORD=gmail_app_password_16_chars
MONGO_PASSWORD=strong_database_password

# Never commit .env files to version control
echo ".env" >> .gitignore
```

### 2. Production Secrets Management
```bash
# Using Azure Key Vault
az keyvault secret set --vault-name "hackfinity-vault" --name "mongo-password" --value "strong_password"

# Using AWS Secrets Manager
aws secretsmanager create-secret --name "hackfinity/mongo-password" --secret-string "strong_password"

# Using Google Secret Manager
gcloud secrets create mongo-password --data-file=password.txt
```

### 3. Key Rotation
```python
# Implement key rotation for production
import schedule
import time

def rotate_api_keys():
    """Rotate API keys periodically."""
    # Implementation for key rotation
    pass

# Schedule key rotation every 90 days
schedule.every(90).days.do(rotate_api_keys)
```

## 📊 Logging & Monitoring

### 1. Security Logging
```python
import logging
from datetime import datetime

# Configure security logging
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

def log_security_event(event_type: str, details: dict, request: Request):
    """Log security-related events."""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent'),
        'details': details
    }
    security_logger.info(f"SECURITY_EVENT: {log_entry}")

# Usage examples
@app.post("/api/login")
async def login(request: Request, credentials: UserCredentials):
    if not authenticate_user(credentials):
        log_security_event('FAILED_LOGIN', {'email': credentials.email}, request)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    log_security_event('SUCCESSFUL_LOGIN', {'email': credentials.email}, request)
    return create_access_token({'email': credentials.email})
```

### 2. Intrusion Detection
```python
from collections import defaultdict
from datetime import datetime, timedelta

# Simple rate limiting and intrusion detection
failed_attempts = defaultdict(list)

def check_failed_attempts(ip_address: str) -> bool:
    """Check if IP has too many failed attempts."""
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=15)
    
    # Remove old attempts
    failed_attempts[ip_address] = [
        attempt for attempt in failed_attempts[ip_address] 
        if attempt > cutoff
    ]
    
    # Check if too many recent failures
    if len(failed_attempts[ip_address]) >= 5:
        return False
    
    return True

def record_failed_attempt(ip_address: str):
    """Record a failed login attempt."""
    failed_attempts[ip_address].append(datetime.utcnow())
```

## 🚨 Incident Response

### 1. Security Incident Checklist
```markdown
## Security Incident Response

### Immediate Actions (0-1 hour)
- [ ] Identify and contain the security issue
- [ ] Document the incident details
- [ ] Notify the security team
- [ ] Preserve evidence and logs

### Short-term Actions (1-24 hours)
- [ ] Assess the scope and impact
- [ ] Implement temporary fixes
- [ ] Reset affected passwords/keys
- [ ] Monitor for continued threats

### Long-term Actions (1-7 days)
- [ ] Conduct thorough investigation
- [ ] Implement permanent fixes
- [ ] Update security procedures
- [ ] Notify affected users if required

### Follow-up (1-4 weeks)
- [ ] Post-incident review
- [ ] Update security documentation
- [ ] Improve monitoring and detection
- [ ] Security awareness training
```

### 2. Emergency Contacts
```python
# Emergency response configuration
SECURITY_CONTACTS = {
    'security_team': 'security@hackfinity.com',
    'technical_lead': 'tech-lead@hackfinity.com',
    'compliance_officer': 'compliance@hackfinity.com'
}

def notify_security_incident(severity: str, description: str):
    """Notify security team of incidents."""
    subject = f"SECURITY INCIDENT - {severity}: {description}"
    # Send notification emails
    pass
```

## 🔍 Security Auditing

### 1. Regular Security Audits
```bash
#!/bin/bash
# security_audit.sh

echo "Running security audit..."

# Check for common vulnerabilities
bandit -r backend/

# Check dependencies for known vulnerabilities
safety check

# Check for secrets in code
truffleHog --regex --entropy=False .

# Network security scan
nmap -sS -O localhost

echo "Security audit complete. Review results."
```

### 2. Automated Security Testing
```python
# tests/test_security.py
import pytest
from fastapi.testclient import TestClient

def test_sql_injection_protection():
    """Test SQL injection protection."""
    malicious_input = "'; DROP TABLE sponsors; --"
    response = client.post("/api/sponsors", json={"name": malicious_input})
    assert response.status_code != 500  # Should not crash

def test_xss_protection():
    """Test XSS protection."""
    xss_input = "<script>alert('xss')</script>"
    response = client.post("/api/sponsors", json={"name": xss_input})
    # Verify XSS is properly escaped

def test_file_upload_security():
    """Test file upload security."""
    # Test with malicious file types
    malicious_files = ["test.exe", "test.php", "test.js"]
    for filename in malicious_files:
        response = client.post("/api/upload", files={"file": (filename, b"content")})
        assert response.status_code == 400  # Should reject
```

## 📋 Security Compliance

### 1. GDPR Compliance
```python
# Data protection and user rights
class DataProtectionMixin:
    async def export_user_data(self, email: str) -> dict:
        """Export all user data for GDPR compliance."""
        user_data = {}
        user_data['sponsors'] = await db.sponsors.find({'email': email}).to_list(None)
        user_data['participants'] = await db.participants.find({'email': email}).to_list(None)
        return user_data
    
    async def delete_user_data(self, email: str):
        """Delete all user data for GDPR compliance."""
        await db.sponsors.delete_many({'email': email})
        await db.participants.delete_many({'email': email})
        # Log deletion for audit trail
```

### 2. Data Retention Policies
```python
from datetime import datetime, timedelta

async def cleanup_old_data():
    """Clean up old data according to retention policy."""
    cutoff_date = datetime.utcnow() - timedelta(days=365)  # 1 year retention
    
    # Delete old email logs
    await db.email_logs.delete_many({'sent_date': {'$lt': cutoff_date}})
    
    # Archive old participant data
    old_participants = await db.participants.find({'created_at': {'$lt': cutoff_date}}).to_list(None)
    if old_participants:
        await db.archived_participants.insert_many(old_participants)
        await db.participants.delete_many({'created_at': {'$lt': cutoff_date}})
```

## 🔒 Production Security Checklist

### Pre-Deployment
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure strong authentication
- [ ] Set up proper CORS policies
- [ ] Implement rate limiting
- [ ] Configure security headers
- [ ] Set up proper logging
- [ ] Scan for vulnerabilities
- [ ] Review environment variables

### Post-Deployment
- [ ] Monitor security logs
- [ ] Set up intrusion detection
- [ ] Regular security audits
- [ ] Backup and recovery testing
- [ ] Incident response procedures
- [ ] Security awareness training
- [ ] Regular penetration testing
- [ ] Compliance audits

### Ongoing Maintenance
- [ ] Regular security updates
- [ ] Dependency vulnerability scanning
- [ ] Log analysis and monitoring
- [ ] Access control reviews
- [ ] Backup verification
- [ ] Security policy updates
- [ ] Staff security training
- [ ] Third-party security assessments

## 📞 Security Support

For security-related questions or to report vulnerabilities:

- **Security Email**: security@hackfinity.com
- **Bug Bounty**: [HackerOne Program](https://hackerone.com/hackfinity)
- **Security Documentation**: https://docs.hackfinity.com/security
- **Emergency Contact**: +1-XXX-XXX-XXXX (24/7 security hotline)

---

**Remember: Security is an ongoing process, not a one-time setup. Regular reviews and updates are essential for maintaining a secure platform.** 🔐
