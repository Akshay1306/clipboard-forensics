# File: tests/run_tests.py (Updated)
#!/usr/bin/env python3
"""
Test runner script for the clipboard forensics project
"""
import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Run the complete test suite"""
    
    # Get project root and setup paths
    project_root = Path(__file__).parent.parent
    src_path = project_root / 'src'
    
    print("Running Clipboard Forensics Test Suite")
    print("=" * 50)
    print(f"Project root: {project_root}")
    print(f"Python path: {sys.executable}")
    print()
    
    # Add src to Python path
    sys.path.insert(0, str(src_path))
    
    # Check if pytest is available
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
        import pytest
        print("✅ pytest installed")
    
    # Find test files
    test_files = list(Path('tests').glob('test_*.py'))
    print(f"📋 Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"   - {test_file.name}")
    print()
    
    # Check for coverage
    try:
        import pytest_cov
        print("✅ Running with coverage")
        coverage_args = ['--cov=src/', '--cov-report=term-missing']
    except ImportError:
        print("⚠️  Running without coverage (install pytest-cov for coverage)")
        coverage_args = []
    
    print("Running tests...")
    print("-" * 30)
    
    # Run pytest
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short'
    ] + coverage_args
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        print("-" * 30)
        
        if result.returncode == 0:
            print("✅ All tests passed")
        else:
            print("❌ Some tests failed")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)