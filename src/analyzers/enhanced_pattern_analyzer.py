# File: src/analyzers/enhanced_pattern_analyzer.py
import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import logging

class EnhancedPatternAnalyzer:
    """Advanced pattern detection for sensitive data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Load comprehensive detection patterns"""
        return {
            'credentials': [
                (r'password\s*[:=]\s*[^\s]+', 'Password detected'),
                (r'api[_-]?key\s*[:=]\s*[^\s]+', 'API key detected'),
                (r'token\s*[:=]\s*[^\s]+', 'Token detected'),
                (r'secret\s*[:=]\s*[^\s]+', 'Secret detected'),
            ],
            'financial': [
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'Credit card number'),
                (r'\b\d{3}-\d{2}-\d{4}\b', 'Social Security Number'),
                (r'CVV\s*[:=]?\s*\d{3,4}', 'CVV code'),
            ],
            'personal': [
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email address'),
                (r'\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', 'Phone number'),
                (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP address'),
            ],
            'network': [
                (r'https?://[^\s]+', 'URL'),
                (r'\\\\[^\s]+', 'Network path'),
                (r'[A-Za-z]:\\[^\s]+', 'Local file path'),
            ]
        }
    
    def analyze(self, entries: List) -> Dict[str, Any]:
        """Analyze clipboard entries for sensitive patterns"""
        self.logger.info(f"Enhanced pattern analysis on {len(entries)} entries")
        
        results = {
            'findings': [],
            'summary': defaultdict(int),
            'risk_score': 0,
            'recommendations': []
        }
        
        for entry in entries:
            content = getattr(entry, 'content', '')
            if not content:
                continue
            
            # Check all pattern categories
            for category, patterns in self.patterns.items():
                for pattern, description in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        finding = {
                            'category': category,
                            'description': description,
                            'matched_text': match.group()[:50],  # Truncate for safety
                            'entry_hash': getattr(entry, 'content_hash', 'unknown'),
                            'timestamp': getattr(entry, 'timestamp', 'unknown'),
                            'source': getattr(entry, 'source_app', 'unknown')
                        }
                        results['findings'].append(finding)
                        results['summary'][category] += 1
        
        # Calculate risk score
        results['risk_score'] = self._calculate_risk(results['summary'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results['summary'])
        
        self.logger.info(f"Found {len(results['findings'])} sensitive data patterns")
        return results
    
    def _calculate_risk(self, summary: Dict) -> int:
        """Calculate risk score 0-100"""
        weights = {
            'credentials': 30,
            'financial': 40,
            'personal': 15,
            'network': 10
        }
        
        score = 0
        for category, count in summary.items():
            score += weights.get(category, 5) * min(count, 3)
        
        return min(score, 100)
    
    def _generate_recommendations(self, summary: Dict) -> List[str]:
        """Generate security recommendations"""
        recs = []
        
        if summary.get('credentials', 0) > 0:
            recs.append("Credentials detected in clipboard - consider using password manager")
        
        if summary.get('financial', 0) > 0:
            recs.append("Financial data found - ensure clipboard is cleared after use")
        
        if summary.get('personal', 0) > 2:
            recs.append("Multiple personal identifiers found - review data handling practices")
        
        if not recs:
            recs.append("No high-risk patterns detected")
        
        return recs