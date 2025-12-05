# File: tests/test_simple.py
"""Simple test that should work"""

def test_basic_math():
    """Test that basic Python works"""
    assert 1 + 1 == 2
    assert 2 * 2 == 4

def test_basic_imports():
    """Test that we can import standard Python modules"""
    import os
    import sys
    import json
    assert os is not None
    assert sys is not None
    assert json is not None

def test_project_structure():
    """Test that we can find project files"""
    import os
    from pathlib import Path
    
    # Get project root
    test_file = Path(__file__)
    project_root = test_file.parent.parent
    
    # Check that src directory exists
    src_dir = project_root / "src"
    assert src_dir.exists(), f"src directory not found at {src_dir}"
    
    # Check that core module exists
    core_dir = src_dir / "core"
    assert core_dir.exists(), f"core directory not found at {core_dir}"
    
    # Check that data_models.py exists
    data_models_file = core_dir / "data_models.py"
    assert data_models_file.exists(), f"data_models.py not found at {data_models_file}"

def test_data_models_import():
    """Test that we can import our data models"""
    import sys
    from pathlib import Path
    
    # Add src to path
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from core.data_models import ClipboardEntry, ForensicsReport
        assert ClipboardEntry is not None
        assert ForensicsReport is not None
    except ImportError as e:
        # Print detailed error for debugging
        print(f"Import error: {e}")
        print(f"Python path: {sys.path}")
        print(f"Src path: {src_path}")
        raise

def test_clipboard_entry_creation():
    """Test creating a clipboard entry"""
    import sys
    from pathlib import Path
    from datetime import datetime
    
    # Add src to path
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    from core.data_models import ClipboardEntry
    
    entry = ClipboardEntry(
        timestamp=datetime.now().isoformat(),
        content_type="text",
        content="Test content",
        content_hash="",
        size_bytes=12
    )
    
    assert entry.content == "Test content"
    assert entry.content_type == "text"
    assert entry.size_bytes == 12
    # Hash should be auto-generated
    assert len(entry.content_hash) == 16