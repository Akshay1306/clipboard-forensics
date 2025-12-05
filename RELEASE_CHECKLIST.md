# Release Checklist

## Before Release
- [ ] All tests passing
- [ ] GUI launches without errors
- [ ] CLI generates both JSON and HTML reports
- [ ] HTML reports display correctly in browsers
- [ ] Documentation complete
- [ ] Sample data tested
- [ ] Requirements.txt accurate

## Files to Include
- [ ] All source code
- [ ] Tests
- [ ] Documentation (README, USER_GUIDE, DEMO)
- [ ] Install scripts (install.bat, run.bat)
- [ ] requirements.txt
- [ ] LICENSE
- [ ] .gitignore

## Quality Checks
- [ ] No hardcoded passwords or keys
- [ ] No personal data in code
- [ ] Logging works correctly
- [ ] Error handling graceful
- [ ] Performance acceptable (<5 seconds for analysis)

## Deliverables
- [ ] GitHub repository (public/private)
- [ ] Demo video (2-5 minutes)
- [ ] Technical report (2-3 pages)
- [ ] Presentation slides (10-15 slides)
```

### **Task 6: Create Quick Reference (15 min)**

**Create `QUICK_START.txt`:**
```
═══════════════════════════════════════════
 CLIPBOARD FORENSICS TOOL - QUICK START
═══════════════════════════════════════════

INSTALLATION:
1. Double-click: install.bat
2. Wait for completion

RUNNING:
- GUI: Double-click run.bat
- CLI: python src/main.py --cli

TESTING:
python tests/run_tests.py

OUTPUT:
Check: output/ folder for reports
- .json = Data
- .html = Visual report (open in browser)

COMMON ISSUES:
- "python not found" → Install Python 3.8+
- "module not found" → Run install.bat
- "No entries" → Copy something first

FEATURES:
✓ Detects passwords, credit cards, emails
✓ Risk scoring
✓ Activity charts
✓ Search & filter

LEGAL:
⚠ Authorized use only
⚠ Obtain permission first

SUPPORT:
See docs/USER_GUIDE.md