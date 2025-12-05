# 🔍 Cross-Platform Clipboard Forensics Tool

Professional digital forensics tool for analyzing Windows clipboard history and detecting sensitive data exposure.

## ✨ Features

- **Multi-Source Extraction**: Current clipboard, Registry, Cloud clipboard
- **Smart Pattern Detection**: Automatically detects passwords, credit cards, emails, URLs
- **Risk Analysis**: Calculates security risk score (0-100)
- **Visual Reports**: Interactive HTML reports with charts and search
- **Timeline Analysis**: Hourly activity patterns and statistics
- **Dual Interface**: Both GUI and CLI modes

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone <your-repo-url>
cd clipboard-forensics

# Run installer
install.bat
```

### Usage

**GUI Mode (Easiest):**
```bash
run.bat
# or
python src/main.py --gui
```

**CLI Mode:**
```bash
python src/main.py --cli --output results/
```

## 📊 What Gets Analyzed

1. **Current Clipboard**: Active clipboard content
2. **Windows Registry**: Clipboard configuration and settings
3. **Cloud Clipboard**: History (if enabled)
4. **Pattern Detection**: Sensitive data identification
5. **Activity Patterns**: Usage statistics and timelines

## 🔒 Security Features

- Detects passwords, API keys, tokens
- Identifies credit cards and SSNs
- Finds emails and phone numbers
- Risk scoring (0-100 scale)
- Security recommendations

## 📈 Reports

Two report formats generated:
- **JSON**: Machine-readable, complete data
- **HTML**: Human-readable with charts, search, filtering

Sample output:
```
output/clipboard_forensics_20241001_120000.json
output/clipboard_forensics_20241001_120000.html
```

## 🧪 Testing
```bash
python tests/run_tests.py
```

## 📁 Project Structure
```
clipboard-forensics/
├── src/
│   ├── core/              # Forensics engine
│   ├── platforms/         # OS-specific analyzers
│   ├── analyzers/         # Pattern & statistics
│   ├── gui/               # User interface
│   └── utils/             # Report generation
├── tests/                 # Test suite
├── docs/                  # Documentation
├── output/                # Generated reports
└── requirements.txt       # Dependencies
```

## ⚖️ Legal Notice

**For authorized use only**. This tool is designed for:
- Digital forensics investigations
- Security audits
- Incident response
- Educational purposes

Always obtain proper authorization before analyzing any system.

## 🎓 Use Cases

- **Corporate Security**: Detect data leakage
- **Incident Response**: Analyze compromised systems
- **Compliance**: Audit clipboard usage
- **Training**: Demonstrate security risks

## 🔧 System Requirements

- Python 3.8+
- Windows 10/11
- 4GB RAM (recommended)
- 100MB disk space

## 📞 Support

For issues or questions, see `docs/USER_GUIDE.md`

## 📜 License

MIT License - See LICENSE file

## 👨‍💻 Author

Your Name - 2-Month Forensics Project

---

**Project Status**: ✅ Complete  
**Test Coverage**: 13/13 tests passing  
**Platforms**: Windows (Linux/macOS planned)