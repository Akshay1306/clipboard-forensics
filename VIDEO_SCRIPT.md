# Video Demo Script (3-5 minutes)

## Opening (0:00-0:30)
"Hello, I'm Akshaydeep Hazarika, and I'm presenting the Clipboard Forensics Tool - 
a professional digital forensics application for analyzing clipboard history 
and detecting sensitive data exposure.

In this demo, I'll show you how this tool automatically extracts clipboard 
data from multiple sources, detects security risks, and generates 
professional forensic reports."

## Problem Context (0:30-1:00)
"Every day, users copy sensitive information to their clipboard - passwords, 
credit cards, confidential documents. This data persists in clipboard history, 
creating a security risk. My tool addresses this by providing automated 
forensic analysis of clipboard data."

## Tool Launch (1:00-1:30)
[Screen: Show desktop]
"The tool provides both GUI and CLI interfaces. Let me launch the GUI."

[Screen: Click run.bat or python src/main.py --gui]

"Here's the interface - clean, professional, and easy to use."

## Live Analysis (1:30-2:30)
[Screen: Notepad with sensitive data]
"First, I'll copy some sample data that contains sensitive information..."

[Screen: Copy text with username, password, email, credit card]

[Screen: Click "Run Analysis" button]
"Now I'll run the analysis. Notice the real-time logging showing 
what's being extracted..."

[Screen: Show progress]

"Analysis complete in under 3 seconds!"

## Results (2:30-4:00)
[Screen: Open HTML report]
"Let's look at the report. Here we see:

1. Risk Score of 85/100 - indicating high-risk content
2. The tool automatically detected credentials, financial data, and personal info
3. Activity charts showing when clipboard operations occurred
4. Security recommendations

The search functionality lets me filter entries..."
[Demonstrate search]

"And I can filter by content type..."
[Demonstrate filter buttons]

## Technical Highlights (4:00-4:30)
"From a technical perspective, this tool:
- Extracts from multiple Windows sources
- Uses regex pattern matching for detection
- Calculates weighted risk scores
- Generates both JSON and HTML reports
- Has 100% test pass rate"

## Closing (4:30-5:00)
"This tool is ready for real-world use in digital forensics, 
security audits, and incident response. It demonstrates a complete 
software development cycle from requirements to deployment.

Thank you for watching. Documentation and source code are available 
in the project repository."

[Screen: Show final slide with contact info]