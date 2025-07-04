# 📚 Hackfinity Platform API Documentation

This document provides comprehensive API documentation for the Hackfinity Platform backend.

## 🔗 Base URL

```
Development: http://localhost:8000
Production: https://api.hackfinity.com
```

## 📊 API Overview

The Hackfinity Platform API is built with **FastAPI** and provides endpoints for:
- Sponsor management and email automation
- Participant management and certificate generation
- Email scheduling and automation
- File upload and processing
- Analytics and reporting
- Template management

## 🔐 Authentication

Currently, the API uses basic access without authentication. For production deployment, implement JWT token authentication.

## 📋 Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {...},
  "message": "Success message",
  "timestamp": "2025-07-04T12:00:00Z"
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error description",
  "detail": "Detailed error message",
  "timestamp": "2025-07-04T12:00:00Z"
}
```

## 🏷️ API Endpoints

### Core Endpoints

#### Root
```
GET /api/
```
Returns API status and basic information.

**Response:**
```json
{
  "message": "Hackfinity Communication Platform API",
  "version": "1.0.0",
  "status": "running"
}
```

---

## 💼 Sponsor Management

### List Sponsors
```
GET /api/sponsors
```
Get all sponsors with their email status.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@company.com",
    "organization": "Tech Corp",
    "email_status": "sent",
    "timestamp": "2025-07-04T12:00:00Z",
    "additional_info": {...}
  }
]
```

### Upload Sponsors
```
POST /api/upload-sponsors
```
Upload sponsor CSV/Excel file and generate email content.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV/Excel file)

**Response:**
```json
{
  "sponsors": [...],
  "total_count": 25,
  "preview_email": "<html>...</html>"
}
```

### Send Sponsor Emails
```
POST /api/send-sponsor-emails
```
Send generated emails to all sponsors in background.

**Response:**
```json
{
  "message": "Sending emails to 25 sponsors",
  "count": 25
}
```

### Email Statistics
```
GET /api/email-stats
```
Get email sending statistics.

**Response:**
```json
{
  "total": 25,
  "sent": 20,
  "failed": 2,
  "pending": 3
}
```

---

## 👥 Participant Management

### List Participants
```
GET /api/participants
```
Get all participants with their certificate status.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "certificate_generated": true,
    "certificate_sent": true,
    "timestamp": "2025-07-04T12:00:00Z"
  }
]
```

### Upload Participants
```
POST /api/upload-participants
```
Upload participant CSV/Excel file and generate certificates.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV/Excel file)

**Response:**
```json
{
  "participants": [...],
  "total_count": 100,
  "preview_certificate": "base64_encoded_pdf"
}
```

### Send Certificates
```
POST /api/send-certificates
```
Send certificates to all participants in background.

**Response:**
```json
{
  "message": "Sending certificates to 100 participants",
  "count": 100
}
```

### Certificate Statistics
```
GET /api/certificate-stats
```
Get certificate generation and sending statistics.

**Response:**
```json
{
  "total": 100,
  "sent": 85,
  "failed": 5,
  "pending": 10
}
```

---

## ⏰ Email Scheduling

### Schedule Email
```
POST /api/schedule-email
```
Schedule an email to be sent at a specific date and time.

**Request:**
```json
{
  "recipient_email": "sponsor@company.com",
  "subject": "Partnership Opportunity",
  "content": "<html>Email content...</html>",
  "schedule_date": "2025-07-10",
  "schedule_time": "09:00",
  "template_type": "sponsor",
  "attachments": ["file1.pdf"]
}
```

**Response:**
```json
{
  "message": "Email scheduled successfully",
  "email_id": "uuid",
  "scheduled_for": "2025-07-10 09:00"
}
```

### Schedule Bulk Emails
```
POST /api/schedule-bulk-emails
```
Schedule emails for multiple recipients.

**Request:**
```json
{
  "emails": ["email1@example.com", "email2@example.com"],
  "subject": "Bulk Email Subject",
  "content": "<html>Email content...</html>",
  "schedule_date": "2025-07-10",
  "schedule_time": "09:00",
  "template_type": "sponsor"
}
```

**Response:**
```json
{
  "message": "Scheduled 2 emails successfully",
  "scheduled_email_ids": ["uuid1", "uuid2"],
  "scheduled_for": "2025-07-10 09:00"
}
```

### List Scheduled Emails
```
GET /api/scheduled-emails
```
Get all scheduled emails.

**Response:**
```json
[
  {
    "id": "uuid",
    "recipient_email": "sponsor@company.com",
    "subject": "Partnership Opportunity",
    "schedule_date": "2025-07-10T00:00:00Z",
    "schedule_time": "09:00",
    "status": "pending",
    "template_type": "sponsor",
    "created_at": "2025-07-04T12:00:00Z"
  }
]
```

### Update Scheduled Email
```
PUT /api/scheduled-emails/{email_id}
```
Update a scheduled email.

**Request:**
```json
{
  "subject": "Updated Subject",
  "schedule_time": "10:00"
}
```

**Response:**
```json
{
  "message": "Scheduled email updated successfully"
}
```

### Cancel Scheduled Email
```
DELETE /api/scheduled-emails/{email_id}
```
Cancel a scheduled email.

**Response:**
```json
{
  "message": "Scheduled email cancelled successfully"
}
```

### Scheduled Email Analytics
```
GET /api/analytics/scheduled-emails
```
Get analytics for scheduled emails.

**Response:**
```json
{
  "overview": {
    "total_scheduled": 50,
    "pending": 30,
    "sent": 18,
    "failed": 2,
    "success_rate": 90.0
  },
  "by_date": {
    "2025-07-10": 10,
    "2025-07-11": 15
  },
  "by_type": {
    "sponsor": 35,
    "participant": 15
  },
  "upcoming": [...]
}
```

---

## 📁 File Upload & Processing

### Drag & Drop Upload
```
POST /api/upload-excel-drag-drop
```
Enhanced drag and drop Excel/CSV upload with automatic processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: CSV/Excel file
  - `upload_type`: "sponsors" or "participants"
  - `auto_process`: boolean (default: true)

**Response:**
```json
{
  "filename": "sponsors.csv",
  "total_records": 25,
  "upload_type": "sponsors",
  "processed_data": [...],
  "column_mapping": {
    "detected_fields": ["name", "email", "organization"],
    "suggested_mapping": {...},
    "confidence_score": 0.9
  },
  "data_quality": {
    "quality_score": 85.5,
    "total_records": 25,
    "valid_emails": 23,
    "missing_names": 0,
    "missing_organizations": 2,
    "issues": ["2 records missing organization"],
    "recommendations": [...]
  },
  "sponsors_created": 25
}
```

### Validate File Upload
```
POST /api/validate-excel-upload
```
Validate Excel/CSV file before processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV/Excel file)

**Response:**
```json
{
  "valid": true,
  "filename": "data.csv",
  "total_records": 25,
  "preview_data": [...],
  "column_analysis": {...},
  "quality_analysis": {...},
  "recommendations": [
    "File structure looks good",
    "Detected 3 standard fields",
    "Ready for processing"
  ]
}
```

---

## 📧 Template Management

### List Templates
```
GET /api/templates
```
Get all email templates.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Sponsor Outreach",
    "subject": "Partnership Opportunity",
    "content": "<html>...</html>",
    "template_type": "sponsor",
    "placeholders": ["{name}", "{organization}"],
    "created_at": "2025-07-04T12:00:00Z"
  }
]
```

### Create Template
```
POST /api/templates
```
Create a new email template.

**Request:**
```json
{
  "name": "Custom Template",
  "subject": "Custom Subject with {name}",
  "content": "<html>Hello {name} from {organization}...</html>",
  "template_type": "sponsor"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Custom Template",
  "subject": "Custom Subject with {name}",
  "content": "<html>Hello {name} from {organization}...</html>",
  "template_type": "sponsor",
  "placeholders": ["{name}", "{organization}"],
  "created_at": "2025-07-04T12:00:00Z"
}
```

### Get Template
```
GET /api/templates/{template_id}
```
Get a specific email template.

### Update Template
```
PUT /api/templates/{template_id}
```
Update an email template.

### Delete Template
```
DELETE /api/templates/{template_id}
```
Delete an email template.

---

## 📊 Analytics

### Sponsor Analytics
```
GET /api/analytics/sponsors
```
Get comprehensive sponsor analytics with charts and insights.

**Response:**
```json
{
  "overview": {
    "total_sponsors": 100,
    "emails_sent": 85,
    "responses_received": 25,
    "conversion_rate": 25.0
  },
  "charts": {
    "funnel": {...},
    "timeline": {...},
    "geography": {...}
  },
  "insights": [...]
}
```

### Certificate Analytics
```
GET /api/analytics/certificates
```
Get comprehensive certificate analytics.

### Dashboard Analytics
```
GET /api/analytics/dashboard
```
Get combined analytics for main dashboard.

**Response:**
```json
{
  "sponsors": {...},
  "certificates": {...},
  "summary": {
    "total_sponsors": 100,
    "total_participants": 500,
    "completion_rate": 85.0,
    "conversion_rate": 25.0
  }
}
```

---

## 📊 Advanced Charts

### Sponsor Funnel Chart
```
GET /api/charts/sponsor-funnel
```
Get sponsor conversion funnel chart data.

### Participant Journey Chart
```
GET /api/charts/participant-journey
```
Get participant journey timeline chart.

### Advanced Chart Types
```
GET /api/charts/advanced/{chart_type}?data_source=sponsors
```
Get advanced chart visualizations.

**Chart Types:**
- `3d_scatter` - 3D scatter plot
- `treemap` - Treemap visualization
- `sunburst` - Sunburst chart
- `sankey` - Sankey diagram
- `radar` - Radar chart
- `waterfall` - Waterfall chart
- `gauge` - Gauge chart
- `parallel_coordinates` - Parallel coordinates
- `animated_bar` - Animated bar chart

---

## 🏆 Certificate Management

### Certificate Templates
```
GET /api/certificates/templates
```
Get available certificate templates.

### Create Certificate Template
```
POST /api/certificates/templates
```
Create a new certificate template.

### Generate Certificate
```
POST /api/certificates/generate
```
Generate a single certificate.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `template_id`: Template ID
  - `participant_data`: JSON string with participant data
  - `format`: "pdf" or "png" (default: "pdf")

**Response:**
```json
{
  "certificate": "base64_encoded_certificate",
  "format": "pdf",
  "filename": "certificate_john_doe.pdf"
}
```

### Bulk Generate Certificates
```
POST /api/certificates/generate-batch
```
Generate certificates for multiple participants.

### Preview Certificate
```
GET /api/certificates/preview/{template_id}
```
Preview a certificate template with sample data.

---

## ❌ Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Resource not found |
| 422 | Validation Error - Invalid data format |
| 500 | Internal Server Error - Server error |

### Common Error Responses

**File Upload Error:**
```json
{
  "detail": "Only CSV and Excel files are supported"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Not Found Error:**
```json
{
  "detail": "Template not found"
}
```

---

## 📝 Data Models

### Sponsor Data
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "organization": "string",
  "additional_info": "object",
  "email_content": "string|null",
  "email_status": "pending|sent|failed",
  "timestamp": "datetime"
}
```

### Participant Data
```json
{
  "id": "string",
  "name": "string", 
  "email": "string",
  "additional_info": "object",
  "certificate_generated": "boolean",
  "certificate_sent": "boolean",
  "certificate_data": "string|null",
  "timestamp": "datetime"
}
```

### Scheduled Email
```json
{
  "id": "string",
  "recipient_email": "string",
  "subject": "string",
  "content": "string",
  "schedule_date": "datetime",
  "schedule_time": "string",
  "status": "pending|sent|failed",
  "template_type": "string",
  "attachments": "array|null",
  "created_at": "datetime",
  "sent_at": "datetime|null"
}
```

---

## 🔧 Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **File Upload**: 10 requests per minute per IP
- **Email Sending**: 50 emails per minute per user

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1625097600
```

---

## 📚 SDK & Libraries

### Python SDK Example
```python
import requests

class HackfinityAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def upload_sponsors(self, file_path):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/api/upload-sponsors",
                files={'file': f}
            )
        return response.json()
    
    def schedule_email(self, email_data):
        response = requests.post(
            f"{self.base_url}/api/schedule-email",
            json=email_data
        )
        return response.json()

# Usage
api = HackfinityAPI()
result = api.upload_sponsors("sponsors.csv")
```

### JavaScript/Node.js Example
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

class HackfinityAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }
    
    async uploadSponsors(filePath) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        
        const response = await axios.post(
            `${this.baseURL}/api/upload-sponsors`,
            form,
            { headers: form.getHeaders() }
        );
        return response.data;
    }
    
    async scheduleEmail(emailData) {
        const response = await axios.post(
            `${this.baseURL}/api/schedule-email`,
            emailData
        );
        return response.data;
    }
}

// Usage
const api = new HackfinityAPI();
api.uploadSponsors('sponsors.csv').then(console.log);
```

---

## 🧪 Testing

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints directly.

### Example cURL Commands

**Upload Sponsors:**
```bash
curl -X POST "http://localhost:8000/api/upload-sponsors" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sponsors.csv"
```

**Schedule Email:**
```bash
curl -X POST "http://localhost:8000/api/schedule-email" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "test@example.com",
    "subject": "Test Email",
    "content": "Test content",
    "schedule_date": "2025-07-10",
    "schedule_time": "09:00",
    "template_type": "sponsor"
  }'
```

**Get Analytics:**
```bash
curl -X GET "http://localhost:8000/api/analytics/dashboard"
```

---

## 🔄 Webhooks (Future Feature)

Future versions will support webhooks for real-time notifications:

```json
{
  "event": "email.sent",
  "data": {
    "email_id": "uuid",
    "recipient": "sponsor@company.com",
    "status": "sent",
    "timestamp": "2025-07-04T12:00:00Z"
  },
  "webhook_id": "uuid"
}
```

---

## 📞 Support

For API support and questions:
- **Documentation**: https://docs.hackfinity.com
- **Issues**: GitHub Issues
- **Email**: api-support@hackfinity.com

---

*This documentation is for Hackfinity Platform API v1.0. For the latest updates, visit our documentation site.*
