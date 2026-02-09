#!/usr/bin/env python3
"""Verify backend setup and dependencies."""

import sys
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print("✅ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python 3.9+ required, got:", f"{version.major}.{version.minor}")
        return False

def check_dependencies():
    """Check required dependencies."""
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic_settings",
        "supabase",
        "python_jose",
        "passlib",
        "pytest",
    ]
    
    missing = []
    for package in required:
        try:
            importlib.import_module(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0

def check_file_structure():
    """Check required files exist."""
    required_files = [
        "main.py",
        "config.py",
        "models.py",
        "database.py",
        "middleware.py",
        "requirements.txt",
        "providers/__init__.py",
        "providers/base.py",
        "providers/openai.py",
        "providers/anthropic.py",
        "providers/google.py",
        "engines/__init__.py",
        "engines/cost_engine.py",
        "engines/recommendations_engine.py",
        "routes/__init__.py",
        "routes/auth.py",
        "routes/events.py",
        "routes/costs.py",
        "routes/budgets.py",
        "routes/recommendations.py",
        "routes/health.py",
        "tests/__init__.py",
        "tests/test_providers.py",
        "tests/test_cost_engine.py",
        "tests/test_api.py",
    ]
    
    backend_dir = Path(__file__).parent
    missing_files = []
    
    for file in required_files:
        path = backend_dir / file
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_environment():
    """Check .env file."""
    env_file = Path(__file__).parent / ".env"
    example_file = Path(__file__).parent / ".env.example"
    
    if env_file.exists():
        print("✅ .env file exists")
        return True
    elif example_file.exists():
        print("⚠️  .env file missing (but .env.example exists)")
        print("   Run: cp .env.example .env")
        return False
    else:
        print("❌ Neither .env nor .env.example found")
        return False

def main():
    """Run all checks."""
    print("\n🔍 LLMLab Backend Verification\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Environment", check_environment),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}")
        print("-" * 40)
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 40)
    if all(results):
        print("✅ All checks passed!")
        print("\n🚀 Ready to start:")
        print("   python main.py")
        return 0
    else:
        print("❌ Some checks failed")
        print("\n📖 See documentation for setup steps")
        return 1

if __name__ == "__main__":
    sys.exit(main())
