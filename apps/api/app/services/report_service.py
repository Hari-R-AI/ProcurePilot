import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.api.v1.schemas.procurement import ProcurementRequestDetail

class ReportService:
    """Service to generate PDF reports for procurement analysis."""
    
    @staticmethod
    def generate_procurement_report(request_detail: ProcurementRequestDetail) -> bytes:
        """Generate a structured PDF report containing request details and analysis."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="TitleStyle", fontName="Helvetica-Bold", fontSize=18, spaceAfter=20, textColor=colors.HexColor("#1e3a8a")))
        styles.add(ParagraphStyle(name="SubtitleStyle", fontName="Helvetica-Bold", fontSize=14, spaceAfter=10, spaceBefore=15, textColor=colors.HexColor("#374151")))
        styles.add(ParagraphStyle(name="NormalStyle", fontName="Helvetica", fontSize=11, spaceAfter=6, leading=14, textColor=colors.HexColor("#4b5563")))
        styles.add(ParagraphStyle(name="BoldLabelStyle", fontName="Helvetica-Bold", fontSize=11, textColor=colors.HexColor("#111827")))
        
        Story = []
        
        # Header
        Story.append(Paragraph("ProcurePilot - Procurement Analysis Report", styles["TitleStyle"]))
        Story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["NormalStyle"]))
        Story.append(Spacer(1, 20))
        
        # Request Details
        Story.append(Paragraph("1. Request Details", styles["SubtitleStyle"]))
        req_data = [
            ["ID / Date", f"#{request_detail.id}  |  {request_detail.created_at.strftime('%Y-%m-%d %H:%M')}"],
            ["Title", request_detail.title],
            ["Category", request_detail.category],
            ["Department", request_detail.department or "N/A"],
            ["Urgency", request_detail.urgency],
            ["Budget", f"INR {request_detail.budget:,.2f}" if request_detail.budget else "Not specified"],
        ]
        
        t = Table(req_data, colWidths=[120, 340])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#1f2937")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ]))
        Story.append(t)
        Story.append(Spacer(1, 10))
        
        Story.append(Paragraph("Description:", styles["BoldLabelStyle"]))
        Story.append(Paragraph(request_detail.description, styles["NormalStyle"]))
        Story.append(Spacer(1, 15))
        
        analysis = request_detail.latest_analysis
        if analysis:
            # Analysis Summary
            Story.append(Paragraph("2. Analysis Summary", styles["SubtitleStyle"]))
            Story.append(Paragraph(f"<b>Confidence:</b> {analysis.confidence_score*100:.0f}% ({analysis.confidence_label})", styles["NormalStyle"]))
            Story.append(Paragraph(f"<b>Compliance:</b> {analysis.compliance_status}", styles["NormalStyle"]))
            if analysis.approval_suggestion:
                Story.append(Paragraph(f"<b>Approval Required:</b> {analysis.approval_suggestion.level} - {analysis.approval_suggestion.role}", styles["NormalStyle"]))
            Story.append(Spacer(1, 10))
            Story.append(Paragraph(analysis.summary, styles["NormalStyle"]))
            Story.append(Spacer(1, 15))
            
            # Extracted Requirements
            if analysis.extracted_requirements:
                Story.append(Paragraph("3. Extracted Requirements", styles["SubtitleStyle"]))
                for req in analysis.extracted_requirements:
                    Story.append(Paragraph(f"• <b>{req.name}</b> [{req.type} | {req.priority}]", styles["BoldLabelStyle"]))
                    if req.description:
                        Story.append(Paragraph(req.description, styles["NormalStyle"]))
                Story.append(Spacer(1, 15))
            
            # Policy Context
            if analysis.policy_snippets:
                Story.append(Paragraph("4. Policy Context", styles["SubtitleStyle"]))
                for pol in analysis.policy_snippets:
                    Story.append(Paragraph(f"• <b>{pol.source} ({pol.section})</b>", styles["BoldLabelStyle"]))
                    Story.append(Paragraph(pol.content[:200] + ("..." if len(pol.content) > 200 else ""), styles["NormalStyle"]))
                Story.append(Spacer(1, 15))
            
            # Risk Flags
            if analysis.risk_flags:
                Story.append(Paragraph("5. Risk Flags", styles["SubtitleStyle"]))
                for r in analysis.risk_flags:
                    Story.append(Paragraph(f"• <b>[{r.severity}] {r.category}</b>: {r.description}", styles["NormalStyle"]))
                Story.append(Spacer(1, 15))
            
            # Recommendations
            if analysis.recommendation_items:
                Story.append(Paragraph("6. Recommendations & Next Steps", styles["SubtitleStyle"]))
                for idx, r in enumerate(analysis.recommendation_items):
                    Story.append(Paragraph(f"{idx+1}. <b>{r.action}</b> ({r.priority})", styles["BoldLabelStyle"]))
                    Story.append(Paragraph(r.description, styles["NormalStyle"]))
                    meta = []
                    if r.owner: meta.append(f"Owner: {r.owner}")
                    if r.timeline: meta.append(f"Timeline: {r.timeline}")
                    if meta:
                        Story.append(Paragraph(" | ".join(meta), styles["NormalStyle"]))
                    Story.append(Spacer(1, 8))
        else:
            Story.append(Paragraph("No analysis data available for this request.", styles["NormalStyle"]))
            
        doc.build(Story)
        return buffer.getvalue()
