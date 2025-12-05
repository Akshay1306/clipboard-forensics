# Live Demo Script

## Setup (2 minutes)
1. Open PowerShell
2. Navigate to project: `cd clipboard-forensics`
3. Launch GUI: `python src/main.py --gui`

## Demo Scenario (5 minutes)

### Step 1: Show Tool Interface
- Professional GUI with clear controls
- Explain analysis, output folder, log display

### Step 2: Copy Sensitive Data
Copy this to clipboard:
```
username: admin
password: Secret123!
email: john.doe@company.com
card: 4532-1234-5678-9010
api_key: sk_live_abc123xyz789
```

### Step 3: Run Analysis
- Click "Run Analysis"
- Show real-time logs
- Wait for completion (2-3 seconds)

### Step 4: Review HTML Report
- Click "Open Output Folder"
- Open HTML report in browser
- Demonstrate:
  - Risk Score (should be HIGH ~70-90)
  - Detected patterns (credentials, financial)
  - Activity charts
  - Search functionality
  - Filter buttons

### Step 5: Show JSON Report
- Open JSON in text editor
- Show structured data format
- Explain programmatic use cases

## Key Points to Emphasize

1. **Automatic Detection**: Tool found all sensitive data automatically
2. **Risk Scoring**: Calculated risk based on content
3. **Actionable**: Provides security recommendations
4. **Professional**: Production-quality reports
5. **Fast**: Analysis completes in seconds

## Questions to Anticipate

**Q: What platforms?**
A: Currently Windows, designed for cross-platform

**Q: Can it recover old clipboard data?**
A: Yes, if clipboard history is enabled

**Q: Legal to use?**
A: Yes, for authorized systems only

**Q: Accuracy?**
A: Pattern matching, may have false positives but comprehensive