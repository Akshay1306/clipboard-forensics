# File: src/platforms/platform_factory.py
import platform
from typing import Optional
from .base_analyzer import BaseAnalyzer

class PlatformAnalyzerFactory:
    """Factory for creating platform-specific analyzers"""
    
    @staticmethod
    def create_analyzer(platform_name: str = None) -> BaseAnalyzer:
        """Create appropriate analyzer for the platform"""
        if platform_name is None:
            platform_name = platform.system().lower()
        
        if platform_name == "windows":
            from .windows_analyzer import WindowsAnalyzer
            return WindowsAnalyzer()
        elif platform_name == "darwin":
            from .macos_analyzer import MacOSAnalyzer
            return MacOSAnalyzer()
        elif platform_name == "linux":
            from .linux_analyzer import LinuxAnalyzer
            return LinuxAnalyzer()
        else:
            raise NotImplementedError(f"Platform {platform_name} not supported yet")

# =====================================

# File: src/platforms/windows_analyzer.py
import os
import sqlite3
import winreg
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import logging

from .base_analyzer import BaseAnalyzer
from ..core.data_models import ClipboardEntry

class WindowsAnalyzer(BaseAnalyzer):
    """Windows-specific clipboard analysis"""
    
    def __init__(self):
        super().__init__()
        self.user_profile = os.environ.get('USERPROFILE', '')
        
    def extract_clipboard_data(self) -> List[ClipboardEntry]:
        """Main extraction method for Windows"""
        self.logger.info("Starting Windows clipboard extraction")
        
        # Extract from various sources
        self._extract_cloud_clipboard()
        self._extract_registry_data()
        self._extract_clipboard_managers()
        self._get_current_clipboard()
        
        self.logger.info(f"Extracted {len(self.entries)} entries from Windows")
        return self.entries
    
    def _extract_cloud_clipboard(self):
        """Extract Windows 10/11 Cloud Clipboard data"""
        try:
            clipboard_db = Path(self.user_profile) / "AppData/Local/Microsoft/Windows/CloudClipboard/clipboard.db"
            
            if not clipboard_db.exists():
                self.logger.info("Cloud clipboard database not found")
                return
                
            self.logger.info(f"Analyzing cloud clipboard database: {clipboard_db}")
            
            conn = sqlite3.connect(str(clipboard_db))
            cursor = conn.cursor()
            
            # Get table structure first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.logger.debug(f"Found tables: {tables}")
            
            # Try to extract from main clipboard table
            for table in tables:
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 10")
                    columns = [description[0] for description in cursor.description]
                    self.logger.debug(f"Table {table} columns: {columns}")
                    
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        entry = self._create_entry_from_row(row, columns, "Windows Cloud Clipboard")
                        if entry:
                            self.entries.append(entry)
                            
                except sqlite3.Error as e:
                    self.logger.warning(f"Error reading table {table}: {e}")
                    continue
            
            conn.close()
            self.logger.info(f"Extracted {len([e for e in self.entries if e.source_app == 'Windows Cloud Clipboard'])} cloud clipboard entries")
            
        except Exception as e:
            self.logger.error(f"Error extracting cloud clipboard: {e}")
    
    def _extract_registry_data(self):
        """Extract clipboard-related registry data"""
        try:
            registry_paths = [
                r"SOFTWARE\Microsoft\Clipboard",
                r"SOFTWARE\Classes\CLSID\{clipboard-related-keys}"
            ]
            
            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        info = winreg.QueryInfoKey(key)
                        num_values = info[1]
                        
                        for i in range(num_values):
                            try:
                                name, value, reg_type = winreg.EnumValue(key, i)
                                
                                entry = ClipboardEntry(
                                    timestamp=datetime.now().isoformat(),
                                    content_type="registry_data",
                                    content=f"{name}: {value}",
                                    content_hash="",
                                    size_bytes=len(str(value)),
                                    source_app="Windows Registry",
                                    user=os.environ.get('USERNAME'),
                                    session_info="Local",
                                    metadata={"registry_path": reg_path, "type": reg_type}
                                )
                                self.entries.append(entry)
                                
                            except WindowsError:
                                continue
                                
                except WindowsError as e:
                    self.logger.debug(f"Registry path {reg_path} not accessible: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error extracting registry data: {e}")
    
    def _extract_clipboard_managers(self):
        """Extract data from popular Windows clipboard managers"""
        managers = {
            "Ditto": "%APPDATA%/Ditto/Ditto.db",
            "ClipX": "%APPDATA%/ClipX/clipdata.txt",
            "Clipboard Master": "%APPDATA%/Clipboard Master/data.db",
            "CLCL": "%APPDATA%/CLCL/CLCL.ini"
        }
        
        for manager_name, path_template in managers.items():
            try:
                manager_path = os.path.expandvars(path_template)
                if os.path.exists(manager_path):
                    self.logger.info(f"Found {manager_name} at {manager_path}")
                    self._extract_manager_data(manager_name, manager_path)
            except Exception as e:
                self.logger.warning(f"Error checking {manager_name}: {e}")
    
    def _extract_manager_data(self, manager_name: str, path: str):
        """Extract data from specific clipboard manager"""
        try:
            if path.endswith('.db'):
                # SQLite database
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    try:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            entry = self._create_entry_from_row(row, columns, manager_name)
                            if entry:
                                self.entries.append(entry)
                                
                    except sqlite3.Error:
                        continue
                        
                conn.close()
                
            elif path.endswith(('.txt', '.ini')):
                # Text-based storage
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                entry = ClipboardEntry(
                    timestamp=datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
                    content_type="text",
                    content=content[:1000],
                    content_hash="",
                    size_bytes=len(content),
                    source_app=manager_name,
                    user=os.environ.get('USERNAME'),
                    session_info="Stored"
                )
                self.entries.append(entry)
                
        except Exception as e:
            self.logger.error(f"Error extracting from {manager_name}: {e}")
    
    def _create_entry_from_row(self, row, columns, source_app):
        """Create ClipboardEntry from database row"""
        try:
            # Create a dictionary from row data
            row_data = dict(zip(columns, row))
            
            # Extract common fields
            content = ""
            timestamp = datetime.now().isoformat()
            
            # Try to find content in various column names
            content_columns = ['content', 'text', 'data', 'clipboard_data', 'item_text']
            for col in content_columns:
                if col in row_data and row_data[col]:
                    content = str(row_data[col])
                    break
            
            # Try to find timestamp
            time_columns = ['timestamp', 'time', 'created', 'date_created', 'modified']
            for col in time_columns:
                if col in row_data and row_data[col]:
                    try:
                        if isinstance(row_data[col], (int, float)):
                            timestamp = datetime.fromtimestamp(row_data[col]).isoformat()
                        else:
                            timestamp = str(row_data[col])
                    except:
                        pass
                    break
            
            if content:
                return ClipboardEntry(
                    timestamp=timestamp,
                    content_type="text",
                    content=content[:1000],
                    content_hash="",
                    size_bytes=len(content),
                    source_app=source_app,
                    user=os.environ.get('USERNAME'),
                    session_info="Stored",
                    metadata=row_data
                )
                
        except Exception as e:
            self.logger.debug(f"Error creating entry from row: {e}")
            return None
    
    def get_current_clipboard(self) -> Optional[ClipboardEntry]:
        """Get current Windows clipboard content"""
        try:
            import win32clipboard
            
            win32clipboard.OpenClipboard()
            try:
                data = win32clipboard.GetClipboardData()
                if data:
                    entry = ClipboardEntry(
                        timestamp=datetime.now().isoformat(),
                        content_type="text",
                        content=str(data),
                        content_hash="",
                        size_bytes=len(str(data)),
                        source_app="Windows Clipboard",
                        user=os.environ.get('USERNAME'),
                        session_info="Current"
                    )
                    return entry
            finally:
                win32clipboard.CloseClipboard()
                
        except Exception as e:
            self.logger.warning(f"Could not access current clipboard: {e}")
        
        return None
    
    def _get_current_clipboard(self):
        """Add current clipboard to entries"""
        current = self.get_current_clipboard()
        if current:
            self.entries.append(current)
    
    def detect_clipboard_managers(self) -> List[str]:
        """Detect installed clipboard managers"""
        detected = []
        
        managers = {
            "Ditto": "%APPDATA%/Ditto/",
            "ClipX": "%APPDATA%/ClipX/",
            "Clipboard Master": "%APPDATA%/Clipboard Master/",
            "CLCL": "%APPDATA%/CLCL/"
        }
        
        for manager, path_template in managers.items():
            path = os.path.expandvars(path_template)
            if os.path.exists(path):
                detected.append(manager)
        
        return detected

# =====================================

# File: src/analyzers/pattern_analyzer.py
import re
from typing import List, Dict, Any
from collections import defaultdict, Counter
import logging

from ..core.data_models import ClipboardEntry

class PatternAnalyzer:
    """Analyzes clipboard data for suspicious patterns and sensitive information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sensitive_patterns = self._load_sensitive_patterns()
    
    def _load_sensitive_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for detecting sensitive information"""
        return {
            'passwords': [
                r'password\s*[:=]\s*\S+',
                r'pwd\s*[:=]\s*\S+',
                r'pass\s*[:=]\s*\S+',
                r'secret\s*[:=]\s*\S+'
            ],
            'tokens': [
                r'token\s*[:=]\s*[a-zA-Z0-9+/=]{20,}',
                r'api[_-]?key\s*[:=]\s*[a-zA-Z0-9]+',
                r'access[_-]?token\s*[:=]\s*[a-zA-Z0-9+/=]{20,}'
            ],
            'credentials': [
                r'username\s*[:=]\s*\S+',
                r'user\s*[:=]\s*\S+',
                r'login\s*[:=]\s*\S+'
            ],
            'financial': [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'account\s*[:=]\s*\d+'
            ],
            'personal': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'  # Phone
            ]
        }
    
    def analyze(self, entries: List[ClipboardEntry]) -> Dict[str, Any]:
        """Perform comprehensive pattern analysis"""
        self.logger.info(f"Analyzing patterns in {len(entries)} clipboard entries")
        
        results = {
            'suspicious_patterns': [],
            'data_types': defaultdict(int),
            'frequent_sources': defaultdict(int),
            'potential_exfiltration': [],
            'sensitive_data_found': defaultdict(list),
            'usage_statistics': self._calculate_usage_stats(entries),
            'anomalies': self._detect_anomalies(entries)
        }
        
        for entry in entries:
            # Count data types and sources
            results['data_types'][entry.content_type] += 1
            results['frequent_sources'][entry.source_app or 'Unknown'] += 1
            
            # Check for sensitive patterns
            sensitive_matches = self._check_sensitive_patterns(entry)
            if sensitive_matches:
                results['sensitive_data_found'].update(sensitive_matches)
                results['suspicious_patterns'].append({
                    'type': 'sensitive_data',
                    'entry_hash': entry.content_hash,
                    'timestamp': entry.timestamp,
                    'patterns': list(sensitive_matches.keys()),
                    'source': entry.source_app
                })
            
            # Check for potential exfiltration
            if self._is_potential_exfiltration(entry):
                results['potential_exfiltration'].append({
                    'type': 'suspicious_session',
                    'entry_hash': entry.content_hash,
                    'timestamp': entry.timestamp,
                    'session_info': entry.session_info,
                    'source': entry.source_app,
                    'reason': self._get_exfiltration_reason(entry)
                })
        
        self.logger.info(f"Pattern analysis complete. Found {len(results['suspicious_patterns'])} suspicious patterns")
        return results
    
    def _check_sensitive_patterns(self, entry: ClipboardEntry) -> Dict[str, List[str]]:
        """Check entry content against sensitive data patterns"""
        matches = defaultdict(list)
        content_lower = entry.content.lower()
        
        for category, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    matches[category].append(pattern)
        
        return dict(matches)
    
    def _is_potential_exfiltration(self, entry: ClipboardEntry) -> bool:
        """Determine if entry indicates potential data exfiltration"""
        indicators = [
            entry.session_info and 'remote' in entry.session_info.lower(),
            entry.source_app and any(remote_app in entry.source_app.lower() 
                                   for remote_app in ['rdp', 'vnc', 'teamviewer', 'ssh']),
            len(entry.content) > 10000,  # Large clipboard transfers
            entry.content_type in ['file', 'image'] and len(entry.content) > 1000
        ]
        
        return any(indicators)
    
    def _get_exfiltration_reason(self, entry: ClipboardEntry) -> str:
        """Get reason why entry is flagged as potential exfiltration"""
        reasons = []
        
        if entry.session_info and 'remote' in entry.session_info.lower():
            reasons.append("Remote session detected")
        
        if len(entry.content) > 10000:
            reasons.append("Large data transfer")
        
        if entry.source_app and any(app in entry.source_app.lower() 
                                  for app in ['rdp', 'vnc', 'teamviewer']):
            reasons.append("Remote access application")
        
        return "; ".join(reasons) if reasons else "Suspicious activity pattern"
    
    def _calculate_usage_stats(self, entries: List[ClipboardEntry]) -> Dict[str, Any]:
        """Calculate clipboard usage statistics"""
        if not entries:
            return {}
        
        content_sizes = [entry.size_bytes for entry in entries if entry.size_bytes]
        
        return {
            'total_entries': len(entries),
            'avg_content_size': sum(content_sizes) / len(content_sizes) if content_sizes else 0,
            'max_content_size': max(content_sizes) if content_sizes else 0,
            'most_active_app': Counter(e.source_app for e in entries if e.source_app).most_common(1),
            'content_type_distribution': dict(Counter(e.content_type for e in entries)),
            'entries_per_hour': self._calculate_entries_per_hour(entries)
        }
    
    def _calculate_entries_per_hour(self, entries: List[ClipboardEntry]) -> Dict[str, int]:
        """Calculate clipboard activity by hour"""
        from datetime import datetime
        
        hourly_counts = defaultdict(int)
        
        for entry in entries:
            try:
                timestamp = datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00'))
                hour_key = f"{timestamp.hour:02d}:00"
                hourly_counts[hour_key] += 1
            except:
                continue
        
        return dict(hourly_counts)
    
    def _detect_anomalies(self, entries: List[ClipboardEntry]) -> List[Dict[str, Any]]:
        """Detect anomalous clipboard behavior"""
        anomalies = []
        
        if not entries:
            return anomalies
        
        # Detect unusually large clipboard items
        sizes = [e.size_bytes for e in entries if e.size_bytes > 0]
        if sizes:
            avg_size = sum(sizes) / len(sizes)
            size_threshold = avg_size * 10  # 10x average
            
            for entry in entries:
                if entry.size_bytes > size_threshold:
                    anomalies.append({
                        'type': 'unusually_large_content',
                        'entry_hash': entry.content_hash,
                        'timestamp': entry.timestamp,
                        'size': entry.size_bytes,
                        'threshold': size_threshold
                    })
        
        # Detect rapid clipboard activity (potential automation)
        # Group entries by minute and look for high-frequency periods
        from collections import defaultdict
        from datetime import datetime
        
        minute_counts = defaultdict(int)
        for entry in entries:
            try:
                timestamp = datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00'))
                minute_key = timestamp.strftime('%Y-%m-%d %H:%M')
                minute_counts[minute_key] += 1
            except:
                continue
        
        # Flag minutes with more than 10 clipboard operations
        for minute, count in minute_counts.items():
            if count > 10:
                anomalies.append({
                    'type': 'high_frequency_activity',
                    'timestamp': minute,
                    'entry_count': count,
                    'threshold': 10
                })
        
        return anomalies

# =====================================

# File: src/analyzers/timeline_analyzer.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from ..core.data_models import ClipboardEntry

class TimelineAnalyzer:
    """Analyzes clipboard data chronologically"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_timeline(self, entries: List[ClipboardEntry]) -> List[Dict[str, Any]]:
        """Create chronological timeline of clipboard events"""
        self.logger.info(f"Creating timeline from {len(entries)} entries")
        
        # Sort entries by timestamp
        sorted_entries = sorted(entries, key=lambda x: self._parse_timestamp(x.timestamp))
        
        timeline = []
        for i, entry in enumerate(sorted_entries):
            timeline_event = {
                'sequence': i + 1,
                'timestamp': entry.timestamp,
                'content_type': entry.content_type,
                'source_app': entry.source_app or 'Unknown',
                'user': entry.user or 'Unknown',
                'session_info': entry.session_info or 'Local',
                'content_preview': self._create_content_preview(entry.content),
                'content_hash': entry.content_hash,
                'size_bytes': entry.size_bytes,
                'time_since_previous': self._calculate_time_gap(
                    sorted_entries[i-1].timestamp if i > 0 else None,
                    entry.timestamp
                )
            }
            timeline.append(timeline_event)
        
        self.logger.info("Timeline creation complete")
        return timeline
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse various timestamp formats"""
        try:
            # Handle ISO format with timezone
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            elif '+' in timestamp_str[-6:] or '-' in timestamp_str[-6:]:
                # Already has timezone
                pass
            else:
                # Assume local timezone
                timestamp_str += '+00:00'
            
            return datetime.fromisoformat(timestamp_str)
        except:
            # Fallback to current time if parsing fails
            return datetime.now()
    
    def _create_content_preview(self, content: str, max_length: int = 100) -> str:
        """Create a safe preview of clipboard content"""
        if not content:
            return "[Empty]"
        
        # Clean up the content for preview
        cleaned = content.replace('\n', ' ').replace('\r', ' ').strip()
        
        if len(cleaned) <= max_length:
            return cleaned
        
        return cleaned[:max_length] + "..."
    
    def _calculate_time_gap(self, previous_timestamp: str, current_timestamp: str) -> Dict[str, Any]:
        """Calculate time gap between clipboard events"""
        if not previous_timestamp:
            return {"seconds": 0, "human_readable": "First entry"}
        
        try:
            prev_time = self._parse_timestamp(previous_timestamp)
            curr_time = self._parse_timestamp(current_timestamp)
            
            gap = curr_time - prev_time
            gap_seconds = gap.total_seconds()
            
            # Convert to human readable format
            if gap_seconds < 60:
                readable = f"{int(gap_seconds)} seconds"
            elif gap_seconds < 3600:
                readable = f"{int(gap_seconds / 60)} minutes"
            elif gap_seconds < 86400:
                readable = f"{int(gap_seconds / 3600)} hours"
            else:
                readable = f"{int(gap_seconds / 86400)} days"
            
            return {
                "seconds": gap_seconds,
                "human_readable": readable
            }
        except:
            return {"seconds": 0, "human_readable": "Unknown"}

# =====================================

# File: src/utils/config_manager.py
import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

class ConfigManager:
    """Manages configuration settings for the forensics tool"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.default_config_file = self.config_dir / "default.json"
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        default_config = {
            "analysis": {
                "max_entries": 10000,
                "content_preview_length": 1000,
                "enable_pattern_analysis": True,
                "enable_timeline_analysis": True,
                "deep_scan": False
            },
            "platforms": {
                "windows": {
                    "extract_cloud_clipboard": True,
                    "extract_registry": True,
                    "extract_clipboard_managers": True,
                    "managers_to_check": ["Ditto", "ClipX", "Clipboard Master"]
                },
                "linux": {
                    "extract_x11_clipboard": True,
                    "extract_clipboard_managers": True,
                    "check_remote_sessions": True,
                    "managers_to_check": ["CopyQ", "Clipit", "Parcellite"]
                },
                "macos": {
                    "extract_pasteboard": True,
                    "extract_clipboard_managers": True,
                    "extract_system_logs": True,
                    "managers_to_check": ["CopyClip", "Paste", "Alfred"]
                }
            },
            "security": {
                "hash_sensitive_content": True,
                "redact_passwords": True,
                "max_content_size": 1048576  # 1MB
            },
            "output": {
                "format": "json",
                "include_metadata": True,
                "compress_reports": False,
                "timestamp_format": "iso"
            },
            "logging": {
                "level": "INFO",
                "file_logging": True,
                "console_logging": True
            }
        }
        
        # Save default config if it doesn't exist
        if not self.default_config_file.exists():
            self.save_config(default_config, str(self.default_config_file))
        
        return default_config
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Merge with default config to ensure all keys exist
            default_config = self.get_default_config()
            merged_config = self._merge_configs(default_config, config)
            
            self.logger.info(f"Loaded configuration from {config_path}")
            return merged_config
            
        except Exception as e:
            self.logger.error(f"Error loading config from {config_path}: {e}")
            self.logger.info("Using default configuration")
            return self.get_default_config()
    
    def save_config(self, config: Dict[str, Any], config_path: str):
        """Save configuration to file"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved configuration to {config_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving config to {config_path}: {e}")
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged

# =====================================

# File: src/utils/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(level: str = 'INFO'):
    """Setup logging configuration"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"clipboard_forensics_{timestamp}.log"
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Setup root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set third-party library log levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
    
    return logger