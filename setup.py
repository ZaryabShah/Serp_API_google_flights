"""
Setup script for the Google Flights URL Generator project.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    
    # Basic requirements (without Playwright for now)
    basic_requirements = [
        "click>=8.0.0",
        "requests>=2.28.0"
    ]
    
    for package in basic_requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
    
    # Optional: Install Playwright for URL validation
    print("\n🎭 Installing Playwright for URL validation (optional)...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        print("✅ Installed Playwright")
        
        # Install browser
        print("🌐 Installing Chromium browser...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("✅ Installed Chromium browser")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Playwright installation failed: {e}")
        print("   URL validation will not be available, but URL generation will work fine.")

def run_basic_test():
    """Run a basic test to ensure everything works."""
    print("\n🧪 Running basic functionality test...")
    
    try:
        # Import and test the library
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from gfurl import build_gf_url
        
        # Test basic URL generation
        url = build_gf_url(
            legs=[{"from": "SYD", "to": "MEL", "date": "2025-08-15"}],
            pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
            hl="en", gl="AU", currency="AUD"
        )
        
        print("✅ Basic URL generation works!")
        print(f"🔗 Sample URL: {url[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Google Flights URL Generator")
    print("=" * 60)
    
    # Install requirements
    install_requirements()
    
    # Run basic test
    if run_basic_test():
        print("\n" + "=" * 60)
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Run examples: python examples/basic_examples.py")
        print("   2. Run CLI: python cli.py --help")
        print("   3. Run tests: python test_generator.py")
        print("   4. Open test form: examples/test_form.html")
        print("\n💡 Quick test:")
        print("   python cli.py --from LAX --to JFK --depart 2025-08-15")
    else:
        print("\n❌ Setup encountered issues. Please check the error messages above.")

if __name__ == "__main__":
    main()
