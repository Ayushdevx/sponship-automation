#!/usr/bin/env python3
"""
Hackfinity Platform - Clean Server Implementation
Core functionality for email scheduling, file uploads, and basic analytics
"""

from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import pandas as pd
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import asyncio
import tempfile
import json
import base64

# PDF Generation imports
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("ReportLab not available. PDF generation will be disabled.")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
try:
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'hackfinity_db')]
    MONGO_AVAILABLE = True
except Exception as e:
    logger.warning(f"MongoDB connection failed: {e}. Using in-memory storage.")
    MONGO_AVAILABLE = False
    db = None

# Create FastAPI app
app = FastAPI(
    title="Hackfinity Platform API",
    description="Certificate generation and sponsor management platform",
    version="2.0.0",
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

# Data Models
class SponsorData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    organization: str
    additional_info: dict = {}
    email_content: Optional[str] = None
    email_status: str = "pending"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ParticipantData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    additional_info: dict = {}
    certificate_generated: bool = False
    certificate_sent: bool = False
    certificate_data: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EmailTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject: str
    content: str
    template_type: str = "sponsor"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Email configuration
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# In-memory storage (fallback when MongoDB is not available)
memory_storage = {
    "sponsors": [],
    "participants": [],
    "templates": []
}

# Helper Functions
async def store_data(collection: str, data: dict):
    """Store data in MongoDB or memory"""
    if MONGO_AVAILABLE:
        collection_obj = getattr(db, collection)
        await collection_obj.insert_one(data)
    else:
        memory_storage[collection].append(data)

async def get_data(collection: str, query: dict = None):
    """Get data from MongoDB or memory"""
    if MONGO_AVAILABLE:
        collection_obj = getattr(db, collection)
        if query:
            cursor = collection_obj.find(query)
        else:
            cursor = collection_obj.find()
        return await cursor.to_list(length=None)
    else:
        return memory_storage.get(collection, [])

async def process_csv_file(file_content: bytes, filename: str) -> List[dict]:
    """Process uploaded CSV file"""
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Convert to list of dictionaries
        data = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            # Handle NaN values
            row_dict = {k: (v if pd.notna(v) else "") for k, v in row_dict.items()}
            data.append(row_dict)
        
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

async def generate_email_content(sponsor_data: dict) -> str:
    """Generate email content for sponsors"""
    name = sponsor_data.get('Name', sponsor_data.get('name', 'Valued Partner'))
    organization = sponsor_data.get('Organization', sponsor_data.get('organization', 'Your Organization'))
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4A90E2;">Partnership Opportunity with Hackfinity 🚀</h2>
            <p>Dear <strong>{name}</strong>,</p>
            <p>I hope this email finds you well. I'm reaching out to introduce you to <strong>Hackfinity</strong>, the world's biggest Agentic AI hackathon, and explore potential partnership opportunities with <strong>{organization}</strong>.</p>
            
            <h3 style="color: #4A90E2;">Why Partner with Hackfinity?</h3>
            <p>Hackfinity brings together the brightest minds in AI, ML, Blockchain, EdTech, FinTech, and Healthcare to build the future of technology.</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4 style="color: #2C3E50; margin-bottom: 10px;">🎯 Partnership Benefits:</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Access to top-tier talent from around the world</li>
                    <li>Brand visibility to thousands of developers and innovators</li>
                    <li>Opportunity to mentor breakthrough AI projects</li>
                    <li>Early access to cutting-edge solutions</li>
                    <li>Networking with industry leaders and VCs</li>
                </ul>
            </div>
            
            <p>I'd love to discuss how we can collaborate to make this hackathon a tremendous success. Would you be available for a brief call next week to explore partnership opportunities?</p>
            
            <p style="margin-top: 30px;">
                Best regards,<br>
                <strong>The Hackfinity Team</strong><br>
                <em>Building the Future with AI</em>
            </p>
        </div>
    </body>
    </html>
    """

async def generate_certificate(participant_name: str, event_name: str = "Hackfinity 2025") -> str:
    """Generate certificate PDF and return as base64"""
    if not PDF_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF generation not available")
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            doc = SimpleDocTemplate(tmp_file.name, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=36,
                textColor=HexColor('#4A90E2'),
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=HexColor('#666666'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            name_style = ParagraphStyle(
                'CustomName',
                parent=styles['Heading1'],
                fontSize=48,
                textColor=HexColor('#2C3E50'),
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['Normal'],
                fontSize=16,
                textColor=HexColor('#333333'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            # Certificate content
            story.append(Spacer(1, 1*inch))
            story.append(Paragraph("🚀 CERTIFICATE OF PARTICIPATION", title_style))
            story.append(Spacer(1, 0.5*inch))
            
            story.append(Paragraph("This is to certify that", subtitle_style))
            story.append(Paragraph(f"<b>{participant_name}</b>", name_style))
            story.append(Paragraph(f"has successfully participated in", content_style))
            story.append(Paragraph(f"<b>{event_name}</b>", title_style))
            story.append(Paragraph("The World's Biggest Agentic AI Hackathon", subtitle_style))
            
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("Demonstrating excellence in AI innovation, collaboration,", content_style))
            story.append(Paragraph("and cutting-edge technology development", content_style))
            
            story.append(Spacer(1, 1*inch))
            story.append(Paragraph(f"Issued on: {datetime.now().strftime('%B %d, %Y')}", content_style))
            story.append(Paragraph("Hackfinity Team", content_style))
            
            doc.build(story)
            
            with open(tmp_file.name, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
                base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
            
            os.unlink(tmp_file.name)
            return base64_pdf
            
    except Exception as e:
        logger.error(f"Error generating certificate for {participant_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Certificate generation failed: {str(e)}")

async def send_email(to_email: str, subject: str, html_content: str, attachment_data: str = None, attachment_name: str = None) -> bool:
    """Send email using Gmail SMTP"""
    try:
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            logger.warning("Email credentials not configured")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Add attachment if provided
        if attachment_data and attachment_name:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(base64.b64decode(attachment_data))
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
            msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {str(e)}")
        return False

# API Routes
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "🚀 Welcome to Hackfinity Platform API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "📧 Email Management",
            "📁 File Upload Processing", 
            "🏆 Certificate Generation",
            "📊 Basic Analytics"
        ],
        "endpoints": {
            "docs": "/docs",
            "api": "/api"
        },
        "services": {
            "mongodb": MONGO_AVAILABLE,
            "pdf_generation": PDF_AVAILABLE,
            "email": bool(EMAIL_ADDRESS and EMAIL_PASSWORD)
        }
    }

@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {"message": "Hackfinity Platform API", "version": "2.0.0"}

@api_router.post("/upload-sponsors")
async def upload_sponsors(file: UploadFile = File(...)):
    """Upload sponsor CSV/Excel file and generate email content"""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    try:
        file_content = await file.read()
        sponsors_data = await process_csv_file(file_content, file.filename)
        
        sponsors = []
        for sponsor_data in sponsors_data:
            email_content = await generate_email_content(sponsor_data)
            
            sponsor = SponsorData(
                name=sponsor_data.get('Name', sponsor_data.get('name', 'Unknown')),
                email=sponsor_data.get('Email', sponsor_data.get('email', '')),
                organization=sponsor_data.get('Organization', sponsor_data.get('organization', 'Unknown')),
                additional_info=sponsor_data,
                email_content=email_content,
                email_status="generated"
            )
            
            sponsors.append(sponsor)
            await store_data("sponsors", sponsor.dict())
        
        return {
            "message": "Sponsors uploaded successfully",
            "sponsors": [s.dict() for s in sponsors],
            "total_count": len(sponsors),
            "preview_email": sponsors[0].email_content if sponsors else ""
        }
        
    except Exception as e:
        logger.error(f"Error uploading sponsors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/upload-participants")
async def upload_participants(file: UploadFile = File(...)):
    """Upload participant CSV/Excel file and generate certificates"""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    try:
        file_content = await file.read()
        participants_data = await process_csv_file(file_content, file.filename)
        
        participants = []
        for participant_data in participants_data:
            participant_name = participant_data.get('Name', participant_data.get('name', 'Unknown'))
            
            # Generate certificate if PDF is available
            certificate_data = None
            certificate_generated = False
            if PDF_AVAILABLE:
                try:
                    certificate_data = await generate_certificate(participant_name)
                    certificate_generated = True
                except Exception as cert_error:
                    logger.error(f"Error generating certificate for {participant_name}: {cert_error}")
            
            participant = ParticipantData(
                name=participant_name,
                email=participant_data.get('Email', participant_data.get('email', '')),
                additional_info=participant_data,
                certificate_generated=certificate_generated,
                certificate_data=certificate_data
            )
            
            participants.append(participant)
            await store_data("participants", participant.dict())
        
        return {
            "message": "Participants uploaded successfully",
            "participants": [p.dict() for p in participants],
            "total_count": len(participants),
            "certificates_generated": sum(1 for p in participants if p.certificate_generated)
        }
        
    except Exception as e:
        logger.error(f"Error uploading participants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/send-sponsor-emails")
async def send_sponsor_emails(background_tasks: BackgroundTasks):
    """Send generated emails to all sponsors"""
    sponsors = await get_data("sponsors", {"email_status": "generated"})
    
    if not sponsors:
        raise HTTPException(status_code=400, detail="No sponsors found with generated emails")
    
    for sponsor in sponsors:
        background_tasks.add_task(send_sponsor_email_task, sponsor)
    
    return {"message": f"Sending emails to {len(sponsors)} sponsors", "count": len(sponsors)}

@api_router.post("/send-certificates")
async def send_certificates(background_tasks: BackgroundTasks):
    """Send certificates to all participants"""
    participants = await get_data("participants", {"certificate_generated": True, "certificate_sent": False})
    
    if not participants:
        raise HTTPException(status_code=400, detail="No participants found with generated certificates")
    
    for participant in participants:
        background_tasks.add_task(send_certificate_task, participant)
    
    return {"message": f"Sending certificates to {len(participants)} participants", "count": len(participants)}

async def send_sponsor_email_task(sponsor: dict):
    """Background task to send sponsor email"""
    try:
        subject = f"Partnership Opportunity with Hackfinity - {sponsor['organization']}"
        success = await send_email(sponsor['email'], subject, sponsor['email_content'])
        
        # Update status (simplified for now)
        logger.info(f"Email {'sent' if success else 'failed'} to {sponsor['email']}")
        
    except Exception as e:
        logger.error(f"Error in sponsor email task: {str(e)}")

async def send_certificate_task(participant: dict):
    """Background task to send certificate email"""
    try:
        subject = f"🎉 Your Hackfinity Participation Certificate - {participant['name']}"
        
        email_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #4A90E2;">🎉 Congratulations!</h1>
                <h2>Dear {participant['name']},</h2>
                <p>Thank you for participating in <strong>Hackfinity 2025</strong> - The World's Biggest Agentic AI Hackathon!</p>
                <p>Your participation certificate is attached to this email.</p>
                <p>Keep building the future with AI!</p>
                <p><strong>The Hackfinity Team</strong></p>
            </div>
        </body>
        </html>
        """
        
        success = await send_email(
            participant['email'], 
            subject, 
            email_content,
            participant.get('certificate_data'),
            f"{participant['name']}_Hackfinity_Certificate.pdf"
        )
        
        logger.info(f"Certificate {'sent' if success else 'failed'} to {participant['email']}")
        
    except Exception as e:
        logger.error(f"Error in certificate task: {str(e)}")

@api_router.get("/sponsors")
async def get_sponsors():
    """Get all sponsors"""
    sponsors = await get_data("sponsors")
    return sponsors

@api_router.get("/participants")
async def get_participants():
    """Get all participants"""
    participants = await get_data("participants")
    return participants

@api_router.get("/analytics")
async def get_analytics():
    """Get basic analytics"""
    sponsors = await get_data("sponsors")
    participants = await get_data("participants")
    
    return {
        "sponsors": {
            "total": len(sponsors),
            "emails_generated": len([s for s in sponsors if s.get('email_status') == 'generated']),
            "emails_sent": len([s for s in sponsors if s.get('email_status') == 'sent'])
        },
        "participants": {
            "total": len(participants),
            "certificates_generated": len([p for p in participants if p.get('certificate_generated')]),
            "certificates_sent": len([p for p in participants if p.get('certificate_sent')])
        },
        "system": {
            "mongodb_available": MONGO_AVAILABLE,
            "pdf_generation_available": PDF_AVAILABLE,
            "email_configured": bool(EMAIL_ADDRESS and EMAIL_PASSWORD)
        }
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "mongodb": "available" if MONGO_AVAILABLE else "unavailable",
            "pdf_generation": "available" if PDF_AVAILABLE else "unavailable",
            "email": "configured" if EMAIL_ADDRESS and EMAIL_PASSWORD else "not_configured"
        }
    }

# Include API router
app.include_router(api_router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Hackfinity Platform API starting up...")
    logger.info(f"MongoDB: {'Connected' if MONGO_AVAILABLE else 'Not available'}")
    logger.info(f"PDF Generation: {'Available' if PDF_AVAILABLE else 'Not available'}")
    logger.info(f"Email: {'Configured' if EMAIL_ADDRESS and EMAIL_PASSWORD else 'Not configured'}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Hackfinity Platform API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
