# File: src/core/forensics_engine.py
import platform
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import logging
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from core.data_models import ClipboardEntry, ForensicsReport

class ForensicsEngine:
    """Main forensics engine that orchestrates the analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.platform = platform.system().lower()
        self.entries: List[ClipboardEntry] = []
        self.stats = defaultdict(int)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ForensicsEngine initialized for {self.platform}")
    
    def analyze(self) -> ForensicsReport:
        """Main analysis orchestration method"""
        self.logger.info(f"Starting clipboard forensics analysis on {self.platform}")
        
        try:
            # Platform-specific extraction
            self._extract_platform_data()
            
            # Pattern analysis
            pattern_results = self._analyze_patterns()
            
            # Timeline creation
            timeline = self._create_timeline()
            
            # Generate report
            report = self._generate_report(pattern_results, timeline)
            
            self.logger.info(f"Analysis complete. Found {len(self.entries)} clipboard entries")
            return report
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            # Return empty report instead of crashing
            return self._generate_empty_report(str(e))
    
    def _extract_platform_data(self):
        """Extract data from the current platform"""
        self.logger.info(f"Extracting data for platform: {self.platform}")
        
        try:
            if self.platform == "windows":
                self._extract_windows_data()
            elif self.platform == "linux":
                self.logger.info("Linux analysis not yet implemented (Week 3)")
            elif self.platform == "darwin":
                self.logger.info("macOS analysis not yet implemented (Week 4)")
            else:
                self.logger.warning(f"Unsupported platform: {self.platform}")
        except Exception as e:
            self.logger.error(f"Platform extraction failed: {e}")
    
    def _extract_windows_data(self):
        """Extract Windows-specific data"""
        try:
            from platforms.windows_analyzer import WindowsAnalyzer
            analyzer = WindowsAnalyzer()
            platform_entries = analyzer.extract_clipboard_data()
            self.entries.extend(platform_entries)
            self.stats['platform_entries'] = len(platform_entries)
            self.logger.info(f"Extracted {len(platform_entries)} entries from Windows")
        except ImportError as e:
            self.logger.warning(f"Windows analyzer not available: {e}")
            self._add_sample_entry()
        except Exception as e:
            self.logger.error(f"Windows extraction failed: {e}")
            self._add_sample_entry()
    
    def _add_sample_entry(self):
        """Add a sample entry for testing purposes"""
        sample_entry = ClipboardEntry(
            timestamp=datetime.now().isoformat(),
            content_type="text",
            content="Sample clipboard content for testing",
            content_hash="",
            size_bytes=34,
            source_app="Test System",
            user=os.environ.get('USERNAME', 'unknown'),
            session_info="Sample"
        )
        self.entries.append(sample_entry)
        self.stats['sample_entries'] = 1
        self.logger.info("Added sample entry for testing")
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in clipboard data"""
        try:
            from analyzers.enhanced_pattern_analyzer import EnhancedPatternAnalyzer
            analyzer = EnhancedPatternAnalyzer()
            enhanced_results = analyzer.analyze(self.entries)
            
            # Create compatible structure
            results = {
                'suspicious_patterns': enhanced_results.get('findings', []),
                'data_types': defaultdict(int),
                'frequent_sources': defaultdict(int),
                'potential_exfiltration': [],
                'enhanced': enhanced_results
            }
            
            return results
        except ImportError as e:
            self.logger.warning(f"Enhanced analyzer not available: {e}")
            return self._empty_pattern_results()
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
            return self._empty_pattern_results()
    
    def _create_timeline(self) -> List[Dict[str, Any]]:
        """Create timeline of clipboard events"""
        try:
            from analyzers.timeline_analyzer import TimelineAnalyzer
            analyzer = TimelineAnalyzer()
            return analyzer.create_timeline(self.entries)
        except ImportError as e:
            self.logger.warning(f"Timeline analyzer not available: {e}")
            return self._create_simple_timeline()
        except Exception as e:
            self.logger.error(f"Timeline creation failed: {e}")
            return self._create_simple_timeline()
    
    def _create_simple_timeline(self) -> List[Dict[str, Any]]:
        """Create a simple timeline when analyzer isn't available"""
        timeline = []
        for i, entry in enumerate(self.entries):
            timeline.append({
                'sequence': i + 1,
                'timestamp': entry.timestamp,
                'content_type': entry.content_type,
                'source_app': entry.source_app or 'Unknown',
                'content_preview': entry.content[:50] + "..." if len(entry.content) > 50 else entry.content,
                'size_bytes': entry.size_bytes
            })
        return timeline
    
    def _empty_pattern_results(self):
        """Return empty pattern analysis results"""
        return {
            'suspicious_patterns': [],
            'data_types': defaultdict(int),
            'frequent_sources': defaultdict(int),
            'potential_exfiltration': [],
            'sensitive_data_found': defaultdict(list),
            'enhanced': {
                'findings': [],
                'summary': {},
                'risk_score': 0,
                'recommendations': ['Pattern analysis unavailable']
            }
        }
    
    def _analyze_statistics(self) -> Dict[str, Any]:
        """Generate usage statistics"""
        try:
            from ..analyzers.statistics_analyzer import StatisticsAnalyzer
            analyzer = StatisticsAnalyzer()
            return analyzer.analyze(self.entries)
        except Exception as e:
            self.logger.error(f"Statistics analysis failed: {e}")
            return {}
    
    def _generate_report(self, pattern_results: Dict, timeline: List[Dict]) -> ForensicsReport:
        """Generate comprehensive forensics report"""
        metadata = {
            "analysis_time": datetime.now().isoformat(),
            "platform": self.platform.title(),
            "total_entries": len(self.entries),
            "user": os.environ.get('USER') or os.environ.get('USERNAME'),
            "hostname": platform.node(),
            "analyzer_version": "1.0.0"
        }
        
        # Add statistics
        statistics = self._analyze_statistics()

        return ForensicsReport(
            metadata=metadata,
            entries=self.entries,
            statistics=statistics,
            timeline=timeline,
            analysis=pattern_results,
            generated_at=datetime.now().isoformat()
        )
    
    def _generate_empty_report(self, error_msg: str) -> ForensicsReport:
        """Generate empty report when analysis fails"""
        metadata = {
            "analysis_time": datetime.now().isoformat(),
            "platform": self.platform.title(),
            "total_entries": 0,
            "user": os.environ.get('USER') or os.environ.get('USERNAME'),
            "hostname": platform.node(),
            "analyzer_version": "1.0.0",
            "error": error_msg
        }
        
        return ForensicsReport(
            metadata=metadata,
            entries=[],
            statistics={},
            timeline=[],
            analysis={'error': error_msg, 'suspicious_patterns': [], 'potential_exfiltration': []},
            generated_at=datetime.now().isoformat()
        )