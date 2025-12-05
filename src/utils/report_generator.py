# File: src/utils/report_generator.py (COMPLETE VERSION)
from datetime import datetime
from pathlib import Path
import html

class HTMLReportGenerator:
    """Generate human-readable HTML reports"""
    
    def __init__(self):
        self.template = self._get_template()
    
    def generate(self, report, output_path: str):
        """Generate HTML report from ForensicsReport object"""
        
        # Build entries HTML
        entries_html = ""
        for i, entry in enumerate(report.entries, 1):
            content = html.escape(entry.content)
            entries_html += f"""
            <div class="entry" data-type="{entry.content_type}">
                <div class="entry-header">
                    <span class="entry-number">#{i}</span>
                    <span class="source">{html.escape(entry.source_app or 'Unknown')}</span>
                    <span class="timestamp">{entry.timestamp}</span>
                </div>
                <div class="content-type">{entry.content_type}</div>
                <div class="content">
                    <pre>{content}</pre>
                </div>
                <div class="entry-footer">
                    Size: {entry.size_bytes} bytes | Hash: {entry.content_hash}
                </div>
            </div>
            """
        
        # Build summary
        summary_html = f"""
        <div class="summary">
            <h2>Analysis Summary</h2>
            <table>
                <tr><td><strong>Platform:</strong></td><td>{report.metadata.get('platform', 'Unknown')}</td></tr>
                <tr><td><strong>User:</strong></td><td>{report.metadata.get('user', 'Unknown')}</td></tr>
                <tr><td><strong>Hostname:</strong></td><td>{report.metadata.get('hostname', 'Unknown')}</td></tr>
                <tr><td><strong>Analysis Time:</strong></td><td>{report.metadata.get('analysis_time', 'Unknown')}</td></tr>
                <tr><td><strong>Total Entries:</strong></td><td>{report.metadata.get('total_entries', 0)}</td></tr>
            </table>
        </div>
        """
        
        # Alerts
        alerts_html = ""
        suspicious = report.analysis.get('suspicious_patterns', [])
        exfiltration = report.analysis.get('potential_exfiltration', [])
        
        if suspicious or exfiltration:
            alerts_html = '<div class="alerts">'
            if suspicious:
                alerts_html += f'<div class="alert warning">Warning: {len(suspicious)} suspicious patterns detected</div>'
            if exfiltration:
                alerts_html += f'<div class="alert danger">Alert: {len(exfiltration)} potential data exfiltration indicators</div>'
            alerts_html += '</div>'
        
        # Risk analysis
        risk_html = ""
        enhanced = report.analysis.get('enhanced', {})
        if enhanced:
            risk_score = enhanced.get('risk_score', 0)
            risk_color = '#28a745' if risk_score < 30 else '#ffc107' if risk_score < 70 else '#dc3545'
            
            risk_html = f"""
            <div class="risk-analysis">
                <h3>Risk Analysis</h3>
                <div class="risk-score" style="color: {risk_color}">
                    Risk Score: {risk_score}/100
                </div>
                <div class="findings-summary">
                    <h4>Sensitive Data Found:</h4>
                    <ul>
            """
            
            summary_dict = enhanced.get('summary', {})
            if summary_dict:
                for category, count in summary_dict.items():
                    risk_html += f"<li>{category.title()}: {count} occurrence(s)</li>"
            else:
                risk_html += "<li>No sensitive data detected</li>"
            
            risk_html += "</ul></div>"
            
            if enhanced.get('recommendations'):
                risk_html += "<h4>Recommendations:</h4><ul>"
                for rec in enhanced['recommendations']:
                    risk_html += f"<li>{rec}</li>"
                risk_html += "</ul>"
            
            risk_html += "</div>"
        
        # Statistics charts
        charts_html = ""
        stats = report.statistics
        if stats and stats.get('hourly_activity'):
            hourly = stats['hourly_activity']
            max_count = max(hourly.values()) if hourly.values() else 1
            
            charts_html = """
            <div class="statistics">
                <h3>Activity Patterns</h3>
                <div class="chart-container">
                    <h4>Clipboard Activity by Hour</h4>
                    <div class="bar-chart">
            """
            
            for hour in range(24):
                count = hourly.get(hour, 0)
                percentage = (count / max_count * 100) if max_count > 0 else 0
                charts_html += f"""
                <div class="bar-item">
                    <div class="bar-label">{hour:02d}:00</div>
                    <div class="bar-container">
                        <div class="bar" style="width: {percentage}%"></div>
                        <span class="bar-value">{count}</span>
                    </div>
                </div>
                """
            
            charts_html += "</div></div>"
            
            # Source distribution
            if stats.get('source_distribution'):
                sources = stats['source_distribution']
                total = sum(sources.values())
                
                charts_html += """
                <div class="chart-container">
                    <h4>Sources Distribution</h4>
                    <div class="pie-chart">
                """
                
                for source, count in sources.items():
                    percentage = (count / total * 100) if total > 0 else 0
                    charts_html += f"""
                    <div class="pie-item">
                        <span class="pie-label">{source}</span>
                        <div class="pie-bar" style="width: {percentage}%"></div>
                        <span class="pie-value">{count} ({percentage:.1f}%)</span>
                    </div>
                    """
                
                charts_html += "</div></div>"
            
            charts_html += "</div>"
        
        # Fill template
        html_content = self.template.format(
            title="Clipboard Forensics Report",
            generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=summary_html,
            alerts=alerts_html,
            risk=risk_html,
            charts=charts_html,
            entries=entries_html
        )
        
        # Save
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _get_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .summary td {{
            padding: 8px;
            border-bottom: 1px solid #eee;
        }}
        .alerts {{
            margin-bottom: 20px;
        }}
        .alert {{
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        .alert.warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        .alert.danger {{
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }}
        .risk-analysis {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .risk-score {{
            font-size: 24px;
            font-weight: bold;
            margin: 15px 0;
        }}
        .findings-summary ul {{
            list-style: none;
            padding: 0;
        }}
        .findings-summary li {{
            padding: 8px;
            background: #f8f9fa;
            margin: 5px 0;
            border-radius: 4px;
        }}
        .statistics {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chart-container {{
            margin: 20px 0;
        }}
        .bar-chart {{
            padding: 10px 0;
        }}
        .bar-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .bar-label {{
            width: 60px;
            font-size: 12px;
            color: #7f8c8d;
        }}
        .bar-container {{
            flex: 1;
            display: flex;
            align-items: center;
        }}
        .bar {{
            height: 25px;
            background: linear-gradient(to right, #3498db, #2980b9);
            border-radius: 3px;
            transition: width 0.3s;
        }}
        .bar-value {{
            margin-left: 10px;
            font-size: 12px;
            color: #2c3e50;
            min-width: 30px;
        }}
        .pie-chart {{
            padding: 10px 0;
        }}
        .pie-item {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .pie-label {{
            width: 150px;
            font-size: 13px;
        }}
        .pie-bar {{
            height: 20px;
            background: #3498db;
            border-radius: 3px;
            margin: 0 10px;
        }}
        .pie-value {{
            font-size: 12px;
            color: #7f8c8d;
        }}
        .search-filter {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .search-filter input {{
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }}
        .search-filter input:focus {{
            outline: none;
            border-color: #3498db;
        }}
        .filter-buttons {{
            margin-top: 15px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}
        .filter-btn.active {{
            background: #3498db;
            color: white;
        }}
        .filter-btn:not(.active) {{
            background: #ecf0f1;
            color: #2c3e50;
        }}
        .filter-btn:hover {{
            opacity: 0.8;
        }}
        .stats {{
            text-align: center;
            padding: 10px;
            color: #7f8c8d;
            font-size: 14px;
        }}
        .entry {{
            background: white;
            margin-bottom: 15px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        .entry.hidden {{
            display: none;
        }}
        .entry-header {{
            background: #3498db;
            color: white;
            padding: 12px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .entry-number {{
            font-weight: bold;
            font-size: 16px;
        }}
        .source {{
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
        }}
        .timestamp {{
            font-size: 12px;
            opacity: 0.9;
        }}
        .content-type {{
            padding: 8px 15px;
            background: #ecf0f1;
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
        }}
        .content {{
            padding: 15px;
        }}
        .content pre {{
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        .entry-footer {{
            padding: 10px 15px;
            background: #f8f9fa;
            font-size: 12px;
            color: #6c757d;
        }}
        .highlight {{
            background-color: yellow;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>🔍 {title}</h1>
    <div class="meta">Generated: {generated_time}</div>
    
    {summary}
    {alerts}
    {risk}
    {charts}
    
    <div class="search-filter">
        <h3>Search & Filter</h3>
        <input type="text" id="searchBox" placeholder="Search clipboard content..." onkeyup="searchEntries()">
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterByType('all')">All</button>
            <button class="filter-btn" onclick="filterByType('text')">Text Only</button>
            <button class="filter-btn" onclick="filterByType('registry_setting')">Registry</button>
        </div>
        <div class="stats" id="stats"></div>
    </div>
    
    <h2>Clipboard Entries</h2>
    <div id="entries">
        {entries}
    </div>
    
    <script>
        let allEntries = document.querySelectorAll('.entry');
        let currentFilter = 'all';
        
        function updateStats() {{
            let visible = document.querySelectorAll('.entry:not(.hidden)').length;
            let total = allEntries.length;
            document.getElementById('stats').innerHTML = `Showing ${{visible}} of ${{total}} entries`;
        }}
        
        function searchEntries() {{
            let searchTerm = document.getElementById('searchBox').value.toLowerCase();
            
            allEntries.forEach(entry => {{
                let content = entry.querySelector('.content').textContent.toLowerCase();
                let source = entry.querySelector('.source').textContent.toLowerCase();
                
                if (content.includes(searchTerm) || source.includes(searchTerm)) {{
                    if (currentFilter === 'all' || entry.dataset.type === currentFilter) {{
                        entry.classList.remove('hidden');
                        
                        if (searchTerm) {{
                            highlightText(entry, searchTerm);
                        }}
                    }}
                }} else {{
                    entry.classList.add('hidden');
                }}
            }});
            
            updateStats();
        }}
        
        function filterByType(type) {{
            currentFilter = type;
            
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            allEntries.forEach(entry => {{
                if (type === 'all' || entry.dataset.type === type) {{
                    entry.classList.remove('hidden');
                }} else {{
                    entry.classList.add('hidden');
                }}
            }});
            
            if (document.getElementById('searchBox').value) {{
                searchEntries();
            }} else {{
                updateStats();
            }}
        }}
        
        function highlightText(entry, searchTerm) {{
            let contentDiv = entry.querySelector('.content pre');
            let originalText = contentDiv.getAttribute('data-original') || contentDiv.textContent;
            
            if (!contentDiv.getAttribute('data-original')) {{
                contentDiv.setAttribute('data-original', originalText);
            }}
            
            if (searchTerm) {{
                let regex = new RegExp(`(${{searchTerm}})`, 'gi');
                let highlightedText = originalText.replace(regex, '<span class="highlight">$1</span>');
                contentDiv.innerHTML = highlightedText;
            }} else {{
                contentDiv.textContent = originalText;
            }}
        }}
        
        allEntries.forEach(entry => {{
            let typeText = entry.querySelector('.content-type').textContent.trim().toLowerCase();
            entry.dataset.type = typeText;
        }});
        
        updateStats();
    </script>
</body>
</html>"""