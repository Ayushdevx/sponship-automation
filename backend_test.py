#!/usr/bin/env python3
import requests
import pandas as pd
import io
import os
import time
import unittest
import json
from dotenv import load_dotenv

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL not found in environment variables")

# Ensure the URL ends with /api for all API calls
API_URL = f"{BACKEND_URL}/api"

class HackfinityBackendTests(unittest.TestCase):
    """Test suite for Hackfinity Communication Platform backend APIs"""
    
    def setUp(self):
        """Set up test data"""
        # Create a sample CSV file with sponsor data
        self.sponsors_data = [
            {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "organization": "Tech Innovations Inc.",
                "role": "CTO",
                "industry": "Technology"
            },
            {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@example.com",
                "organization": "Future Finance",
                "role": "Director of Partnerships",
                "industry": "FinTech"
            },
            {
                "name": "Michael Chen",
                "email": "michael.chen@example.com",
                "organization": "HealthTech Solutions",
                "role": "CEO",
                "industry": "Healthcare"
            }
        ]
        
        # Create a DataFrame and save to a CSV buffer
        self.df = pd.DataFrame(self.sponsors_data)
        self.csv_buffer = io.StringIO()
        self.df.to_csv(self.csv_buffer, index=False)
        self.csv_content = self.csv_buffer.getvalue()
        
        # Save to a temporary file
        with open('/tmp/test_sponsors.csv', 'w') as f:
            f.write(self.csv_content)
        
        print(f"Testing against backend API at: {API_URL}")
    
    def test_1_root_endpoint(self):
        """Test the root API endpoint"""
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print("✅ Root endpoint test passed")
    
    def test_2_upload_sponsors(self):
        """Test uploading sponsors CSV file and generating emails"""
        # Open the file in binary mode
        with open('/tmp/test_sponsors.csv', 'rb') as f:
            files = {'file': ('test_sponsors.csv', f, 'text/csv')}
            response = requests.post(f"{API_URL}/upload-sponsors", files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure
        self.assertIn("sponsors", data)
        self.assertIn("total_count", data)
        self.assertIn("preview_email", data)
        
        # Verify sponsor count
        self.assertEqual(data["total_count"], len(self.sponsors_data))
        
        # Verify email content was generated
        self.assertTrue(len(data["preview_email"]) > 0)
        
        # Verify all sponsors have email content
        for sponsor in data["sponsors"]:
            self.assertIn("email_content", sponsor)
            self.assertIsNotNone(sponsor["email_content"])
            self.assertEqual(sponsor["email_status"], "generated")
        
        print(f"✅ Upload sponsors test passed - {data['total_count']} sponsors processed")
        
        # Store sponsor IDs for later tests
        self.sponsor_ids = [sponsor["id"] for sponsor in data["sponsors"]]
    
    def test_3_get_sponsors(self):
        """Test retrieving sponsor data"""
        response = requests.get(f"{API_URL}/sponsors")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify we have sponsors in the database
        self.assertTrue(len(data) > 0)
        
        # Verify sponsor data structure
        for sponsor in data:
            self.assertIn("id", sponsor)
            self.assertIn("name", sponsor)
            self.assertIn("email", sponsor)
            self.assertIn("organization", sponsor)
            self.assertIn("email_content", sponsor)
            self.assertIn("email_status", sponsor)
        
        print(f"✅ Get sponsors test passed - {len(data)} sponsors retrieved")
    
    def test_4_email_stats(self):
        """Test retrieving email statistics"""
        response = requests.get(f"{API_URL}/email-stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify stats structure
        self.assertIn("total", data)
        self.assertIn("sent", data)
        self.assertIn("failed", data)
        self.assertIn("pending", data)
        
        # Verify total matches our upload
        self.assertTrue(data["total"] >= len(self.sponsors_data))
        
        # Verify pending count (should match our upload since we haven't sent emails yet)
        self.assertTrue(data["pending"] >= len(self.sponsors_data))
        
        print(f"✅ Email stats test passed - Total: {data['total']}, Pending: {data['pending']}")
    
    def test_5_send_sponsor_emails(self):
        """Test sending sponsor emails"""
        response = requests.post(f"{API_URL}/send-sponsor-emails")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure
        self.assertIn("message", data)
        self.assertIn("count", data)
        
        # Verify count is at least our upload count
        self.assertTrue(data["count"] >= len(self.sponsors_data))
        
        print(f"✅ Send sponsor emails test passed - {data['count']} emails queued for sending")
        
        # Wait a moment for background tasks to process
        print("Waiting for background email tasks to process...")
        time.sleep(5)
    
    def test_6_verify_email_status(self):
        """Verify email status after sending"""
        response = requests.get(f"{API_URL}/email-stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Print current stats
        print(f"Email Stats: Total: {data['total']}, Sent: {data['sent']}, Failed: {data['failed']}, Pending: {data['pending']}")
        
        # Check if emails were processed (either sent or failed)
        self.assertTrue(data["sent"] > 0 or data["failed"] > 0)
        
        # Get detailed sponsor data to check individual status
        response = requests.get(f"{API_URL}/sponsors")
        self.assertEqual(response.status_code, 200)
        sponsors = response.json()
        
        # Count statuses
        statuses = {"sent": 0, "failed": 0, "generated": 0}
        for sponsor in sponsors:
            if sponsor["email_status"] in statuses:
                statuses[sponsor["email_status"]] += 1
        
        print(f"Sponsor Email Statuses: {statuses}")
        
        # Verify some emails were processed
        self.assertTrue(statuses["sent"] > 0 or statuses["failed"] > 0)
        
        print("✅ Email status verification test passed")

def run_tests():
    """Run all tests in order"""
    # Create a test suite with tests in specific order
    suite = unittest.TestSuite()
    suite.addTest(HackfinityBackendTests('test_1_root_endpoint'))
    suite.addTest(HackfinityBackendTests('test_2_upload_sponsors'))
    suite.addTest(HackfinityBackendTests('test_3_get_sponsors'))
    suite.addTest(HackfinityBackendTests('test_4_email_stats'))
    suite.addTest(HackfinityBackendTests('test_5_send_sponsor_emails'))
    suite.addTest(HackfinityBackendTests('test_6_verify_email_status'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ All backend tests passed successfully!")
    else:
        print("\n❌ Some tests failed. See details above.")
    
    # Exit with appropriate status code
    exit(0 if success else 1)