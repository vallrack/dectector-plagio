import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from ..models.database import Project, CodeFile
from sqlmodel import Session, select

class ReportService:
    @staticmethod
    def generate_project_pdf(project_id: int, session: Session) -> io.BytesIO:
        project = session.get(Project, project_id)
        if not project:
            return None
        
        files = session.exec(select(CodeFile).where(CodeFile.project_id == project_id)).all()
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#3b82f6")
        )
        
        content = []
        
        # Título
        content.append(Paragraph(f"Reporte de Análisis de IA: {project.name}", title_style))
        content.append(Spacer(1, 12))
        
        # Resumen General
        content.append(Paragraph(f"Resumen del Proyecto", styles['Heading2']))
        data = [
            ["ID del Proyecto", str(project.id)],
            ["Fecha de Análisis", project.upload_date.strftime("%Y-%m-%d %H:%M:%S")],
            ["Archivos Analizados", str(len(files))],
            ["Score Global de IA", f"{project.overall_score}%"],
            ["Estado", project.status.upper()]
        ]
        
        t = Table(data, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(t)
        content.append(Spacer(1, 24))
        
        # Detalle por Archivo
        content.append(Paragraph(f"Detalle de Archivos", styles['Heading2']))
        file_data = [["Archivo", "IA %", "Resultado", "Justificación"]]
        for f in files:
            res = "IA" if f.ai_score > 60 else "Humano"
            # Truncar razonamiento si es muy largo
            reason = "Análisis heurístico" # Placeholder if not found
            # En una versión real, extraeríamos el reasoning guardado en la DB
            file_data.append([f.filename, f"{f.ai_score}%", res, Paragraph(reason, styles['Normal'])])
        
        ft = Table(file_data, colWidths=[150, 50, 70, 200])
        ft.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        content.append(ft)
        
        # Disclaimer
        content.append(Spacer(1, 48))
        disclaimer = "Este reporte fue generado automáticamente por LuminaShield. El análisis se basa en modelos probabilísticos y debe ser revisado por un profesional."
        content.append(Paragraph(disclaimer, styles['Italic']))
        
        doc.build(content)
        buffer.seek(0)
        return buffer
