import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
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
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=26,
            spaceAfter=20,
            textColor=colors.HexColor("#1e40af"),
            alignment=1 # Center
        )

        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor("#3b82f6"),
            borderPadding=5
        )

        evidence_style = ParagraphStyle(
            'EvidenceStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceBefore=5,
            textColor=colors.HexColor("#374151")
        )
        
        content = []
        
        # PORTADA
        content.append(Spacer(1, 100))
        content.append(Paragraph(f"REPORTE FORENSE DE IA", title_style))
        content.append(Paragraph(f"Proyecto: {project.name}", styles['Heading2']))
        content.append(Spacer(1, 20))
        content.append(Paragraph(f"Este documento contiene un análisis detallado generado por el sistema LuminaShield y su Ejército de IA para identificar trazas de generación por modelos de lenguaje (GPT-4, Claude, Gemini, etc.).", styles['Normal']))
        content.append(Spacer(1, 200))
        
        # Resumen Ejecutivo
        content.append(Paragraph("Resumen Ejecutivo", header_style))
        summary_data = [
            ["ID del Proyecto", str(project.id)],
            ["Fecha de Análisis", project.upload_date.strftime("%Y-%m-%d %H:%M:%S")],
            ["Archivos Analizados", str(len(files))],
            ["Probabilidad Global de IA", f"{project.overall_score}%"],
            ["Veredicto Final", "SOSPECHA DE IA" if project.overall_score > 60 else "PROBABLE HUMANO"]
        ]
        
        st = Table(summary_data, colWidths=[150, 300])
        st.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        content.append(st)
        content.append(PageBreak())
        
        # DETALLE POR ARCHIVO
        content.append(Paragraph("Desglose Forense por Archivo", header_style))
        
        for f in files:
            content.append(Paragraph(f"Archivo: {f.filename}", styles['Heading3']))
            
            # Tabla básica del archivo
            file_info = [
                ["Métrica", "Valor"],
                ["Probabilidad de IA", f"{f.ai_score}%"],
                ["Motor de Análisis", f.analysis_engine or "LuminaShield"],
                ["Modelo Detectado", f.detected_model or "N/A"]
            ]
            
            fit = Table(file_info, colWidths=[150, 300])
            fit.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            content.append(fit)
            content.append(Spacer(1, 10))
            
            # EVIDENCIAS DETALLADAS
            if f.ai_analysis:
                try:
                    analysis_data = json.loads(f.ai_analysis)
                    if analysis_data:
                        content.append(Paragraph("Evidencias de Generación por IA:", styles['Heading4']))
                        
                        # Consolidar evidencias de todos los modelos
                        for result in analysis_data:
                            model_name = result.get('detected_model', 'Modelo Desconocido')
                            content.append(Paragraph(f"• Según {model_name}:", styles['Normal']))
                            
                            evidences = result.get('evidence', [])
                            if isinstance(evidences, list):
                                for ev in evidences:
                                    content.append(Paragraph(f"- {ev}", evidence_style))
                            
                            poi = result.get('points_of_interest', [])
                            if poi and isinstance(poi, list):
                                content.append(Paragraph("Puntos Críticos:", evidence_style))
                                for p in poi:
                                    content.append(Paragraph(f"  > {p}", evidence_style))
                            
                            content.append(Spacer(1, 5))
                except Exception as e:
                    content.append(Paragraph(f"Error al procesar evidencias: {e}", styles['Italic']))
            else:
                content.append(Paragraph("No se encontraron evidencias forenses adicionales para este archivo.", styles['Italic']))
            
            content.append(Spacer(1, 20))
            content.append(Paragraph("-" * 80, styles['Normal']))

        # Disclaimer
        content.append(Spacer(1, 40))
        disclaimer = "IMPORTANTE: Este reporte es una herramienta de apoyo probabilística. Los resultados deben ser validados por un experto humano antes de tomar cualquier medida académica o profesional."
        content.append(Paragraph(disclaimer, ParagraphStyle('Disc', parent=styles['Normal'], textColor=colors.red, fontSize=9, italic=True)))
        
        doc.build(content)
        buffer.seek(0)
        return buffer
