#!/usr/bin/env python3
"""
Ultra minimal FastAPI server for testing
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import json

# Create FastAPI app
app = FastAPI()

# CORS middleware with very permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🌐 Incoming request: {request.method} {request.url}")
    print(f"🌐 Headers: {dict(request.headers)}")
    response = await call_next(request)
    print(f"🌐 Response status: {response.status_code}")
    return response

@app.get("/test", response_class=HTMLResponse)
async def serve_test_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backend Connection Test</title>
    </head>
    <body>
        <h1>Backend Connection Test (Served from Backend)</h1>
        <button onclick="testConnection()">Test Connection</button>
        <button onclick="testScheduleEmail()">Test Schedule Email</button>
        <div id="result"></div>

        <script>
            async function testConnection() {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = 'Testing connection...';
                
                try {
                    const response = await fetch('/api/test-connection');
                    const data = await response.json();
                    resultDiv.innerHTML = `<p style="color: green;">✅ Connection successful: ${JSON.stringify(data)}</p>`;
                } catch (error) {
                    resultDiv.innerHTML = `<p style="color: red;">❌ Connection failed: ${error.message}</p>`;
                    console.error('Connection error:', error);
                }
            }

            async function testScheduleEmail() {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = 'Testing email scheduling...';
                
                const emailData = {
                    recipient_email: "test@example.com",
                    subject: "Test Email",
                    content: "This is a test",
                    schedule_date: "2025-07-06",
                    schedule_time: "10:00",
                    template_type: "sponsor",
                    priority: "normal",
                    recurring: false
                };
                
                try {
                    const response = await fetch('/api/schedule-email', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(emailData)
                    });
                    const data = await response.json();
                    resultDiv.innerHTML = `<p style="color: green;">✅ Email scheduling successful: ${JSON.stringify(data)}</p>`;
                } catch (error) {
                    resultDiv.innerHTML = `<p style="color: red;">❌ Email scheduling failed: ${error.message}</p>`;
                    console.error('Email scheduling error:', error);
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/")
async def root():
    return {"message": "Server is running!"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "server": "minimal"}

@app.get("/api/sponsors")
async def get_sponsors():
    return []

@app.get("/api/participants") 
async def get_participants():
    return []

@app.get("/api/templates")
async def get_templates():
    return []

@app.get("/api/test-connection")
async def test_connection():
    return {"status": "connected", "message": "Frontend can reach backend", "timestamp": "2025-07-05"}

@app.options("/api/schedule-email")
async def options_schedule_email():
    return {"message": "CORS preflight OK"}

@app.post("/api/schedule-email")
async def schedule_email(request: Request):
    try:
        print(f"🔍 DEBUG: Received request to /api/schedule-email")
        print(f"🔍 DEBUG: Request method: {request.method}")
        print(f"🔍 DEBUG: Request headers: {dict(request.headers)}")
        
        # Try to get the body as JSON
        body = await request.body()
        print(f"🔍 DEBUG: Raw body: {body}")
        
        if body:
            try:
                data = json.loads(body.decode('utf-8'))
                print(f"🔍 DEBUG: Parsed JSON data: {data}")
            except json.JSONDecodeError as e:
                print(f"❌ DEBUG: JSON decode error: {e}")
                data = {}
        else:
            data = {}
        
        print(f"✅ DEBUG: Email schedule request processed successfully")
        return {"message": "Email scheduled successfully", "data": data, "debug": "Backend received the request"}
    except Exception as e:
        print(f"❌ DEBUG: Error in schedule_email: {e}")
        return {"error": str(e), "message": "Error processing request"}

@app.get("/api/scheduled-emails")
async def get_scheduled_emails():
    return []

@app.get("/api/analytics")
async def get_analytics():
    return {
        "sponsor_stats": {"total": 0, "sent": 0, "failed": 0, "pending": 0},
        "certificate_stats": {"total": 0, "sent": 0, "failed": 0, "pending": 0}
    }

if __name__ == "__main__":
    print("Starting ultra minimal server...")
    print("Backend URL will be: http://0.0.0.0:8000")
    print("Frontend should connect to: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
