import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from platforms.windows_analyzer import WindowsAnalyzer

def test_windows_analyzer_initialization():
    analyzer = WindowsAnalyzer()
    assert analyzer.user_profile
    assert analyzer.entries == []

def test_current_clipboard_extraction():
    analyzer = WindowsAnalyzer()
    current = analyzer.get_current_clipboard()
    # May be None if clipboard is empty
    if current:
        assert current.content_type == "text"
        assert current.source_app == "Windows Clipboard"

def test_full_extraction():
    analyzer = WindowsAnalyzer()
    entries = analyzer.extract_clipboard_data()
    # Should have at least registry entries
    assert len(entries) >= 1