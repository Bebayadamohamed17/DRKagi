from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import sqlite3
import os

class PDFReporter:
    def __init__(self, db_path="pentest_data.db"):
        self.db_path = db_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(name='SectionHeader', parent=self.styles['Heading2'], spaceAfter=10, textColor=colors.HexColor("#2c3e50")))
        self.styles.add(ParagraphStyle(name='VulnCritical', parent=self.styles['Normal'], textColor=colors.red))
        self.styles.add(ParagraphStyle(name='VulnHigh', parent=self.styles['Normal'], textColor=colors.orange))

    def generate_report(self, filename="Pentest_Report.pdf", executive_summary=""):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        # 1. Title Page
        elements.append(Paragraph("Ethical AI Penetration Test Report", self.styles['Title']))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Confidential & Proprietary", self.styles['Italic']))
        elements.append(Spacer(1, 1*inch))

        # 2. Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['Heading1']))
        if executive_summary:
            # Handle markdown-like bolding if simple
            summary_text = executive_summary.replace("**", "")
            elements.append(Paragraph(summary_text, self.styles['Normal']))
        else:
            elements.append(Paragraph("No summary provided.", self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))

        # 3. Discovered Assets (Targets)
        elements.append(Paragraph("Discovered Assets", self.styles['Heading1']))
        targets_data = self._get_targets_data()
        if targets_data:
            t = Table(targets_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("No assets found.", self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))

        # 4. Vulnerabilities
        elements.append(Paragraph("Vulnerability Findings", self.styles['Heading1']))
        vulns = self._get_vulns_data()
        
        if vulns:
            for v in vulns:
                # v = (name, severity, description, target_ip, exploit_path)
                color = colors.black
                if v[1] == 'CRITICAL': color = colors.red
                elif v[1] == 'HIGH': color = colors.orange
                
                elements.append(Paragraph(f"[{v[1]}] {v[0]}", ParagraphStyle(name='VHeading', parent=self.styles['Heading3'], textColor=color)))
                elements.append(Paragraph(f"<b>Host:</b> {v[3]}", self.styles['Normal']))
                elements.append(Paragraph(f"<b>Description:</b> {v[2]}", self.styles['Normal']))
                if v[4]:
                     elements.append(Paragraph(f"<b>Exploit Path:</b> {v[4]}", self.styles['Code']))
                elements.append(Spacer(1, 0.2*inch))
        else:
             elements.append(Paragraph("No vulnerabilities discovered.", self.styles['Normal']))

        # Build
        try:
            doc.build(elements)
            print(f"[+] PDF Report generated: {filename}")
            return True
        except Exception as e:
            print(f"[-] PDF Generation Error: {e}")
            return False

    def _get_targets_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address, hostname, status, last_scanned FROM targets")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows: return None
        
        data = [['IP Address', 'Hostname', 'Status', 'Last Scanned']]
        for row in rows:
            data.append([str(r) for r in row])
        return data

    def _get_vulns_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.name, v.severity, v.description, t.ip_address, v.exploit_path
            FROM vulnerabilities v
            JOIN targets t ON v.target_id = t.id
            ORDER BY 
                CASE v.severity
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows
