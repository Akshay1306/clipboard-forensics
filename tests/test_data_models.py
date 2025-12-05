# File: tests/test_data_models.py (Simplified - no complex imports)
import pytest
from datetime import datetime
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.data_models import ClipboardEntry, ForensicsReport

class TestClipboardEntry:
    def test_clipboard_entry_creation(self):
        """Test basic clipboard entry creation"""
        entry = ClipboardEntry(
            timestamp=datetime.now().isoformat(),
            content_type="text",
            content="Hello World",
            content_hash="",
            size_bytes=11,
            source_app="Test App"
        )
        
        assert entry.content == "Hello World"
        assert entry.content_type == "text"
        assert entry.size_bytes == 11
        assert entry.content_hash  # Should be auto-generated
    
    def test_clipboard_entry_hash_generation(self):
        """Test automatic hash generation"""
        entry = ClipboardEntry(
            timestamp=datetime.now().isoformat(),
            content_type="text",
            content="Test content",
            content_hash="",
            size_bytes=12
        )
        
        # Hash should be generated automatically
        assert entry.content_hash
        assert len(entry.content_hash) == 16  # Truncated to 16 chars
    
    def test_clipboard_entry_serialization(self):
        """Test dictionary conversion"""
        entry = ClipboardEntry(
            timestamp=datetime.now().isoformat(),
            content_type="text",
            content="Test",
            content_hash="abc123",
            size_bytes=4
        )
        
        entry_dict = entry.to_dict()
        assert entry_dict['content'] == "Test"
        assert entry_dict['content_type'] == "text"
        
        # Test deserialization
        new_entry = ClipboardEntry.from_dict(entry_dict)
        assert new_entry.content == entry.content
        assert new_entry.content_type == entry.content_type

class TestForensicsReport:
    def test_report_creation(self):
        """Test forensics report creation"""
        # Create a sample entry
        entry = ClipboardEntry(
            timestamp=datetime.now().isoformat(),
            content_type="text",
            content="Sample content",
            content_hash="sample123",
            size_bytes=14
        )
        
        # Create report
        report = ForensicsReport(
            metadata={"platform": "test", "total_entries": 1},
            entries=[entry],
            statistics={"text": 1},
            timeline=[{"time": entry.timestamp, "content": "Sample content"}],
            analysis={"patterns": []},
            generated_at=datetime.now().isoformat()
        )
        
        assert len(report.entries) == 1
        assert report.metadata["platform"] == "test"
        assert report.statistics["text"] == 1
    
    def test_report_json_serialization(self):
        """Test JSON serialization of report"""
        entry = ClipboardEntry(
            timestamp="2023-12-01T10:00:00",
            content_type="text",
            content="Test content",
            content_hash="test123",
            size_bytes=12
        )
        
        report = ForensicsReport(
            metadata={"test": "value"},
            entries=[entry],
            statistics={"total": 1},
            timeline=[],
            analysis={},
            generated_at="2023-12-01T10:00:00"
        )
        
        json_str = report.to_json()
        assert '"test": "value"' in json_str
        assert '"content": "Test content"' in json_str