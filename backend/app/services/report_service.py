import io
import json
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from ..models.database import Project, CodeFile
from sqlmodel import Session, select

logger = logging.getLogger(__name__)

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
        
        # Estilos personalizados mejorados
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
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
            textColor=colors.HexColor("#1e3a8a"),
            borderPadding=5
        )

        sub_header_style = ParagraphStyle(
            'SubHeaderStyle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor("#2563eb"),
            spaceBefore=8
        )

        evidence_style = ParagraphStyle(
            'EvidenceStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceBefore=3,
            textColor=colors.HexColor("#374151")
        )

        detail_style = ParagraphStyle(
            'DetailStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#4b5563"),
            italic=True
        )
        
        content = []
        
        # --- PORTADA ---
        content.append(Spacer(1, 100))
        content.append(Paragraph("REPORTE FORENSE DE AUTORÍA IA", title_style))
        content.append(Spacer(1, 10))
        content.append(Paragraph(f"PROYECTO: {project.name}", styles['Heading2']))
        content.append(Spacer(1, 20))
        content.append(Paragraph(
            "Análisis técnico avanzado de firmas digitales y patrones sintéticos para la detección "
            "de contenido generado por modelos de lenguaje de gran escala (LLMs).", 
            styles['Normal']
        ))
        content.append(Spacer(1, 250))
        content.append(Paragraph(f"Generado por LuminaShield AI Engine", detail_style))
        content.append(PageBreak())
        
        # --- RESUMEN EJECUTIVO ---
        content.append(Paragraph("Resumen Ejecutivo", header_style))
        summary_data = [
            ["ID de Proyecto", str(project.id)],
            ["Fecha de Análisis", project.upload_date.strftime("%d/%m/%Y %H:%M:%S")],
            ["Archivos Procesados", str(len(files))],
            ["Probabilidad Global de IA", f"{project.overall_score}%"],
            ["Veredicto Final", "SOSPECHA DE IA" if project.overall_score > 60 else "PROBABLE HUMANO"]
        ]
        
        st = Table(summary_data, colWidths=[150, 300])
        st.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1, 4), (1, 4), colors.red if project.overall_score > 60 else colors.green),
        ]))
        content.append(st)
        content.append(Spacer(1, 30))
        
        # --- DETALLE POR ARCHIVO ---
        content.append(Paragraph("Análisis Detallado por Archivo", header_style))
        
        for f in files:
            content.append(Paragraph(f"Archivo: {f.filename}", sub_header_style))
            
            # Info básica
            file_info = [
                ["Métrica", "Valor"],
                ["Probabilidad IA", f"{f.ai_score}%"],
                ["Modelo Identificado", f.detected_model or "No Determinado"],
                ["Motor Principal", f.analysis_engine or "LuminaShield"]
            ]
            
            fit = Table(file_info, colWidths=[150, 300])
            fit.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            content.append(fit)
            content.append(Spacer(1, 10))
            
            # --- EVIDENCIAS FORENSES ---
            if f.ai_analysis:
                try:
                    data = json.loads(f.ai_analysis)
                    # El nuevo formato tiene army_details, points_of_interest, evidence
                    
                    # 1. Detalles del Ejército (si existen)
                    army_details = data.get("army_details", [])
                    if army_details:
                        content.append(Paragraph("Evidencias del Consenso de IA:", styles['Heading4']))
                        for detail in army_details:
                            model_name = detail.get("detected_model", "Analista IA")
                            prob = detail.get("probability", 0)
                            content.append(Paragraph(f"• {model_name} (Confianza: {prob}%):", styles['Normal']))
                            
                            ev_list = detail.get("evidence", [])
                            if isinstance(ev_list, list):
                                for ev in ev_list:
                                    content.append(Paragraph(f"- {ev}", evidence_style))
                    
                    # 2. Puntos de Interés Heurísticos
                    poi = data.get("points_of_interest", [])
                    if poi:
                        content.append(Paragraph("Patrones y Estructuras Detectadas:", styles['Heading4']))
                        for p in poi:
                            content.append(Paragraph(f"> {p}", evidence_style))
                            
                except Exception as e:
                    logger.error(f"Error parsing ai_analysis in PDF: {e}")
                    content.append(Paragraph("Error al procesar las evidencias técnicas.", detail_style))
            else:
                content.append(Paragraph("No se encontraron firmas adicionales en este archivo.", detail_style))
            
            content.append(Spacer(1, 15))
            content.append(Paragraph("-" * 90, detail_style))
            content.append(Spacer(1, 10))

        # --- FINAL ---
        content.append(Spacer(1, 40))
        disclaimer = (
            "AVISO LEGAL: Este reporte es un análisis probabilístico basado en modelos de inteligencia artificial "
            "y heurísticas estilométricas. Los resultados deben ser interpretados como una guía técnica y no como "
            "una prueba absoluta. Se recomienda la revisión manual por un experto humano."
        )
        content.append(Paragraph(disclaimer, ParagraphStyle('Disc', parent=styles['Normal'], textColor=colors.HexColor("#991b1b"), fontSize=8, italic=True)))
        
        doc.build(content)
        buffer.seek(0)
        return buffer
