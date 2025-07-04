from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
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
import schedule
import threading
import time
from typing import Dict, Any

# Import our custom modules
from analytics import AnalyticsEngine
from template_engine import TemplateEngine
from certificate_customizer import CertificateCustomizer
import base64
import tempfile
import json

# Global variable to store scheduled emails
scheduled_emails = {}

# Mock classes for emergentintegrations
class UserMessage:
    def __init__(self, text: str):
        self.text = text

class LlmChat:
    def __init__(self, api_key: str, session_id: str, system_message: str):
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
    
    def with_model(self, provider: str, model: str):
        return self
    
    async def send_message(self, message):
        # Simple mock response - in production this would use the actual AI service
        return type('Response', (), {
            'text': f"""
            <html>
            <body>
            <p>Dear Sponsor,</p>
            <p>We are excited to invite you to partner with Hackfinity, the world's biggest Agentic AI hackathon!</p>
            <p>Our event focuses on cutting-edge domains including AI, ML, Blockchain, EdTech, FinTech, and Healthcare.</p>
            <p>By sponsoring Hackfinity, you'll gain:</p>
            <ul>
                <li>Brand exposure to thousands of talented developers</li>
                <li>Access to innovative solutions and talent</li>
                <li>Networking opportunities with industry leaders</li>
                <li>Direct engagement with the AI community</li>
            </ul>
            <p>We would love to discuss sponsorship opportunities with you.</p>
            <p>Best regards,<br>The Hackfinity Team</p>
            </body>
            </html>
            """
        })()
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import base64
import tempfile
from analytics import AnalyticsEngine
from template_engine import TemplateEngine, AdvancedTemplate, TemplateCategory, TEMPLATE_LIBRARY
from certificate_customizer import CertificateCustomizer, CertificateTemplate, CertificateStyle, CertificateElement, CERTIFICATE_TEMPLATES
import plotly.graph_objects as go

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Initialize services
analytics_service = AnalyticsEngine(db)
template_service = TemplateEngine(db)
certificate_service = CertificateCustomizer(db)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class SponsorData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    organization: str
    additional_info: dict = {}
    email_content: Optional[str] = None
    email_status: str = "pending"  # pending, sent, failed
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ParticipantData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    additional_info: dict = {}
    certificate_generated: bool = False
    certificate_sent: bool = False
    certificate_data: Optional[str] = None  # base64 encoded certificate
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EmailTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject: str
    content: str
    placeholders: List[str] = []
    template_type: str = "sponsor"  # sponsor, participant, custom
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EmailGenerationResponse(BaseModel):
    sponsors: List[SponsorData]
    total_count: int
    preview_email: str

class CertificateGenerationResponse(BaseModel):
    participants: List[ParticipantData]
    total_count: int
    preview_certificate: str  # base64 encoded

class TemplateRequest(BaseModel):
    name: str
    subject: str
    content: str
    template_type: str = "sponsor"

# Additional models for scheduling
class ScheduledEmail(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_email: str
    subject: str
    content: str
    schedule_date: datetime
    schedule_time: str  # Format: "HH:MM"
    status: str = "pending"  # pending, sent, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    template_type: str = "sponsor"  # sponsor, certificate, general
    attachments: Optional[List[str]] = None

class ScheduledEmailCreate(BaseModel):
    recipient_email: str
    subject: str
    content: str
    schedule_date: str  # ISO date format
    schedule_time: str  # HH:MM format
    template_type: str = "sponsor"
    attachments: Optional[List[str]] = None

class BulkEmailSchedule(BaseModel):
    emails: List[str]
    subject: str
    content: str
    schedule_date: str
    schedule_time: str
    template_type: str = "sponsor"

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'hackfinity.innovation@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'fdfl ehph igpp qfmz')

# Gemini AI configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyAMylAU5PgE1Esto97QTPNblQ6NhscplN8')

async def process_csv_file(file_content: bytes, filename: str) -> List[dict]:
    """Process uploaded CSV/Excel file and extract data"""
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError("Unsupported file format")
        
        # Convert to list of dictionaries
        data = []
        for _, row in df.iterrows():
            item = {}
            # Map common column names
            for col in df.columns:
                col_lower = col.lower()
                if 'name' in col_lower and 'organization' not in col_lower:
                    item['name'] = str(row[col])
                elif 'email' in col_lower:
                    item['email'] = str(row[col])
                elif 'organization' in col_lower or 'company' in col_lower:
                    item['organization'] = str(row[col])
                else:
                    item[col] = str(row[col])
            
            # Ensure required fields
            if 'name' not in item:
                item['name'] = item.get('Name', 'Unknown')
            if 'email' not in item:
                item['email'] = item.get('Email', '')
            if 'organization' not in item:
                item['organization'] = item.get('Organization', item.get('Company', 'Unknown'))
            
            data.append(item)
        
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

async def generate_email_content(sponsor_data: dict, template: dict = None) -> str:
    """Generate personalized email content using Gemini AI or template"""
    try:
        if template:
            # Use template
            content = template['content']
            subject = template['subject']
            
            # Replace placeholders
            for key, value in sponsor_data.items():
                placeholder = f"{{{key}}}"
                content = content.replace(placeholder, str(value))
                subject = subject.replace(placeholder, str(value))
            
            return content
        else:
            # Use AI generation
            chat = LlmChat(
                api_key=GEMINI_API_KEY,
                session_id=f"sponsor_{uuid.uuid4()}",
                system_message="""You are an expert email copywriter for Hackfinity, the world's biggest Agentic AI hackathon. 
                Generate personalized, persuasive, and engaging sponsor outreach emails that highlight:
                1. Hackfinity's impressive scale and global reach
                2. Focus on AI, ML, Blockchain, EdTech, FinTech, Healthcare domains
                3. Specific sponsorship benefits and ROI
                4. Collaboration opportunities
                5. Clear call-to-action
                
                Make each email unique and tailored to the sponsor's profile. Use professional tone but be engaging."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            prompt = f"""
            Create a personalized sponsor outreach email for:
            - Name: {sponsor_data.get('name', 'Unknown')}
            - Organization: {sponsor_data.get('organization', 'Unknown')}
            - Email: {sponsor_data.get('email', 'Unknown')}
            - Additional context: {sponsor_data.get('additional_info', {})}
            
            The email should:
            1. Address them personally
            2. Highlight Hackfinity's scale (world's biggest Agentic AI hackathon)
            3. Mention relevant domains (AI, ML, Blockchain, EdTech, FinTech, Healthcare)
            4. Present clear sponsorship benefits
            5. Include a compelling call-to-action
            6. Be professional yet engaging
            
            Format as HTML email with proper structure.
            """
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            return response
    except Exception as e:
        logging.error(f"Error generating email for {sponsor_data.get('name')}: {str(e)}")
        return f"""
        <html>
        <body>
            <h2>Partnership Opportunity with Hackfinity</h2>
            <p>Dear {sponsor_data.get('name', 'Team')},</p>
            <p>I hope this email finds you well. I'm reaching out to introduce you to Hackfinity, the world's biggest Agentic AI hackathon, and explore potential partnership opportunities.</p>
            <p>Hackfinity brings together the brightest minds in AI, ML, Blockchain, EdTech, FinTech, and Healthcare to build the future of technology. As a leader in the {sponsor_data.get('organization', 'industry')}, your expertise would be invaluable to our community.</p>
            <p>Benefits of partnering with us:</p>
            <ul>
                <li>Access to top-tier talent from around the world</li>
                <li>Brand visibility to thousands of developers and innovators</li>
                <li>Opportunity to mentor and connect with breakthrough projects</li>
                <li>Early access to cutting-edge AI solutions</li>
            </ul>
            <p>I'd love to discuss how we can collaborate to make this hackathon a success. Would you be available for a brief call next week?</p>
            <p>Best regards,<br>The Hackfinity Team</p>
        </body>
        </html>
        """

async def generate_certificate(participant_name: str, event_name: str = "Hackfinity 2025") -> str:
    """Generate a certificate PDF and return as base64 string"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            # Create PDF document
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
            
            # Build PDF
            doc.build(story)
            
            # Read the PDF file and encode as base64
            with open(tmp_file.name, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
                base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            return base64_pdf
            
    except Exception as e:
        logging.error(f"Error generating certificate for {participant_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Certificate generation failed: {str(e)}")

async def send_certificate_email(participant_email: str, participant_name: str, certificate_data: str) -> bool:
    """Send certificate via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = participant_email
        msg['Subject'] = f"🎉 Your Hackfinity Participation Certificate - {participant_name}"
        
        # Email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;">
                <div style="background: white; padding: 30px; border-radius: 8px; text-align: center;">
                    <h1 style="color: #4A90E2; margin-bottom: 20px;">🎉 Congratulations!</h1>
                    <h2 style="color: #2C3E50; margin-bottom: 20px;">Dear {participant_name},</h2>
                    <p style="font-size: 18px; margin-bottom: 20px;">
                        Thank you for participating in <strong>Hackfinity 2025</strong> - The World's Biggest Agentic AI Hackathon!
                    </p>
                    <p style="font-size: 16px; margin-bottom: 20px;">
                        Your participation certificate is attached to this email. We're proud to have had you as part of our amazing community of innovators and AI enthusiasts.
                    </p>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #4A90E2; margin-bottom: 10px;">🚀 What's Next?</h3>
                        <p style="margin-bottom: 10px;">• Connect with fellow participants on our community platform</p>
                        <p style="margin-bottom: 10px;">• Share your experience on social media</p>
                        <p style="margin-bottom: 10px;">• Stay tuned for future Hackfinity events</p>
                    </div>
                    <p style="font-size: 14px; color: #666;">
                        Keep building the future with AI!<br>
                        <strong>The Hackfinity Team</strong>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach certificate PDF
        pdf_attachment = MIMEBase('application', 'pdf')
        pdf_attachment.set_payload(base64.b64decode(certificate_data))
        encoders.encode_base64(pdf_attachment)
        pdf_attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="{participant_name}_Hackfinity_Certificate.pdf"'
        )
        msg.attach(pdf_attachment)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        logging.error(f"Error sending certificate to {participant_email}: {str(e)}")
        return False

async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email using Gmail SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to Gmail SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        logging.error(f"Error sending email to {to_email}: {str(e)}")
        return False

# Email scheduler functions
def schedule_email_job():
    """Background job to check and send scheduled emails"""
    current_time = datetime.now()
    current_time_str = current_time.strftime("%H:%M")
    current_date_str = current_time.date().isoformat()
    
    for email_id, scheduled_email in scheduled_emails.items():
        if (scheduled_email.status == "pending" and 
            scheduled_email.schedule_date.date().isoformat() == current_date_str and
            scheduled_email.schedule_time == current_time_str):
            
            # Send the email
            success = asyncio.run(send_scheduled_email(scheduled_email))
            
            if success:
                scheduled_email.status = "sent"
                scheduled_email.sent_at = current_time
                logging.info(f"Scheduled email {email_id} sent successfully")
            else:
                scheduled_email.status = "failed"
                logging.error(f"Failed to send scheduled email {email_id}")

async def send_scheduled_email(scheduled_email: ScheduledEmail) -> bool:
    """Send a scheduled email"""
    try:
        return await send_email(
            scheduled_email.recipient_email,
            scheduled_email.subject,
            scheduled_email.content
        )
    except Exception as e:
        logging.error(f"Error sending scheduled email: {str(e)}")
        return False

def start_email_scheduler():
    """Start the email scheduler in a background thread"""
    def run_scheduler():
        schedule.every().minute.do(schedule_email_job)
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logging.info("Email scheduler started")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Hackfinity Communication Platform API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/upload-sponsors", response_model=EmailGenerationResponse)
async def upload_sponsors(file: UploadFile = File(...)):
    """Upload sponsor CSV/Excel file and generate email content"""
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    # Read file content
    file_content = await file.read()
    
    # Process the file
    sponsors_data = await process_csv_file(file_content, file.filename)
    
    # Generate emails for all sponsors
    sponsors = []
    preview_email = ""
    
    for i, sponsor_data in enumerate(sponsors_data):
        try:
            # Generate email content
            email_content = await generate_email_content(sponsor_data)
            
            # Create sponsor object
            sponsor = SponsorData(
                name=sponsor_data.get('name', 'Unknown'),
                email=sponsor_data.get('email', ''),
                organization=sponsor_data.get('organization', 'Unknown'),
                additional_info=sponsor_data,
                email_content=email_content,
                email_status="generated"
            )
            
            sponsors.append(sponsor)
            
            # Use first email as preview
            if i == 0:
                preview_email = email_content
            
            # Store in database
            await db.sponsors.insert_one(sponsor.dict())
            
        except Exception as e:
            logging.error(f"Error processing sponsor {sponsor_data.get('name')}: {str(e)}")
            continue
    
    return EmailGenerationResponse(
        sponsors=sponsors,
        total_count=len(sponsors),
        preview_email=preview_email
    )

@api_router.post("/upload-participants", response_model=CertificateGenerationResponse)
async def upload_participants(file: UploadFile = File(...)):
    """Upload participant CSV/Excel file and generate certificates"""
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    # Read file content
    file_content = await file.read()
    
    # Process the file
    participants_data = await process_csv_file(file_content, file.filename)
    
    # Generate certificates for all participants
    participants = []
    preview_certificate = ""
    
    for i, participant_data in enumerate(participants_data):
        try:
            # Generate certificate
            certificate_data = await generate_certificate(participant_data.get('name', 'Unknown'))
            
            # Create participant object
            participant = ParticipantData(
                name=participant_data.get('name', 'Unknown'),
                email=participant_data.get('email', ''),
                additional_info=participant_data,
                certificate_generated=True,
                certificate_data=certificate_data
            )
            
            participants.append(participant)
            
            # Use first certificate as preview
            if i == 0:
                preview_certificate = certificate_data
            
            # Store in database
            await db.participants.insert_one(participant.dict())
            
        except Exception as e:
            logging.error(f"Error processing participant {participant_data.get('name')}: {str(e)}")
            continue
    
    return CertificateGenerationResponse(
        participants=participants,
        total_count=len(participants),
        preview_certificate=preview_certificate
    )

@api_router.post("/send-sponsor-emails")
async def send_sponsor_emails(background_tasks: BackgroundTasks):
    """Send generated emails to all sponsors"""
    
    # Get all sponsors with generated emails
    sponsors = await db.sponsors.find({"email_status": "generated"}).to_list(None)
    
    if not sponsors:
        raise HTTPException(status_code=400, detail="No sponsors found with generated emails")
    
    # Add email sending to background tasks
    for sponsor in sponsors:
        background_tasks.add_task(send_sponsor_email, sponsor)
    
    return {"message": f"Sending emails to {len(sponsors)} sponsors", "count": len(sponsors)}

@api_router.post("/send-certificates")
async def send_certificates(background_tasks: BackgroundTasks):
    """Send certificates to all participants"""
    
    # Get all participants with generated certificates
    participants = await db.participants.find({"certificate_generated": True, "certificate_sent": False}).to_list(None)
    
    if not participants:
        raise HTTPException(status_code=400, detail="No participants found with generated certificates")
    
    # Add certificate sending to background tasks
    for participant in participants:
        background_tasks.add_task(send_participant_certificate, participant)
    
    return {"message": f"Sending certificates to {len(participants)} participants", "count": len(participants)}

async def send_sponsor_email(sponsor: dict):
    """Background task to send individual sponsor email"""
    try:
        subject = f"Partnership Opportunity with Hackfinity - {sponsor['organization']}"
        
        success = await send_email(
            sponsor['email'],
            subject,
            sponsor['email_content']
        )
        
        # Update status in database
        status = "sent" if success else "failed"
        await db.sponsors.update_one(
            {"id": sponsor["id"]},
            {"$set": {"email_status": status, "sent_at": datetime.utcnow()}}
        )
        
        # Add small delay to avoid rate limiting
        await asyncio.sleep(2)
        
    except Exception as e:
        logging.error(f"Error in background email task: {str(e)}")
        await db.sponsors.update_one(
            {"id": sponsor["id"]},
            {"$set": {"email_status": "failed", "error": str(e)}}
        )

async def send_participant_certificate(participant: dict):
    """Background task to send individual participant certificate"""
    try:
        success = await send_certificate_email(
            participant['email'],
            participant['name'],
            participant['certificate_data']
        )
        
        # Update status in database
        await db.participants.update_one(
            {"id": participant["id"]},
            {"$set": {"certificate_sent": success, "sent_at": datetime.utcnow()}}
        )
        
        # Add small delay to avoid rate limiting
        await asyncio.sleep(2)
        
    except Exception as e:
        logging.error(f"Error in background certificate task: {str(e)}")
        await db.participants.update_one(
            {"id": participant["id"]},
            {"$set": {"certificate_sent": False, "error": str(e)}}
        )

@api_router.get("/sponsors", response_model=List[SponsorData])
async def get_sponsors():
    """Get all sponsors with their email status"""
    sponsors = await db.sponsors.find().to_list(None)
    return [SponsorData(**sponsor) for sponsor in sponsors]

@api_router.get("/participants", response_model=List[ParticipantData])
async def get_participants():
    """Get all participants with their certificate status"""
    participants = await db.participants.find().to_list(None)
    return [ParticipantData(**participant) for participant in participants]

@api_router.get("/email-stats")
async def get_email_stats():
    """Get email sending statistics"""
    total = await db.sponsors.count_documents({})
    sent = await db.sponsors.count_documents({"email_status": "sent"})
    failed = await db.sponsors.count_documents({"email_status": "failed"})
    pending = await db.sponsors.count_documents({"email_status": "generated"})
    
    return {
        "total": total,
        "sent": sent,
        "failed": failed,
        "pending": pending
    }

@api_router.get("/certificate-stats")
async def get_certificate_stats():
    """Get certificate sending statistics"""
    total = await db.participants.count_documents({})
    sent = await db.participants.count_documents({"certificate_sent": True})
    failed = await db.participants.count_documents({"certificate_sent": False, "certificate_generated": True})
    pending = await db.participants.count_documents({"certificate_generated": True, "certificate_sent": False})
    
    return {
        "total": total,
        "sent": sent,
        "failed": failed,
        "pending": pending
    }

# Email Template Management
@api_router.post("/templates", response_model=EmailTemplate)
async def create_template(template: TemplateRequest):
    """Create a new email template"""
    template_obj = EmailTemplate(**template.dict())
    await db.templates.insert_one(template_obj.dict())
    return template_obj

@api_router.get("/templates", response_model=List[EmailTemplate])
async def get_templates():
    """Get all email templates"""
    templates = await db.templates.find().to_list(None)
    return [EmailTemplate(**template) for template in templates]

@api_router.get("/templates/{template_id}", response_model=EmailTemplate)
async def get_template(template_id: str):
    """Get a specific email template"""
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return EmailTemplate(**template)

@api_router.put("/templates/{template_id}", response_model=EmailTemplate)
async def update_template(template_id: str, template: TemplateRequest):
    """Update an email template"""
    template_dict = template.dict()
    template_dict["updated_at"] = datetime.utcnow()
    
    result = await db.templates.update_one(
        {"id": template_id},
        {"$set": template_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    updated_template = await db.templates.find_one({"id": template_id})
    return EmailTemplate(**updated_template)

@api_router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete an email template"""
    result = await db.templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}

# ===== ANALYTICS ENDPOINTS =====

@api_router.get("/analytics/sponsors")
async def get_sponsor_analytics():
    """Get comprehensive sponsor analytics with charts and insights"""
    try:
        analytics = await analytics_engine.get_sponsor_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error getting sponsor analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/certificates")
async def get_certificate_analytics():
    """Get comprehensive certificate analytics with charts and insights"""
    try:
        analytics = await analytics_engine.get_certificate_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error getting certificate analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/dashboard")
async def get_dashboard_analytics():
    """Get combined analytics for main dashboard"""
    try:
        sponsor_analytics = await analytics_engine.get_sponsor_analytics()
        certificate_analytics = await analytics_engine.get_certificate_analytics()
        
        dashboard = {
            "sponsors": sponsor_analytics,
            "certificates": certificate_analytics,
            "summary": {
                "total_sponsors": sponsor_analytics.get("overview", {}).get("total_sponsors", 0),
                "total_participants": certificate_analytics.get("overview", {}).get("total_participants", 0),
                "completion_rate": certificate_analytics.get("overview", {}).get("completion_rate", 0),
                "conversion_rate": sponsor_analytics.get("overview", {}).get("conversion_rate", 0)
            }
        }
        
        return dashboard
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ADVANCED TEMPLATE ENDPOINTS =====

@api_router.get("/templates/categories")
async def get_template_categories():
    """Get all template categories"""
    try:
        categories = await template_engine.get_template_categories()
        return [category.dict() for category in categories]
    except Exception as e:
        logger.error(f"Error getting template categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates/advanced")
async def get_advanced_templates(category_id: Optional[str] = None, template_type: Optional[str] = None):
    """Get advanced templates with filtering"""
    try:
        templates = await template_engine.get_templates(category_id, template_type)
        return [template.dict() for template in templates]
    except Exception as e:
        logger.error(f"Error getting advanced templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/templates/advanced")
async def create_advanced_template(template_data: dict):
    """Create a new advanced template"""
    try:
        template = AdvancedTemplate(**template_data)
        created_template = await template_engine.create_template(template)
        return created_template.dict()
    except Exception as e:
        logger.error(f"Error creating advanced template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/templates/advanced/{template_id}")
async def update_advanced_template(template_id: str, updates: dict):
    """Update an advanced template"""
    try:
        updated_template = await template_engine.update_template(template_id, updates)
        if not updated_template:
            raise HTTPException(status_code=404, detail="Template not found")
        return updated_template.dict()
    except Exception as e:
        logger.error(f"Error updating advanced template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/templates/advanced/{template_id}/duplicate")
async def duplicate_advanced_template(template_id: str, new_name: str = Form(...)):
    """Duplicate an advanced template"""
    try:
        duplicated_template = await template_engine.duplicate_template(template_id, new_name)
        if not duplicated_template:
            raise HTTPException(status_code=404, detail="Template not found")
        return duplicated_template.dict()
    except Exception as e:
        logger.error(f"Error duplicating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/templates/advanced/{template_id}/render")
async def render_advanced_template(template_id: str, variables: dict):
    """Render template with provided variables"""
    try:
        rendered = await template_engine.render_template(template_id, variables)
        return rendered
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/templates/advanced/{template_id}/preview")
async def preview_advanced_template(template_id: str, sample_data: Optional[dict] = None):
    """Preview template with sample data"""
    try:
        template_data = await db.templates.find_one({"id": template_id})
        if not template_data:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template = AdvancedTemplate(**template_data)
        preview = await template_engine.preview_template(template, sample_data)
        return preview
    except Exception as e:
        logger.error(f"Error previewing template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates/advanced/{template_id}/analytics")
async def get_template_analytics(template_id: str):
    """Get analytics for a specific template"""
    try:
        analytics = await template_engine.get_template_analytics(template_id)
        return analytics
    except Exception as e:
        logger.error(f"Error getting template analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== CERTIFICATE CUSTOMIZATION ENDPOINTS =====

@api_router.get("/certificates/templates")
async def get_certificate_templates(category: Optional[str] = None):
    """Get available certificate templates"""
    try:
        templates = await certificate_customizer.get_certificate_templates(category)
        return [template.dict() for template in templates]
    except Exception as e:
        logger.error(f"Error getting certificate templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/certificates/templates")
async def create_certificate_template(template_data: dict):
    """Create a new certificate template"""
    try:
        template = CertificateTemplate(**template_data)
        created_template = await certificate_customizer.create_template(template)
        return created_template.dict()
    except Exception as e:
        logger.error(f"Error creating certificate template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/certificates/templates/{template_id}")
async def update_certificate_template(template_id: str, updates: dict):
    """Update a certificate template"""
    try:
        updated_template = await certificate_customizer.update_template(template_id, updates)
        if not updated_template:
            raise HTTPException(status_code=404, detail="Template not found")
        return updated_template.dict()
    except Exception as e:
        logger.error(f"Error updating certificate template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/certificates/templates/{template_id}/duplicate")
async def duplicate_certificate_template(template_id: str, new_name: str = Form(...)):
    """Duplicate a certificate template"""
    try:
        duplicated_template = await certificate_customizer.duplicate_template(template_id, new_name)
        if not duplicated_template:
            raise HTTPException(status_code=404, detail="Template not found")
        return duplicated_template.dict()
    except Exception as e:
        logger.error(f"Error duplicating certificate template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/certificates/generate")
async def generate_certificate(
    template_id: str = Form(...),
    participant_data: str = Form(...),
    format: str = Form("pdf")
):
    """Generate a certificate with custom data"""
    try:
        data = json.loads(participant_data)
        certificate_bytes = await certificate_customizer.generate_certificate(template_id, data, format)
        
        # Return as base64 for easy frontend handling
        import base64
        certificate_b64 = base64.b64encode(certificate_bytes).decode('utf-8')
        
        return {
            "certificate": certificate_b64,
            "format": format,
            "filename": f"certificate_{data.get('participant_name', 'participant')}.{format.lower()}"
        }
    except Exception as e:
        logger.error(f"Error generating certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/certificates/templates/{template_id}/preview")
async def preview_certificate_template(template_id: str, sample_data: Optional[dict] = None):
    """Preview certificate template"""
    try:
        template_data = await db.certificate_templates.find_one({"id": template_id})
        if not template_data:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template = CertificateTemplate(**template_data)
        preview_b64 = await certificate_customizer.preview_certificate(template, sample_data)
        
        return {
            "preview": preview_b64,
            "format": "png"
        }
    except Exception as e:
        logger.error(f"Error previewing certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/certificates/templates/{template_id}/analytics")
async def get_certificate_template_analytics(template_id: str):
    """Get analytics for a certificate template"""
    try:
        analytics = await certificate_customizer.get_certificate_analytics(template_id)
        return analytics
    except Exception as e:
        logger.error(f"Error getting certificate template analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/certificates/bulk-generate")
async def bulk_generate_certificates(
    template_id: str = Form(...),
    participants_data: str = Form(...),
    format: str = Form("pdf")
):
    """Generate certificates for multiple participants"""
    try:
        participants = json.loads(participants_data)
        certificates = []
        
        for participant in participants:
            certificate_bytes = await certificate_customizer.generate_certificate(template_id, participant, format)
            certificate_b64 = base64.b64encode(certificate_bytes).decode('utf-8')
            
            certificates.append({
                "participant_name": participant.get("participant_name", "Unknown"),
                "certificate": certificate_b64,
                "format": format
            })
        
        return {
            "certificates": certificates,
            "total_generated": len(certificates)
        }
    except Exception as e:
        logger.error(f"Error bulk generating certificates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENHANCED CHART ENDPOINTS =====

@api_router.get("/charts/sponsor-funnel")
async def get_sponsor_funnel_chart():
    """Get sponsor conversion funnel chart"""
    try:
        sponsors = await db.sponsors.find({}).to_list(length=None)
        
        # Create funnel data
        total_contacts = len(sponsors)
        opened_emails = len([s for s in sponsors if s.get('email_opened', False)])
        responded = len([s for s in sponsors if s.get('response_received', False)])
        confirmed = len([s for s in sponsors if s.get('status') == 'confirmed'])
        
        # Create Plotly funnel chart
        fig = go.Figure(go.Funnel(
            y=["Contacted", "Opened Email", "Responded", "Confirmed"],
            x=[total_contacts, opened_emails, responded, confirmed],
            textinfo="value+percent initial",
            marker_color=["#6366f1", "#8b5cf6", "#10b981", "#059669"]
        ))
        
        fig.update_layout(
            title="Sponsor Conversion Funnel",
            font_size=14,
            height=400
        )
        
        return {"chart": fig.to_json()}
    except Exception as e:
        logger.error(f"Error creating sponsor funnel chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/charts/participant-journey")
async def get_participant_journey_chart():
    """Get participant journey timeline chart"""
    try:
        participants = await db.participants.find({}).to_list(length=None)
        
        # Create journey stages
        registered = len(participants)
        started = len([p for p in participants if p.get('started', False)])
        submitted = len([p for p in participants if p.get('submitted', False)])
        completed = len([p for p in participants if p.get('status') == 'completed'])
        
        # Create sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=["Registered", "Started", "Submitted", "Completed"],
                color=["#6366f1", "#8b5cf6", "#10b981", "#059669"]
            ),
            link=dict(
                source=[0, 1, 2],
                target=[1, 2, 3],
                value=[started, submitted, completed]
            )
        )])
        
        fig.update_layout(
            title_text="Participant Journey Flow",
            font_size=14,
            height=400
        )
        
        return {"chart": fig.to_json()}
    except Exception as e:
        logger.error(f"Error creating participant journey chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced endpoints for advanced charts
@app.get("/api/charts/advanced/{chart_type}")
async def get_advanced_chart(chart_type: str, data_source: str = "sponsors"):
    """Get advanced modern chart visualizations"""
    try:
        chart_data = await analytics_service.get_advanced_charts(chart_type, data_source)
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/3d-scatter")
async def get_3d_scatter_chart():
    """Get 3D scatter plot for engagement analysis"""
    try:
        sponsors = await db.sponsors.find({}).to_list(length=None)
        chart_data = await analytics_service.get_advanced_charts("3d_scatter", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/treemap")
async def get_treemap_chart():
    """Get treemap visualization for hierarchical data"""
    try:
        chart_data = await analytics_service.get_advanced_charts("treemap", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/sunburst")
async def get_sunburst_chart():
    """Get sunburst chart for multi-level categorization"""
    try:
        chart_data = await analytics_service.get_advanced_charts("sunburst", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/sankey")
async def get_sankey_diagram():
    """Get Sankey diagram for flow visualization"""
    try:
        chart_data = await analytics_service.get_advanced_charts("sankey", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/radar")
async def get_radar_chart():
    """Get radar chart for multi-dimensional analysis"""
    try:
        chart_data = await analytics_service.get_advanced_charts("radar", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/waterfall")
async def get_waterfall_chart():
    """Get waterfall chart for cumulative analysis"""
    try:
        chart_data = await analytics_service.get_advanced_charts("waterfall", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/gauge")
async def get_gauge_chart():
    """Get gauge chart for KPI visualization"""
    try:
        chart_data = await analytics_service.get_advanced_charts("gauge", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/parallel-coordinates")
async def get_parallel_coordinates():
    """Get parallel coordinates plot for multi-dimensional data"""
    try:
        chart_data = await analytics_service.get_advanced_charts("parallel_coordinates", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/charts/animated-bar")
async def get_animated_bar_chart():
    """Get animated bar chart showing progress over time"""
    try:
        chart_data = await analytics_service.get_advanced_charts("animated_bar", "sponsors")
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Enhanced template management endpoints
@app.get("/api/templates/builder-config")
async def get_template_builder_config():
    """Get configuration for the advanced template builder"""
    try:
        config = await template_engine.get_template_builder_config()
        return JSONResponse(content=config)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/templates/advanced")
async def create_advanced_template(template_data: dict):
    """Create a new advanced template"""
    try:
        template = await template_engine.create_advanced_template(template_data)
        return JSONResponse(content=template.dict())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/templates/advanced")
async def get_advanced_templates(category: str = None, search: str = None):
    """Get advanced templates with filtering"""
    try:
        query = {}
        if category:
            query["category_id"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search]}}
            ]
        
        templates = await db.advanced_templates.find(query).to_list(length=None)
        return JSONResponse(content=templates)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/templates/advanced/{template_id}")
async def get_advanced_template(template_id: str):
    """Get a specific advanced template"""
    try:
        template = await db.advanced_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return JSONResponse(content=template)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.put("/api/templates/advanced/{template_id}")
async def update_advanced_template(template_id: str, template_data: dict):
    """Update an advanced template"""
    try:
        result = await db.advanced_templates.update_one(
            {"id": template_id},
            {"$set": {**template_data, "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        updated_template = await db.advanced_templates.find_one({"id": template_id})
        return JSONResponse(content=updated_template)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.delete("/api/templates/advanced/{template_id}")
async def delete_advanced_template(template_id: str):
    """Delete an advanced template"""
    try:
        result = await db.advanced_templates.delete_one({"id": template_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/templates/duplicate/{template_id}")
async def duplicate_template(template_id: str, new_name: str):
    """Duplicate an existing template"""
    try:
        original = await db.advanced_templates.find_one({"id": template_id})
        if not original:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create duplicate with new ID and name
        duplicate = original.copy()
        duplicate["id"] = str(uuid.uuid4())
        duplicate["name"] = new_name
        duplicate["created_at"] = datetime.utcnow()
        duplicate["updated_at"] = datetime.utcnow()
        
        await db.advanced_templates.insert_one(duplicate)
        return JSONResponse(content=duplicate)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/templates/analytics/{template_id}")
async def get_template_analytics(template_id: str):
    """Get analytics for a specific template"""
    try:
        analytics = await template_service.get_template_analytics(template_id)
        return JSONResponse(content=analytics)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/templates/export/{template_id}")
async def export_template(template_id: str, format: str = "json"):
    """Export template in specified format"""
    try:
        template = await db.advanced_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if format == "json":
            return JSONResponse(content=template)
        else:
            # Could implement other formats like HTML, PDF, etc.
            return {"error": f"Format {format} not supported yet"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Complete certificate endpoints
@app.get("/api/certificates/builder-config")
async def get_certificate_builder_config():
    """Get configuration for certificate builder"""
    try:
        config = await certificate_service.create_certificate_builder_config()
        return JSONResponse(content=config)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/certificates/templates")
async def get_certificate_templates(category: str = None):
    """Get certificate templates"""
    try:
        query = {}
        if category:
            query["category"] = category
        templates = await db.certificate_templates.find(query).to_list(length=None)
        return JSONResponse(content=templates)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/certificates/templates")
async def create_certificate_template(template_data: dict):
    """Create new certificate template"""
    try:
        template = await certificate_service.create_certificate_template(template_data)
        return JSONResponse(content=template.dict())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/certificates/templates/{template_id}")
async def get_certificate_template(template_id: str):
    """Get specific certificate template"""
    try:
        template = await db.certificate_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return JSONResponse(content=template)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.put("/api/certificates/templates/{template_id}")
async def update_certificate_template(template_id: str, template_data: dict):
    """Update certificate template"""
    try:
        result = await db.certificate_templates.update_one(
            {"id": template_id},
            {"$set": {**template_data, "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        updated_template = await db.certificate_templates.find_one({"id": template_id})
        return JSONResponse(content=updated_template)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/certificates/generate")
async def generate_certificate(
    template_id: str = Form(...),
    participant_data: str = Form(...),
    format: str = Form("pdf")
):
    """Generate certificate"""
    try:
        data = json.loads(participant_data)
        certificate = await certificate_service.generate_certificate(template_id, data, format)
        return {"certificate": certificate, "format": format}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/certificates/generate-batch")
async def generate_certificate_batch(
    template_id: str = Form(...),
    participants: str = Form(...),
    format: str = Form("pdf")
):
    """Generate certificates in batch"""
    try:
        participant_list = json.loads(participants)
        results = await certificate_service.generate_certificate_batch(template_id, participant_list, format)
        return {"results": results, "total": len(results)}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/certificates/preview/{template_id}")
async def preview_certificate(template_id: str, sample_data: dict = None):
    """Preview certificate template"""
    try:
        if not sample_data:
            sample_data = {
                "participant_name": "John Doe",
                "event_name": "Hackfinity 2025",
                "date": "July 4, 2025"
            }
        preview = await certificate_service.preview_certificate(template_id, sample_data)
        return {"preview": preview}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Email scheduling endpoints
@api_router.post("/schedule-email", response_model=dict)
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
        await db.scheduled_emails.insert_one(email_obj.dict())
        
        return {
            "message": "Email scheduled successfully",
            "email_id": email_obj.id,
            "scheduled_for": f"{scheduled_email.schedule_date} {scheduled_email.schedule_time}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error scheduling email: {str(e)}")

@api_router.post("/schedule-bulk-emails")
async def schedule_bulk_emails(bulk_schedule: BulkEmailSchedule):
    """Schedule emails for multiple recipients"""
    try:
        scheduled_email_ids = []
        
        for email in bulk_schedule.emails:
            email_create = ScheduledEmailCreate(
                recipient_email=email,
                subject=bulk_schedule.subject,
                content=bulk_schedule.content,
                schedule_date=bulk_schedule.schedule_date,
                schedule_time=bulk_schedule.schedule_time,
                template_type=bulk_schedule.template_type
            )
            
            # Parse schedule date and time
            schedule_datetime = datetime.fromisoformat(bulk_schedule.schedule_date)
            
            # Create scheduled email object
            email_obj = ScheduledEmail(
                recipient_email=email,
                subject=bulk_schedule.subject,
                content=bulk_schedule.content,
                schedule_date=schedule_datetime,
                schedule_time=bulk_schedule.schedule_time,
                template_type=bulk_schedule.template_type
            )
            
            # Store in memory and database
            scheduled_emails[email_obj.id] = email_obj
            await db.scheduled_emails.insert_one(email_obj.dict())
            scheduled_email_ids.append(email_obj.id)
        
        return {
            "message": f"Scheduled {len(bulk_schedule.emails)} emails successfully",
            "scheduled_email_ids": scheduled_email_ids,
            "scheduled_for": f"{bulk_schedule.schedule_date} {bulk_schedule.schedule_time}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error scheduling bulk emails: {str(e)}")

@api_router.get("/scheduled-emails")
async def get_scheduled_emails():
    """Get all scheduled emails"""
    try:
        emails = await db.scheduled_emails.find().to_list(None)
        return [ScheduledEmail(**email) for email in emails]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scheduled emails: {str(e)}")

@api_router.put("/scheduled-emails/{email_id}")
async def update_scheduled_email(email_id: str, updates: dict):
    """Update a scheduled email"""
    try:
        result = await db.scheduled_emails.update_one(
            {"id": email_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Scheduled email not found")
        
        # Update in memory
        if email_id in scheduled_emails:
            for key, value in updates.items():
                setattr(scheduled_emails[email_id], key, value)
        
        return {"message": "Scheduled email updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating scheduled email: {str(e)}")

@api_router.delete("/scheduled-emails/{email_id}")
async def cancel_scheduled_email(email_id: str):
    """Cancel a scheduled email"""
    try:
        result = await db.scheduled_emails.delete_one({"id": email_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Scheduled email not found")
        
        # Remove from memory
        if email_id in scheduled_emails:
            del scheduled_emails[email_id]
        
        return {"message": "Scheduled email cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error cancelling scheduled email: {str(e)}")

# Drag and drop Excel upload with enhanced processing
@api_router.post("/upload-excel-drag-drop")
async def upload_excel_drag_drop(
    file: UploadFile = File(...),
    upload_type: str = Form("sponsors"),  # sponsors or participants
    auto_process: bool = Form(True)
):
    """Enhanced drag and drop Excel/CSV upload with automatic processing"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Read file content
        file_content = await file.read()
        
        # Process the file with enhanced mapping
        data = await process_excel_file_enhanced(file_content, file.filename)
        
        results = {
            "filename": file.filename,
            "total_records": len(data),
            "upload_type": upload_type,
            "processed_data": data[:5],  # Preview first 5 records
            "column_mapping": await detect_column_mapping(data[0] if data else {}),
            "data_quality": await analyze_data_quality(data)
        }
        
        if auto_process and upload_type == "sponsors":
            # Auto-generate emails for sponsors
            sponsors = []
            for item in data:
                sponsor = SponsorData(
                    name=item.get('name', 'Unknown'),
                    email=item.get('email', ''),
                    organization=item.get('organization', 'Unknown'),
                    additional_info=item,
                    email_status="uploaded"
                )
                sponsors.append(sponsor)
                await db.sponsors.insert_one(sponsor.dict())
            
            results["sponsors_created"] = len(sponsors)
            
        elif auto_process and upload_type == "participants":
            # Auto-create participant records
            participants = []
            for item in data:
                participant = ParticipantData(
                    name=item.get('name', 'Unknown'),
                    email=item.get('email', ''),
                    additional_info=item
                )
                participants.append(participant)
                await db.participants.insert_one(participant.dict())
            
            results["participants_created"] = len(participants)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

async def process_excel_file_enhanced(file_content: bytes, filename: str) -> List[dict]:
    """Enhanced Excel/CSV file processing with better column detection"""
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError("Unsupported file format")
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Enhanced column mapping
        column_mapping = {
            'name': ['name', 'full name', 'participant name', 'sponsor name', 'contact name', 'first name'],
            'email': ['email', 'email address', 'contact email', 'e-mail'],
            'organization': ['organization', 'company', 'org', 'business', 'corporation'],
            'phone': ['phone', 'phone number', 'contact number', 'mobile'],
            'title': ['title', 'position', 'job title', 'role'],
            'industry': ['industry', 'sector', 'domain'],
            'location': ['location', 'city', 'country', 'address']
        }
        
        # Process data with enhanced mapping
        data = []
        for _, row in df.iterrows():
            item = {}
            
            # Map columns using enhanced logic
            for standard_field, possible_names in column_mapping.items():
                for col in df.columns:
                    if any(possible_name in col for possible_name in possible_names):
                        item[standard_field] = str(row[col]) if pd.notna(row[col]) else ''
                        break
            
            # Add all original columns as additional info
            item['original_data'] = {col: str(row[col]) if pd.notna(row[col]) else '' for col in df.columns}
            
            # Ensure required fields have defaults
            item.setdefault('name', 'Unknown')
            item.setdefault('email', '')
            item.setdefault('organization', 'Unknown')
            
            data.append(item)
        
        return data
        
    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")

async def detect_column_mapping(sample_row: dict) -> dict:
    """Detect and suggest column mappings for uploaded data"""
    mapping = {
        "detected_fields": [],
        "suggested_mapping": {},
        "confidence_score": 0.0
    }
    
    if not sample_row:
        return mapping
    
    field_patterns = {
        'name': ['name', 'full', 'participant', 'sponsor', 'contact'],
        'email': ['email', 'mail', '@'],
        'organization': ['org', 'company', 'business', 'corp'],
        'phone': ['phone', 'mobile', 'contact'],
        'title': ['title', 'position', 'job', 'role']
    }
    
    for key, value in sample_row.items():
        key_lower = key.lower()
        for field, patterns in field_patterns.items():
            if any(pattern in key_lower for pattern in patterns):
                mapping["suggested_mapping"][key] = field
                mapping["detected_fields"].append(field)
                break
    
    mapping["confidence_score"] = len(mapping["detected_fields"]) / len(field_patterns)
    return mapping

async def analyze_data_quality(data: List[dict]) -> dict:
    """Analyze data quality and provide insights"""
    if not data:
        return {"quality_score": 0, "issues": ["No data provided"]}
    
    total_records = len(data)
    issues = []
    valid_emails = 0
    missing_names = 0
    missing_organizations = 0
    
    for record in data:
        # Check email validity
        email = record.get('email', '')
        if email and '@' in email and '.' in email:
            valid_emails += 1
        elif not email:
            issues.append("Missing email addresses")
        
        # Check for missing names
        if not record.get('name') or record.get('name') == 'Unknown':
            missing_names += 1
        
        # Check for missing organizations
        if not record.get('organization') or record.get('organization') == 'Unknown':
            missing_organizations += 1
    
    # Calculate quality score
    email_score = (valid_emails / total_records) * 0.4
    name_score = ((total_records - missing_names) / total_records) * 0.3
    org_score = ((total_records - missing_organizations) / total_records) * 0.3
    quality_score = email_score + name_score + org_score
    
    return {
        "quality_score": round(quality_score * 100, 2),
        "total_records": total_records,
        "valid_emails": valid_emails,
        "missing_names": missing_names,
        "missing_organizations": missing_organizations,
        "issues": list(set(issues)) if issues else ["No major issues detected"],
        "recommendations": [
            "Verify email addresses before sending" if valid_emails < total_records else None,
            "Add missing names for better personalization" if missing_names > 0 else None,
            "Include organization information for better targeting" if missing_organizations > 0 else None
        ]
    }

# Enhanced analytics for scheduled emails
@api_router.get("/analytics/scheduled-emails")
async def get_scheduled_email_analytics():
    """Get analytics for scheduled emails"""
    try:
        scheduled = await db.scheduled_emails.find().to_list(None)
        
        # Calculate metrics
        total_scheduled = len(scheduled)
        pending = len([e for e in scheduled if e.get('status') == 'pending'])
        sent = len([e for e in scheduled if e.get('status') == 'sent'])
        failed = len([e for e in scheduled if e.get('status') == 'failed'])
        
        # Group by date
        dates = {}
        for email in scheduled:
            date_str = email.get('schedule_date', '').split('T')[0] if email.get('schedule_date') else 'Unknown'
            dates[date_str] = dates.get(date_str, 0) + 1
        
        # Group by type
        types = {}
        for email in scheduled:
            email_type = email.get('template_type', 'unknown')
            types[email_type] = types.get(email_type, 0) + 1
        
        return {
            "overview": {
                "total_scheduled": total_scheduled,
                "pending": pending,
                "sent": sent,
                "failed": failed,
                "success_rate": round((sent / total_scheduled * 100) if total_scheduled > 0 else 0, 2)
            },
            "by_date": dates,
            "by_type": types,
            "upcoming": [
                email for email in scheduled 
                if email.get('status') == 'pending' and 
                datetime.fromisoformat(email.get('schedule_date', '').replace('Z', '+00:00')) > datetime.now()
            ][:10]  # Next 10 upcoming emails
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting email analytics: {str(e)}")

# File upload validation and preview
@api_router.post("/validate-excel-upload")
async def validate_excel_upload(file: UploadFile = File(...)):
    """Validate Excel/CSV file before processing"""
    try:
        # Check file size (max 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
        
        # Reset file pointer
        await file.seek(0)
        file_content = await file.read()
        
        # Validate file structure
        data = await process_excel_file_enhanced(file_content, file.filename)
        
        if not data:
            raise HTTPException(status_code=400, detail="File appears to be empty")
        
        # Analyze file structure
        column_analysis = await detect_column_mapping(data[0] if data else {})
        quality_analysis = await analyze_data_quality(data)
        
        return {
            "valid": True,
            "filename": file.filename,
            "total_records": len(data),
            "preview_data": data[:3],  # First 3 records
            "column_analysis": column_analysis,
            "quality_analysis": quality_analysis,
            "recommendations": [
                "File structure looks good" if quality_analysis["quality_score"] > 80 else "Consider improving data quality",
                f"Detected {len(column_analysis['detected_fields'])} standard fields",
                "Ready for processing" if quality_analysis["quality_score"] > 60 else "Manual review recommended"
            ]
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "recommendations": [
                "Check file format (CSV, XLSX, XLS only)",
                "Ensure file has proper headers",
                "Verify data structure and formatting"
            ]
        }

# Include the API router
app.include_router(api_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scheduler on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    try:
        # Load existing scheduled emails from database
        existing_emails = await db.scheduled_emails.find({"status": "pending"}).to_list(None)
        for email_data in existing_emails:
            email_obj = ScheduledEmail(**email_data)
            scheduled_emails[email_obj.id] = email_obj
        
        # Start the email scheduler
        start_email_scheduler()
        
        logging.info(f"Application started successfully. Loaded {len(existing_emails)} scheduled emails.")
        print("🚀 Hackfinity Platform started successfully!")
        print(f"📧 Email scheduler running with {len(existing_emails)} scheduled emails")
        print("🌐 Server running at http://localhost:8000")
        print("📊 API documentation available at http://localhost:8000/docs")
        
    except Exception as e:
        logging.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logging.info("Application shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)