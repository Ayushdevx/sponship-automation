#!/usr/bin/env python3
"""
Minimal Hackfinity Platform Server for testing
"""

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Hackfinity Platform API - Minimal",
    description="Minimal server for testing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router
api_router = APIRouter(prefix="/api")

# Simple data models
class EmailScheduleData(BaseModel):
    recipient_email: str
    subject: str
    content: str
    schedule_date: str
    schedule_time: str
    template_type: str = "sponsor"
    priority: str = "normal"
    recurring: bool = False

# In-memory storage
email_schedules = []
uploaded_files = []

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "mongodb": "not_configured",
            "pdf_generation": "available",
            "email": "configured"
        }
    }

@api_router.post("/schedule-email")
async def schedule_email(email_data: EmailScheduleData):
    """Schedule an email"""
    logger.info(f"Scheduling email to {email_data.recipient_email}")
    
    # Create schedule entry
    schedule_entry = {
        "id": str(uuid.uuid4()),
        "recipient_email": email_data.recipient_email,
        "subject": email_data.subject,
        "content": email_data.content,
        "schedule_date": email_data.schedule_date,
        "schedule_time": email_data.schedule_time,
        "template_type": email_data.template_type,
        "priority": email_data.priority,
        "recurring": email_data.recurring,
        "status": "scheduled",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store in memory
    email_schedules.append(schedule_entry)
    
    logger.info(f"Email scheduled successfully with ID: {schedule_entry['id']}")
    
    return {
        "message": "Email scheduled successfully",
        "schedule_id": schedule_entry["id"],
        "schedule": schedule_entry
    }

@api_router.get("/scheduled-emails")
async def get_scheduled_emails():
    """Get all scheduled emails"""
    return {
        "scheduled_emails": email_schedules,
        "total": len(email_schedules)
    }

@api_router.get("/analytics")
async def get_analytics():
    """Get basic analytics"""
    return {
        "sponsor_stats": {"total": 0, "sent": 0, "failed": 0, "pending": 0},
        "certificate_stats": {"total": 0, "sent": 0, "failed": 0, "pending": 0},
        "email_stats": {"scheduled": len(email_schedules), "sent": 0, "failed": 0}
    }

# Add API router to app
app.include_router(api_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hackfinity Platform API - Minimal Version", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Hackfinity Platform - Minimal Server")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
