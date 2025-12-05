# File: src/analyzers/timeline_analyzer.py
from typing import List, Dict, Any
from datetime import datetime
import logging

class TimelineAnalyzer:
    """Analyzes clipboard data chronologically"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_timeline(self, entries: List) -> List[Dict[str, Any]]:
        """Create chronological timeline of clipboard events"""
        self.logger.info(f"Creating timeline from {len(entries)} entries")
        
        if not entries:
            return []
        
        timeline = []
        for i, entry in enumerate(entries):
            timeline.append({
                'sequence': i + 1,
                'timestamp': getattr(entry, 'timestamp', 'unknown'),
                'content_type': getattr(entry, 'content_type', 'unknown'),
                'source_app': getattr(entry, 'source_app', 'unknown'),
                'content_preview': self._create_preview(getattr(entry, 'content', '')),
                'size_bytes': getattr(entry, 'size_bytes', 0)
            })
        
        return timeline
    
    def _create_preview(self, content: str, max_length: int = 100) -> str:
        """Create a safe preview of clipboard content"""
        if not content:
            return "[Empty]"
        
        cleaned = str(content).replace('\n', ' ').replace('\r', ' ').strip()
        
        if len(cleaned) <= max_length:
            return cleaned
        
        return cleaned[:max_length] + "..."