# File: src/platforms/base_analyzer.py
from abc import ABC, abstractmethod
from typing import List, Optional
import logging

class BaseAnalyzer(ABC):
    """Abstract base class for platform-specific analyzers"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.entries = []
    
    @abstractmethod
    def extract_clipboard_data(self) -> List:
        """Extract clipboard data specific to this platform"""
        pass
    
    @abstractmethod
    def get_current_clipboard(self) -> Optional:
        """Get current clipboard content"""
        pass
    
    @abstractmethod
    def detect_clipboard_managers(self) -> List[str]:
        """Detect installed clipboard managers"""
        pass