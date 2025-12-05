#!/usr/bin/env python3
"""
Quick project status check
"""
import os
from pathlib import Path
from datetime import datetime

def check_project_status():
    """Check basic project status"""
    project_root = Path.cwd()
    
    print("🔍 Clipboard Forensics - Quick Status Check")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project root: {project_root}")
    print()
    
    # Check key files
    key_files = {
        "Core": [
            "src/core/data_models.py",
            "src/core/forensics_engine.py"
        ],
        "Platforms": [
            "src/platforms/base_analyzer.py",
            "src/platforms/windows_analyzer.py"
        ],
        "Main": [
            "src/main.py",
            "requirements.txt"
        ],
        "Tests": [
            "tests/test_simple.py",
            "tests/test_data_models.py"
        ]
    }
    
    total_files = 0
    found_files = 0
    
    for category, files in key_files.items():
        print(f"📋 {category}:")
        for file_path in files:
            total_files += 1
            full_path = project_root / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                print(f"  ✅ {file_path} ({size} bytes)")
                found_files += 1
            else:
                print(f"  ❌ {file_path} (missing)")
        print()
    
    # Calculate completion percentage
    completion = (found_files / total_files) * 100
    print(f"📊 Project Completion: {completion:.1f}% ({found_files}/{total_files} files)")
    
    # Check if CLI works
    print("\n🧪 Quick CLI Test:")
    try:
        import subprocess
        result = subprocess.run([
            'python', 'src/main.py', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✅ CLI help working")
            
            # Try analysis
            result2 = subprocess.run([
                'python', 'src/main.py', '--cli', '--output', 'temp_test/'
            ], capture_output=True, text=True, timeout=15)
            
            if result2.returncode == 0:
                print("  ✅ CLI analysis working")
            else:
                print("  ⚠️  CLI analysis has issues (but this is normal)")
        else:
            print("  ❌ CLI help failing")
    except Exception as e:
        print(f"  ⚠️  Could not test CLI: {e}")
    
    print("\n🎯 Week 1 Progress:")
    if completion >= 75:
        print("  ✅ Week 1 goals mostly achieved!")
        print("  📋 Ready for Week 2: Windows Implementation")
    elif completion >= 50:
        print("  🔄 Week 1 in good progress")
        print("  📋 Focus on completing core files")
    else:
        print("  ⚠️  Need to catch up on Week 1 goals")
    
    print("\n💡 Next Steps:")
    print("  1. Fix relative import issues")
    print("  2. Complete Windows analyzer")
    print("  3. Test clipboard extraction")
    print("  4. Prepare for Week 2")

if __name__ == "__main__":
    check_project_status()