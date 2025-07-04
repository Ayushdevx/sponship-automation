"""
Hackfinity Platform - Core Backend Server
Simplified version focusing on email scheduling and file upload functionality
"""

import os
import asyncio
import logging
import threading
import uuid
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import schedule
import time
import pandas as pd

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

# Email imports
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Environment and database
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo

# Load environment variables
load_dotenv()

# Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "hackfinity_platform")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection (will work even if MongoDB is not available)
try:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    logger.info("MongoDB connection initialized")
except Exception as e:
    logger.warning(f"MongoDB connection failed: {e}")
    db = None

# Global variable to store scheduled emails
scheduled_emails = {}

# Pydantic models
class ScheduledEmailCreate(BaseModel):
    recipient_email: EmailStr
    subject: str
    content: str
    schedule_date: str  # ISO format date
    schedule_time: str  # HH:MM format
    template_type: str = "general"
    attachments: Optional[List[str]] = []

class ScheduledEmail(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_email: EmailStr
    subject: str
    content: str
    schedule_date: datetime
    schedule_time: str
    template_type: str = "general"
    attachments: Optional[List[str]] = []
    status: str = "pending"  # pending, sent, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None

class BulkEmailSchedule(BaseModel):
    emails: List[EmailStr]
    subject: str
    content: str
    schedule_date: str
    schedule_time: str
    template_type: str = "general"

class SponsorData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    organization: str
    additional_info: Optional[Dict[str, Any]] = {}
    email_content: str = ""
    email_status: str = "uploaded"  # uploaded, generated, sent, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None

class ParticipantData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    additional_info: Optional[Dict[str, Any]] = {}
    certificate_generated: bool = False
    certificate_sent: bool = False
    certificate_data: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None

class StatusCheckCreate(BaseModel):
    message: str

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EmailGenerationResponse(BaseModel):
    sponsors: List[SponsorData]
    total_count: int
    preview_email: str

class CertificateGenerationResponse(BaseModel):
    participants: List[ParticipantData]
    total_count: int
    preview_certificate: str

# Create FastAPI app
app = FastAPI(
    title="Hackfinity Platform API",
    description="Certificate and Sponsorship Automation Platform",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions
async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email using Gmail SMTP"""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logger.warning("Email credentials not configured")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

async def process_csv_file(file_content: bytes, filename: str) -> List[dict]:
    """Process CSV/Excel file and return data"""
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError("Unsupported file format")
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        # Clean the data
        for item in data:
            for key, value in item.items():
                if pd.isna(value):
                    item[key] = ""
                else:
                    item[key] = str(value).strip()
        
        return data
        
    except Exception as e:
        logger.error(f"Error processing file {filename}: {str(e)}")
        raise ValueError(f"Error processing file: {str(e)}")

def schedule_email_job():
    """Background job to check and send scheduled emails"""
    current_time = datetime.now()
    current_time_str = current_time.strftime("%H:%M")
    current_date_str = current_time.date().isoformat()
    
    for email_id, scheduled_email in list(scheduled_emails.items()):
        if (scheduled_email.status == "pending" and 
            scheduled_email.schedule_date.date().isoformat() == current_date_str and
            scheduled_email.schedule_time == current_time_str):
            
            # Send the email
            asyncio.create_task(send_scheduled_email(scheduled_email))

async def send_scheduled_email(scheduled_email: ScheduledEmail) -> bool:
    """Send a scheduled email"""
    try:
        success = await send_email(
            scheduled_email.recipient_email,
            scheduled_email.subject,
            scheduled_email.content
        )
        
        # Update status
        scheduled_email.status = "sent" if success else "failed"
        scheduled_email.sent_at = datetime.utcnow()
        
        # Update in database if available
        if db:
            await db.scheduled_emails.update_one(
                {"id": scheduled_email.id},
                {"$set": {
                    "status": scheduled_email.status,
                    "sent_at": scheduled_email.sent_at
                }}
            )
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending scheduled email {scheduled_email.id}: {str(e)}")
        scheduled_email.status = "failed"
        return False

def start_email_scheduler():
    """Start the email scheduler in a background thread"""
    def run_scheduler():
        schedule.every().minute.do(schedule_email_job)
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Email scheduler started")

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Hackfinity Platform API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Email Scheduling",
            "File Upload & Processing",
            "Sponsor Management",
            "Participant Management"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if db else "disconnected"
    email_status = "configured" if EMAIL_ADDRESS and EMAIL_PASSWORD else "not configured"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": db_status,
        "email": email_status,
        "scheduled_emails": len(scheduled_emails)
    }

# Email Scheduling endpoints
@app.post("/api/schedule-email")
async def schedule_email(scheduled_email: ScheduledEmailCreate):
    """Schedule an email to be sent at a specific date and time"""
    try:
        # Parse schedule date and time
        schedule_datetime = datetime.fromisoformat(scheduled_email.schedule_date)
        
        # Create scheduled email object
        email_obj = ScheduledEmail(
            recipient_email=scheduled_email.recipient_email,
            subject=scheduled_email.subject,
            content=scheduled_email.content,
            schedule_date=schedule_datetime,
            schedule_time=scheduled_email.schedule_time,
            template_type=scheduled_email.template_type,
            attachments=scheduled_email.attachments
        )
        
        # Store in memory and database
        scheduled_emails[email_obj.id] = email_obj
        
        if db:
            await db.scheduled_emails.insert_one(email_obj.dict())
        
        return {
            "message": "Email scheduled successfully",
            "email_id": email_obj.id,
            "scheduled_for": f"{scheduled_email.schedule_date} {scheduled_email.schedule_time}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error scheduling email: {str(e)}")

@app.get("/api/scheduled-emails")
async def get_scheduled_emails():
    """Get all scheduled emails"""
    try:
        if db:
            emails = await db.scheduled_emails.find().to_list(None)
            return [ScheduledEmail(**email) for email in emails]
        else:
            return list(scheduled_emails.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scheduled emails: {str(e)}")

@app.delete("/api/scheduled-emails/{email_id}")
async def cancel_scheduled_email(email_id: str):
    """Cancel a scheduled email"""
    try:
        if db:
            result = await db.scheduled_emails.delete_one({"id": email_id})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Scheduled email not found")
        
        # Remove from memory
        if email_id in scheduled_emails:
            del scheduled_emails[email_id]
        
        return {"message": "Scheduled email cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error cancelling scheduled email: {str(e)}")

# File Upload endpoints
@app.post("/api/upload-sponsors")
async def upload_sponsors(file: UploadFile = File(...)):
    """Upload sponsor CSV/Excel file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Read and process file
        file_content = await file.read()
        sponsors_data = await process_csv_file(file_content, file.filename)
        
        # Create sponsor records
        sponsors = []
        for sponsor_data in sponsors_data:
            sponsor = SponsorData(
                name=sponsor_data.get('name', 'Unknown'),
                email=sponsor_data.get('email', ''),
                organization=sponsor_data.get('organization', 'Unknown'),
                additional_info=sponsor_data,
                email_content="Email content will be generated here",
                email_status="generated"
            )
            sponsors.append(sponsor)
            
            # Save to database if available
            if db:
                await db.sponsors.insert_one(sponsor.dict())
        
        return EmailGenerationResponse(
            sponsors=sponsors,
            total_count=len(sponsors),
            preview_email="<p>Dear Sponsor,</p><p>Thank you for your interest in Hackfinity...</p>"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@app.post("/api/upload-participants")
async def upload_participants(file: UploadFile = File(...)):
    """Upload participant CSV/Excel file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Read and process file
        file_content = await file.read()
        participants_data = await process_csv_file(file_content, file.filename)
        
        # Create participant records
        participants = []
        for participant_data in participants_data:
            participant = ParticipantData(
                name=participant_data.get('name', 'Unknown'),
                email=participant_data.get('email', ''),
                additional_info=participant_data,
                certificate_generated=True,
                certificate_data="Certificate data will be generated here"
            )
            participants.append(participant)
            
            # Save to database if available
            if db:
                await db.participants.insert_one(participant.dict())
        
        return CertificateGenerationResponse(
            participants=participants,
            total_count=len(participants),
            preview_certificate="Certificate preview for participant"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@app.get("/api/sponsors")
async def get_sponsors():
    """Get all sponsors"""
    try:
        if db:
            sponsors = await db.sponsors.find().to_list(None)
            return [SponsorData(**sponsor) for sponsor in sponsors]
        else:
            return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sponsors: {str(e)}")

@app.get("/api/participants")
async def get_participants():
    """Get all participants"""
    try:
        if db:
            participants = await db.participants.find().to_list(None)
            return [ParticipantData(**participant) for participant in participants]
        else:
            return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching participants: {str(e)}")

@app.post("/api/send-sponsor-emails")
async def send_sponsor_emails(background_tasks: BackgroundTasks):
    """Send emails to all sponsors"""
    try:
        if db:
            sponsors = await db.sponsors.find({"email_status": "generated"}).to_list(None)
        else:
            sponsors = []
        
        if not sponsors:
            raise HTTPException(status_code=404, detail="No sponsors with generated emails found")
        
        # Add email sending to background tasks
        for sponsor in sponsors:
            if sponsor.get('email') and sponsor.get('email_content'):
                background_tasks.add_task(
                    send_email,
                    sponsor['email'],
                    f"Partnership Opportunity with Hackfinity - {sponsor['organization']}",
                    sponsor['email_content']
                )
        
        return {"message": f"Sending emails to {len(sponsors)} sponsors", "count": len(sponsors)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending sponsor emails: {str(e)}")

# Initialize scheduler on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    try:
        # Load existing scheduled emails from database
        if db:
            existing_emails = await db.scheduled_emails.find({"status": "pending"}).to_list(None)
            for email_data in existing_emails:
                email_obj = ScheduledEmail(**email_data)
                scheduled_emails[email_obj.id] = email_obj
        
        # Start the email scheduler
        start_email_scheduler()
        
        logger.info(f"Application started successfully. Loaded {len(scheduled_emails)} scheduled emails.")
        print("🚀 Hackfinity Platform started successfully!")
        print(f"📧 Email scheduler running with {len(scheduled_emails)} scheduled emails")
        print("🌐 Server running at http://localhost:8000")
        print("📊 API documentation available at http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Application shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
