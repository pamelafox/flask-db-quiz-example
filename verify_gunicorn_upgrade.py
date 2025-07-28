#!/usr/bin/env python3
"""
Verification script for gunicorn upgrade from 22.0.0 to 23.0.0
This script validates that the requirements.txt file contains the correct gunicorn version.
"""

import re
import sys
from pathlib import Path

def check_gunicorn_version():
    """Check if requirements.txt contains gunicorn==23.0.0"""
    requirements_path = Path("src/requirements.txt")
    
    if not requirements_path.exists():
        print("❌ ERROR: src/requirements.txt not found")
        return False
    
    with open(requirements_path, 'r') as f:
        content = f.read()
    
    # Look for gunicorn requirement
    gunicorn_pattern = r'^gunicorn==(.+)$'
    
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('gunicorn=='):
            match = re.match(gunicorn_pattern, line)
            if match:
                version = match.group(1)
                print(f"✅ Found gunicorn requirement: {line}")
                
                if version == "23.0.0":
                    print("✅ SUCCESS: gunicorn is correctly set to version 23.0.0")
                    return True
                else:
                    print(f"❌ ERROR: Expected gunicorn==23.0.0, but found gunicorn=={version}")
                    return False
    
    print("❌ ERROR: No gunicorn requirement found in requirements.txt")
    return False

def main():
    print("🔍 Verifying gunicorn upgrade...")
    print("="*50)
    
    if check_gunicorn_version():
        print("\n🎉 Verification successful! The gunicorn upgrade is properly configured.")
        print("📝 Next steps:")
        print("   1. Create a virtual environment: python -m venv .venv")
        print("   2. Activate it: source .venv/bin/activate")
        print("   3. Install requirements: python -m pip install -r requirements-dev.txt")
        print("   4. Run tests: python -m pytest")
        return 0
    else:
        print("\n❌ Verification failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())