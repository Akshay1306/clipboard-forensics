# File: src/main.py
#!/usr/bin/env python3
"""
Cross-Platform Clipboard Forensics Tool
Main entry point for the application
"""

import sys
import argparse
import os
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Cross-Platform Clipboard Forensics Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --gui                    # Launch GUI interface
  %(prog)s --cli                    # Run CLI analysis
  %(prog)s --output results/        # Specify output directory
  %(prog)s --config custom.json     # Use custom configuration
        """
    )
    
    parser.add_argument(
        '--gui', action='store_true',
        help='Launch GUI interface (default mode)'
    )
    
    parser.add_argument(
        '--cli', action='store_true',
        help='Run command-line interface'
    )
    
    parser.add_argument(
        '--output', '-o', type=str, default='output/',
        help='Output directory for reports (default: output/)'
    )
    
    parser.add_argument(
        '--config', '-c', type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--platform', type=str, choices=['windows', 'linux', 'darwin', 'auto'],
        default='auto', help='Target platform (auto-detect by default)'
    )
    
    return parser.parse_args()

def setup_logging(verbose=False):
    """Setup basic logging"""
    import logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def get_default_config():
    """Get default configuration"""
    return {
        "analysis": {
            "max_entries": 10000,
            "enable_pattern_analysis": True,
            "enable_timeline_analysis": True
        },
        "platforms": {
            "windows": {
                "extract_cloud_clipboard": True,
                "extract_registry": True,
                "extract_clipboard_managers": True
            }
        },
        "security": {
            "hash_sensitive_content": True,
            "redact_passwords": True
        }
    }

def run_cli_analysis(config: dict, output_dir: str, logger):
    """Run command-line analysis"""
    print("Cross-Platform Clipboard Forensics Tool")
    print("=" * 50)
    
    try:
        # Import forensics engine
        from core.forensics_engine import ForensicsEngine
        
        # Initialize forensics engine
        logger.info("Initializing forensics engine...")
        engine = ForensicsEngine(config)
        
        # Perform analysis
        logger.info("Starting analysis...")
        report = engine.analyze()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"clipboard_forensics_{timestamp}.json")
        
        logger.info(f"Saving report to {report_path}")
        report.save(report_path)

        # Add these lines:
        # Generate HTML report
        from utils.report_generator import HTMLReportGenerator
        html_path = report_path.replace('.json', '.html')
        html_gen = HTMLReportGenerator()
        html_gen.generate(report, html_path)
        logger.info(f"HTML report saved to {html_path}")

        print(f"Report saved: {report_path}")
        print(f"HTML report: {html_path}")  # Show both paths
        
        # Display summary
        print(f"\n[SUCCESS] Analysis Complete!")
        print(f"Platform: {report.metadata.get('platform', 'Unknown')}")
        print(f"Total entries: {report.metadata.get('total_entries', 0)}")
        print(f"Report saved: {report_path}")
        
        # Show alerts if any
        analysis = report.analysis
        if analysis.get('suspicious_patterns'):
            print(f"[ALERT] {len(analysis['suspicious_patterns'])} suspicious patterns detected!")
        
        if analysis.get('potential_exfiltration'):
            print(f"[ALERT] {len(analysis['potential_exfiltration'])} potential data exfiltration indicators!")
        
        return 0
            
    except ImportError as e:
        print(f"[ERROR] Missing component: {e}")
        print("Some components are not yet implemented.")
        return 1
    except Exception as e:
        print(f"[ERROR] Error during analysis: {e}")
        logger.exception("Analysis failed")
        return 1

def run_gui_mode(config: dict, logger):
    """Run GUI interface"""
    try:
        print("Launching GUI interface...")
        
        # Try to import GUI
        try:
            from gui.main_window import ClipboardForensicsGUI
            app = ClipboardForensicsGUI(config)
            app.run()
            return 0
        except ImportError:
            print("[INFO] GUI components not available yet.")
            print("GUI will be implemented in Week 6.")
            print("For now, try: python src/main.py --cli")
            return 1
            
    except Exception as e:
        print(f"[ERROR] GUI error: {e}")
        logger.exception("GUI failed")
        return 1

def main():
    """Main application entry point"""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    logger.info("Starting Clipboard Forensics Tool")
    
    # Load configuration
    if args.config and os.path.exists(args.config):
        try:
            import json
            with open(args.config, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded config from {args.config}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            config = get_default_config()
    else:
        config = get_default_config()
    
    # Override platform if specified
    if args.platform != 'auto':
        config['target_platform'] = args.platform
    
    # Determine interface mode
    if args.cli:
        return run_cli_analysis(config, args.output, logger)
    else:
        # Default to GUI mode, fallback to CLI if GUI fails
        result = run_gui_mode(config, logger)
        if result != 0:
            print("\nFalling back to CLI mode...")
            return run_cli_analysis(config, args.output, logger)
        return result

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)

# =====================================

# File: project_status.py
#!/usr/bin/env python3
"""
Quick project status check
"""
import os
from pathlib import Path
from datetime import datetime

def check_project_status():
    """Check basic project status"""
    project_root = Path.cwd()
    
    print("🔍 Clipboard Forensics - Quick Status Check")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project root: {project_root}")
    print()
    
    # Check key files
    key_files = {
        "Core": [
            "src/core/data_models.py",
            "src/core/forensics_engine.py"
        ],
        "Platforms": [
            "src/platforms/base_analyzer.py",
            "src/platforms/windows_analyzer.py"
        ],
        "Main": [
            "src/main.py",
            "requirements.txt"
        ],
        "Tests": [
            "tests/test_simple.py",
            "tests/test_data_models.py"
        ]
    }
    
    total_files = 0
    found_files = 0
    
    for category, files in key_files.items():
        print(f"📋 {category}:")
        for file_path in files:
            total_files += 1
            full_path = project_root / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                print(f"  ✅ {file_path} ({size} bytes)")
                found_files += 1
            else:
                print(f"  ❌ {file_path} (missing)")
        print()
    
    # Calculate completion percentage
    completion = (found_files / total_files) * 100
    print(f"📊 Project Completion: {completion:.1f}% ({found_files}/{total_files} files)")
    
    # Check if tests work
    print("\n🧪 Quick Test Check:")
    try:
        import subprocess
        result = subprocess.run([
            'python', '-m', 'pytest', 'tests/test_simple.py', '-v'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Basic tests passing")
        else:
            print("  ❌ Tests failing")
            print(f"  Error: {result.stderr}")
    except Exception as e:
        print(f"  ⚠️  Could not run tests: {e}")
    
    print("\n💡 Next Steps:")
    if found_files < total_files:
        print("  1. Create missing files")
        print("  2. Run tests: python tests/run_tests.py")
    else:
        print("  1. Test CLI: python src/main.py --cli")
        print("  2. Check functionality: python src/main.py --help")
    
    print("  3. Continue with Week 2 implementation")

if __name__ == "__main__":
    check_project_status()

# =====================================

# File: src/core/forensics_engine.py (Complete version)
import platform
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import logging

from .data_models import ClipboardEntry, ForensicsReport

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
            from ..platforms.windows_analyzer import WindowsAnalyzer
            analyzer = WindowsAnalyzer()
            platform_entries = analyzer.extract_clipboard_data()
            self.entries.extend(platform_entries)
            self.stats['platform_entries'] = len(platform_entries)
            self.logger.info(f"Extracted {len(platform_entries)} entries from Windows")
        except ImportError:
            self.logger.warning("Windows analyzer not available")
        except Exception as e:
            self.logger.error(f"Windows extraction failed: {e}")
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in clipboard data"""
        try:
            from ..analyzers.pattern_analyzer import PatternAnalyzer
            analyzer = PatternAnalyzer()
            return analyzer.analyze(self.entries)
        except ImportError:
            self.logger.warning("Pattern analyzer not available")
            return self._empty_pattern_results()
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
            return self._empty_pattern_results()
    
    def _create_timeline(self) -> List[Dict[str, Any]]:
        """Create timeline of clipboard events"""
        try:
            from ..analyzers.timeline_analyzer import TimelineAnalyzer
            analyzer = TimelineAnalyzer()
            return analyzer.create_timeline(self.entries)
        except ImportError:
            self.logger.warning("Timeline analyzer not available")
            return []
        except Exception as e:
            self.logger.error(f"Timeline creation failed: {e}")
            return []
    
    def _empty_pattern_results(self):
        """Return empty pattern analysis results"""
        return {
            'suspicious_patterns': [],
            'data_types': defaultdict(int),
            'frequent_sources': defaultdict(int),
            'potential_exfiltration': [],
            'sensitive_data_found': defaultdict(list)
        }
    
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
        
        return ForensicsReport(
            metadata=metadata,
            entries=self.entries,
            statistics=dict(self.stats),
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