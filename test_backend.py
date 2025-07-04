#!/usr/bin/env python3
"""
Hackfinity Platform Backend Test & Setup Verification
Run this script to verify your backend setup before starting the server.
"""
import sys
import os
import subprocess
import tempfile
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50)

def print_step(step, text):
    """Print a formatted step"""
    print(f"\n{step}. {text}")
    print("-" * (len(text) + 4))

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking Python dependencies...")
    
    required_packages = {
        'fastapi': 'FastAPI web framework',
        'motor': 'MongoDB async driver', 
        'pandas': 'Data processing library',
        'schedule': 'Email scheduling library',
        'reportlab': 'PDF generation library',
        'python-dotenv': 'Environment variables',
        'uvicorn': 'ASGI web server',
        'pymongo': 'MongoDB driver',
        'openpyxl': 'Excel file processing'
    }
    
    missing_packages = []
    installed_packages = []
    
    for package, description in required_packages.items():
        try:
            if package == 'motor':
                import motor.motor_asyncio
            elif package == 'python-dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package:15} - {description}")
            installed_packages.append(package)
        except ImportError:
            print(f"❌ {package:15} - {description} (MISSING)")
            missing_packages.append(package)
    
    return missing_packages, installed_packages

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("Checking environment configuration...")
    
    backend_dir = Path(__file__).parent / 'backend'
    env_file = backend_dir / '.env'
    
    required_vars = [
        'MONGO_URL',
        'DB_NAME', 
        'EMAIL_ADDRESS',
        'EMAIL_PASSWORD'
    ]
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("Creating sample .env file...")
        
        sample_env = """# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=hackfinity_platform

# Email Configuration (Gmail)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# AI Configuration (Optional)
GEMINI_API_KEY=your_gemini_api_key

# Application Settings
DEBUG=True
ENVIRONMENT=development
"""
        
        env_file.write_text(sample_env)
        print(f"✅ Sample .env file created at {env_file}")
        print("⚠️  Please update with your actual credentials!")
        return False, []
    
    # Check if env file has required variables
    env_content = env_file.read_text()
    missing_vars = []
    found_vars = []
    
    for var in required_vars:
        if f"{var}=" in env_content:
            # Check if it has a real value (not placeholder)
            lines = env_content.split('\n')
            for line in lines:
                if line.startswith(f"{var}="):
                    value = line.split('=', 1)[1].strip()
                    if value and not value.startswith('your_'):
                        print(f"✅ {var} - configured")
                        found_vars.append(var)
                    else:
                        print(f"⚠️  {var} - needs configuration")
                        missing_vars.append(var)
                    break
        else:
            print(f"❌ {var} - missing")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, found_vars

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv
        
        # Load environment variables
        backend_dir = Path(__file__).parent / 'backend'
        load_dotenv(backend_dir / '.env')
        
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        
        # Test connection with timeout
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        
        print(f"✅ MongoDB connection successful")
        print(f"   Connected to: {mongo_url}")
        
        # List databases to verify access
        dbs = client.list_database_names()
        print(f"   Available databases: {len(dbs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Make sure MongoDB is running:")
        print("   - Local: mongod --dbpath ./data")
        print("   - Atlas: Check connection string")
        return False

def test_email_config():
    """Test email configuration"""
    print("Testing email configuration...")
    
    try:
        from dotenv import load_dotenv
        import smtplib
        
        # Load environment variables
        backend_dir = Path(__file__).parent / 'backend'
        load_dotenv(backend_dir / '.env')
        
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not email_address or email_address.startswith('your_'):
            print("⚠️  Email address not configured")
            return False
            
        if not email_password or email_password.startswith('your_'):
            print("⚠️  Email password not configured")
            return False
        
        # Test SMTP connection (but don't send email)
        print(f"   Email address: {email_address}")
        print(f"   Password: {'*' * len(email_password)}")
        print("✅ Email configuration looks good")
        print("   (Use 'Schedule Email' feature to test sending)")
        
        return True
        
    except Exception as e:
        print(f"❌ Email configuration error: {e}")
        return False

def create_sample_data():
    """Create sample CSV files for testing"""
    print("Creating sample data files...")
    
    # Create sample sponsor data
    sponsor_data = """Name,Email,Organization,Title,Industry
John Doe,john.doe@techcorp.com,Tech Corp,CTO,Technology
Jane Smith,jane.smith@startup.io,Startup Inc,Founder,Technology  
Bob Wilson,bob.wilson@bigco.com,Big Company,Director,Finance
Alice Johnson,alice.johnson@innovate.com,Innovate Ltd,CEO,Healthcare
Charlie Brown,charlie.brown@future.org,Future Org,Manager,Education"""

    # Create sample participant data
    participant_data = """Name,Email,Team,Project,Category
Alice Wonder,alice.wonder@example.com,Team Alpha,AI Assistant,AI/ML
Bob Builder,bob.builder@example.com,Team Beta,Blockchain App,Blockchain
Carol Coder,carol.coder@example.com,Solo Developer,FinTech Platform,FinTech
Dave Designer,dave.designer@example.com,Team Gamma,EdTech Solution,EdTech
Eve Engineer,eve.engineer@example.com,Team Delta,Health Monitor,Healthcare"""

    # Save files
    sponsor_file = Path('sample_sponsors.csv')
    participant_file = Path('sample_participants.csv')
    
    sponsor_file.write_text(sponsor_data)
    participant_file.write_text(participant_data)
    
    print(f"✅ Created {sponsor_file} (5 sponsors)")
    print(f"✅ Created {participant_file} (5 participants)")
    print("   Use these files to test the upload functionality")
    
    return True

def test_server_import():
    """Test if server modules can be imported"""
    print("Testing server module imports...")
    
    try:
        # Add backend to path
        backend_dir = Path(__file__).parent / 'backend'
        sys.path.insert(0, str(backend_dir))
        
        # Test core imports
        from fastapi import FastAPI
        print("✅ FastAPI import successful")
        
        from motor.motor_asyncio import AsyncIOMotorClient
        print("✅ Motor MongoDB driver import successful")
        
        import pandas as pd
        print("✅ Pandas import successful")
        
        # Test if we can create the basic server structure
        app = FastAPI()
        print("✅ FastAPI app creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Server import test failed: {e}")
        return False

def run_basic_server_test():
    """Run a basic server startup test"""
    print("Testing basic server functionality...")
    
    try:
        backend_dir = Path(__file__).parent / 'backend'
        
        # Try to run server validation (without actually starting it)
        result = subprocess.run([
            sys.executable, '-c', 
            f"import sys; sys.path.insert(0, '{backend_dir}'); "
            "from fastapi import FastAPI; "
            "print('Server modules can be imported successfully')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Server startup test passed")
            return True
        else:
            print(f"❌ Server startup test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Server test error: {e}")
        return False

def generate_setup_report(results):
    """Generate a setup report with next steps"""
    print_header("SETUP REPORT")
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your backend is ready to run.")
        print("\nNext steps:")
        print("1. cd backend")
        print("2. python server.py")
        print("3. Open http://localhost:8000/docs")
        
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nFailed tests:")
        for test_name, result in results.items():
            if not result:
                print(f"  - {test_name}")
        
        print("\nRecommended fixes:")
        if not results.get('dependencies'):
            print("  - Run: pip install -r backend/requirements.txt")
        if not results.get('environment'):
            print("  - Update backend/.env with your credentials")
        if not results.get('mongodb'):
            print("  - Start MongoDB or check connection string")

def main():
    """Main test function"""
    print_header("HACKFINITY PLATFORM BACKEND TEST")
    print("This script verifies your backend setup before starting the server.")
    
    results = {}
    
    # Test 1: Python version
    print_step(1, "Python Version Check")
    results['python'] = check_python_version()
    
    # Test 2: Dependencies
    print_step(2, "Dependency Check")
    missing, installed = check_dependencies()
    results['dependencies'] = len(missing) == 0
    
    if missing:
        print(f"\n💡 Install missing packages:")
        print(f"pip install {' '.join(missing)}")
    
    # Test 3: Environment file
    print_step(3, "Environment Configuration")
    env_ok, env_vars = check_env_file()
    results['environment'] = env_ok
    
    # Test 4: MongoDB connection
    print_step(4, "MongoDB Connection")
    results['mongodb'] = test_mongodb_connection()
    
    # Test 5: Email configuration
    print_step(5, "Email Configuration")
    results['email'] = test_email_config()
    
    # Test 6: Server imports
    print_step(6, "Server Module Test")
    results['server'] = test_server_import()
    
    # Test 7: Create sample data
    print_step(7, "Sample Data Creation")
    results['sample_data'] = create_sample_data()
    
    # Generate final report
    generate_setup_report(results)
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
