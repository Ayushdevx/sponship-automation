#!/usr/bin/env python3
"""
Test script to verify the Hackfinity platform setup
"""

def test_imports():
    """Test if all required modules can be imported"""
    try:
        # Test FastAPI and basic dependencies
        from fastapi import FastAPI
        print("✓ FastAPI imported successfully")
        
        # Test analytics module
        from analytics import AnalyticsEngine
        print("✓ AnalyticsEngine imported successfully")
        
        # Test template engine
        from template_engine import TemplateEngine
        print("✓ TemplateEngine imported successfully")
        
        # Test certificate customizer
        from certificate_customizer import CertificateCustomizer
        print("✓ CertificateCustomizer imported successfully")
        
        # Test data processing libraries
        import pandas as pd
        import matplotlib.pyplot as plt
        import plotly.express as px
        print("✓ Data processing libraries imported successfully")
        
        print("\n🎉 All imports successful! The platform is ready to run.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_server():
    """Test if the server can be created"""
    try:
        from fastapi import FastAPI
        app = FastAPI()
        print("✓ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ Server creation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Hackfinity Platform Setup")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test basic server creation
        server_ok = test_basic_server()
        
        if server_ok:
            print("\n✅ Platform setup verification complete!")
            print("You can now start the server with: python server.py")
        else:
            print("\n❌ Server setup issues detected")
    else:
        print("\n❌ Import issues detected. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")
