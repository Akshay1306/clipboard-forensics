# File: src/analyzers/statistics_analyzer.py
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any
import logging

class StatisticsAnalyzer:
    """Analyze clipboard usage patterns and statistics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, entries: List) -> Dict[str, Any]:
        """Generate comprehensive statistics"""
        if not entries:
            return {}
        
        return {
            'hourly_activity': self._hourly_activity(entries),
            'source_distribution': self._source_distribution(entries),
            'content_type_stats': self._content_type_stats(entries),
            'size_statistics': self._size_statistics(entries),
            'time_gaps': self._analyze_time_gaps(entries)
        }
    
    def _hourly_activity(self, entries: List) -> Dict[int, int]:
        """Count clipboard operations by hour of day"""
        hourly = defaultdict(int)
        
        for entry in entries:
            try:
                timestamp = getattr(entry, 'timestamp', '')
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hourly[dt.hour] += 1
            except:
                continue
        
        # Fill in missing hours with 0
        return {hour: hourly.get(hour, 0) for hour in range(24)}
    
    def _source_distribution(self, entries: List) -> Dict[str, int]:
        """Count entries by source application"""
        sources = defaultdict(int)
        
        for entry in entries:
            source = getattr(entry, 'source_app', 'Unknown') or 'Unknown'
            sources[source] += 1
        
        return dict(sources)
    
    def _content_type_stats(self, entries: List) -> Dict[str, int]:
        """Count entries by content type"""
        types = defaultdict(int)
        
        for entry in entries:
            content_type = getattr(entry, 'content_type', 'unknown')
            types[content_type] += 1
        
        return dict(types)
    
    def _size_statistics(self, entries: List) -> Dict[str, Any]:
        """Calculate size statistics"""
        sizes = [getattr(entry, 'size_bytes', 0) for entry in entries]
        sizes = [s for s in sizes if s > 0]
        
        if not sizes:
            return {}
        
        return {
            'total_bytes': sum(sizes),
            'average_bytes': sum(sizes) / len(sizes),
            'min_bytes': min(sizes),
            'max_bytes': max(sizes),
            'median_bytes': sorted(sizes)[len(sizes)//2]
        }
    
    def _analyze_time_gaps(self, entries: List) -> Dict[str, Any]:
        """Analyze time between clipboard operations"""
        if len(entries) < 2:
            return {}
        
        gaps = []
        sorted_entries = sorted(entries, key=lambda x: getattr(x, 'timestamp', ''))
        
        for i in range(1, len(sorted_entries)):
            try:
                prev = datetime.fromisoformat(getattr(sorted_entries[i-1], 'timestamp', '').replace('Z', '+00:00'))
                curr = datetime.fromisoformat(getattr(sorted_entries[i], 'timestamp', '').replace('Z', '+00:00'))
                gap_seconds = (curr - prev).total_seconds()
                if gap_seconds > 0:
                    gaps.append(gap_seconds)
            except:
                continue
        
        if not gaps:
            return {}
        
        return {
            'average_gap_seconds': sum(gaps) / len(gaps),
            'min_gap_seconds': min(gaps),
            'max_gap_seconds': max(gaps),
            'rapid_operations': len([g for g in gaps if g < 2])  # Operations < 2 seconds apart
        }