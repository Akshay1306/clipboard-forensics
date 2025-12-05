# File: src/core/data_models.py (Clean version - no circular imports)
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import hashlib
import json

@dataclass
class ClipboardEntry:
    """Represents a single clipboard entry with forensic metadata"""
    timestamp: str
    content_type: str  # text, image, file, html, etc.
    content: str
    content_hash: str
    size_bytes: int
    source_app: Optional[str] = None
    user: Optional[str] = None
    session_info: Optional[str] = None
    metadata: Optional[Dict] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClipboardEntry':
        """Create instance from dictionary"""
        return cls(**data)
    
    def __post_init__(self):
        """Generate content hash if not provided"""
        if not self.content_hash and self.content:
            self.content_hash = hashlib.sha256(
                self.content.encode('utf-8', errors='ignore')
            ).hexdigest()[:16]

@dataclass  
class ForensicsReport:
    """Complete forensics analysis report"""
    metadata: Dict[str, Any]
    entries: List[ClipboardEntry]
    statistics: Dict[str, int]
    timeline: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    generated_at: str
    
    def to_json(self) -> str:
        """Convert report to JSON string"""
        report_dict = {
            'metadata': self.metadata,
            'entries': [entry.to_dict() for entry in self.entries],
            'statistics': self.statistics,
            'timeline': self.timeline,
            'analysis': self.analysis,
            'generated_at': self.generated_at
        }
        return json.dumps(report_dict, indent=2, ensure_ascii=False)
    
    def save(self, filepath: str):
        """Save report to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())