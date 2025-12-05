# File: src/platforms/windows_analyzer.py
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import logging

# Add src to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from platforms.base_analyzer import BaseAnalyzer
from core.data_models import ClipboardEntry

class WindowsAnalyzer(BaseAnalyzer):
    """Windows-specific clipboard analysis"""
    
    def __init__(self):
        super().__init__()
        self.user_profile = os.environ.get('USERPROFILE', '')
        self.logger.info(f"Windows analyzer initialized")
        
    def extract_clipboard_data(self) -> List[ClipboardEntry]:
        """Main extraction method for Windows"""
        self.logger.info("Starting Windows clipboard extraction")
        
        # Get current clipboard
        self._get_current_clipboard()
        
        # Try cloud clipboard extraction
        self._extract_cloud_clipboard()
        
        # Extract registry data
        self._extract_registry_clipboard()
        
        self.logger.info(f"Extracted {len(self.entries)} total entries from Windows")
        return self.entries
    
    def get_current_clipboard(self) -> Optional[ClipboardEntry]:
        """Get current Windows clipboard content"""
        try:
            import subprocess
            result = subprocess.run([
                'powershell.exe', '-Command', 'Get-Clipboard'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                content = result.stdout.strip()
                entry = ClipboardEntry(
                    timestamp=datetime.now().isoformat(),
                    content_type="text",
                    content=content,
                    content_hash="",
                    size_bytes=len(content),
                    source_app="Windows Clipboard",
                    user=os.environ.get('USERNAME'),
                    session_info="Current"
                )
                return entry
        except Exception as e:
            self.logger.warning(f"Could not access clipboard: {e}")
        
        return None
    
    def _get_current_clipboard(self):
        """Add current clipboard to entries"""
        current = self.get_current_clipboard()
        if current:
            self.entries.append(current)
            self.logger.info("Successfully extracted current clipboard")
        else:
            self.logger.warning("No current clipboard content found")
    
    def _find_clipboard_database(self):
        """Search for clipboard database in various locations"""
        possible_paths = [
            Path(self.user_profile) / "AppData/Local/Microsoft/Windows/CloudClipboard/clipboard.db",
            Path(self.user_profile) / "AppData/Local/Microsoft/Clipboard/clipboard.db",
            Path(self.user_profile) / "AppData/Local/Packages/Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy/LocalState/Clipboard",
        ]
        
        for path in possible_paths:
            if path.exists():
                self.logger.info(f"Found clipboard database at: {path}")
                return path
            
            # Also check for .db files in the directory
            if path.parent.exists():
                for db_file in path.parent.glob("*.db"):
                    self.logger.info(f"Found potential clipboard database: {db_file}")
                    return db_file
        
        return None
    
    def _extract_cloud_clipboard(self):
        """Extract Windows 10/11 Cloud Clipboard data"""
        try:
            clipboard_db = self._find_clipboard_database()
            
            if not clipboard_db:
                self.logger.info("Cloud clipboard database not found")
                return
                
            self.logger.info(f"Analyzing clipboard database: {clipboard_db}")
            
            conn = sqlite3.connect(str(clipboard_db))
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.logger.debug(f"Tables found: {tables}")
            
            # Extract from each table
            for table in tables:
                try:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                    rows = cursor.fetchall()
                    
                    self.logger.info(f"Found {len(rows)} rows in table '{table}'")
                    
                    for row in rows:
                        entry = self._parse_cloud_clipboard_row(row, columns, table)
                        if entry:
                            self.entries.append(entry)
                            
                except Exception as e:
                    self.logger.debug(f"Could not read table {table}: {e}")
            
            conn.close()
            cloud_entries = len([e for e in self.entries if 'Cloud' in str(e.source_app)])
            self.logger.info(f"Cloud clipboard extraction complete - found {cloud_entries} entries")
            
        except Exception as e:
            self.logger.error(f"Cloud clipboard extraction failed: {e}")
    
    def _parse_cloud_clipboard_row(self, row, columns, table_name):
        """Parse a row from cloud clipboard database"""
        try:
            row_dict = dict(zip(columns, row))
            
            # Try to extract content
            content = ""
            for col in ['content', 'text', 'data', 'payload', 'Content', 'Text']:
                if col in row_dict and row_dict[col]:
                    raw_content = row_dict[col]
                    # Handle binary data
                    if isinstance(raw_content, bytes):
                        try:
                            content = raw_content.decode('utf-8', errors='ignore')[:1000]
                        except:
                            content = str(raw_content)[:1000]
                    else:
                        content = str(raw_content)[:1000]
                    
                    if content.strip():
                        break
            
            if not content or len(content.strip()) < 3:
                return None
            
            # Try to extract timestamp
            timestamp = datetime.now().isoformat()
            for col in ['timestamp', 'time', 'created_at', 'Timestamp', 'CreatedTime']:
                if col in row_dict and row_dict[col]:
                    try:
                        # Try different timestamp formats
                        ts_value = row_dict[col]
                        if isinstance(ts_value, (int, float)):
                            # Unix timestamp
                            timestamp = datetime.fromtimestamp(ts_value).isoformat()
                        else:
                            # String timestamp
                            timestamp = str(ts_value)
                        break
                    except:
                        pass
            
            return ClipboardEntry(
                timestamp=timestamp,
                content_type="text",
                content=content,
                content_hash="",
                size_bytes=len(content),
                source_app="Windows Cloud Clipboard",
                user=os.environ.get('USERNAME'),
                session_info=f"Table: {table_name}",
                metadata=row_dict
            )
        except Exception as e:
            self.logger.debug(f"Could not parse row: {e}")
            return None
    
    def _extract_registry_clipboard(self):
        """Extract clipboard-related data from Windows Registry"""
        try:
            import winreg
            
            registry_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Clipboard"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\CloudClipboard"),
            ]
            
            for root_key, path in registry_paths:
                try:
                    with winreg.OpenKey(root_key, path) as key:
                        info = winreg.QueryInfoKey(key)
                        num_values = info[1]
                        
                        self.logger.info(f"Reading {num_values} registry values from {path}")
                        
                        for i in range(num_values):
                            try:
                                name, value, reg_type = winreg.EnumValue(key, i)
                                
                                entry = ClipboardEntry(
                                    timestamp=datetime.now().isoformat(),
                                    content_type="registry_setting",
                                    content=f"{name}: {value}",
                                    content_hash="",
                                    size_bytes=len(str(value)),
                                    source_app="Windows Registry",
                                    user=os.environ.get('USERNAME'),
                                    session_info=f"Registry: {path}",
                                    metadata={"key": path, "name": name, "type": reg_type}
                                )
                                self.entries.append(entry)
                            except:
                                continue
                                
                except FileNotFoundError:
                    self.logger.debug(f"Registry path not found: {path}")
                except Exception as e:
                    self.logger.debug(f"Could not read registry {path}: {e}")
                    
        except ImportError:
            self.logger.warning("winreg not available")
        except Exception as e:
            self.logger.error(f"Registry extraction failed: {e}")
    
    def detect_clipboard_managers(self) -> List[str]:
        """Detect installed clipboard managers"""
        detected = []
        
        managers = {
            "Ditto": "%APPDATA%/Ditto/",
            "ClipX": "%APPDATA%/ClipX/",
            "Clipboard Master": "%APPDATA%/Clipboard Master/",
        }
        
        for manager, path_template in managers.items():
            path = os.path.expandvars(path_template)
            if os.path.exists(path):
                detected.append(manager)
                self.logger.info(f"Detected clipboard manager: {manager}")
        
        return detected