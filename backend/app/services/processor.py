import zipfile
import io
import asyncio
import os
from ..core.ai_engine import AIEngine
from ..models.database import CodeFile, Project
from sqlmodel import Session, select
from .army_service import ArmyService


class FileProcessor:

    @staticmethod
    def _build_code_file(
        filename: str,
        ext: str,
        content: str,
        project_id: int,
        analysis: dict,
        analysis_engine: str,
    ) -> CodeFile:
        """Helper: create a CodeFile ORM instance from analysis results."""
        return CodeFile(
            project_id=project_id,
            filename=filename,
            language=ext,
            content=content,
            ai_score=analysis["score"],
            entropy=analysis["entropy"],
            is_ai_generated=analysis["score"] > 60,
            detected_model=analysis.get("detected_model"),
            detected_brand=analysis.get("detected_brand"),
            detected_version=analysis.get("detected_version"),
            attribution_confidence=analysis.get("attribution_confidence", 0.0),
            brand_color=analysis.get("brand_color"),
            analysis_engine=analysis_engine,
        )

    @staticmethod
    async def _run_analysis(content: str) -> tuple[dict, str]:
        """
        Run the heuristic engine + AI Army Consensus + Copyleaks.
        """
        analysis_engine = "LuminaShield"
        analysis = AIEngine.detect_ai_signature(content)

        # 1. Consultar al Ejército de IA (Consenso multi-modelo)
        army_keys = ["OPENAI_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "DEEPSEEK_API_KEY"]
        has_army = any(os.getenv(k) for k in army_keys)

        if has_army:
            army_result = await ArmyService.get_consensus(content)
            if army_result["army_details"]:
                # Mezclamos el score del ejército con el local (Ponderación 70% Ejército / 30% Local)
                local_score = analysis["score"]
                army_score = army_result["army_score"]
                
                # Si el ejército está muy seguro, le damos prioridad
                if army_score > 80 or army_score < 20:
                    analysis["score"] = army_score
                else:
                    analysis["score"] = round((army_score * 0.7) + (local_score * 0.3), 2)
                
                analysis["reasoning"] = f"Consenso de IA ({len(army_result['army_details'])} modelos): {army_result['army_verdict']}"
                analysis_engine += " + AI Army"

        # 2. Consultar a Copyleaks si sigue habiendo sospechas
        if analysis["score"] > 60:
            from ..services.copyleaks_service import CopyleaksService
            deep_result = CopyleaksService.analyze_code(content)

            if "score" in deep_result:
                # Copyleaks suele ser el estándar de oro si está disponible
                analysis["score"] = deep_result["score"]
                if not analysis.get("reasoning"):
                    analysis["reasoning"] = deep_result.get("reasoning", "")
                
                if deep_result.get("detected_model"):
                    analysis["detected_model"] = deep_result["detected_model"]

                analysis_engine += " + Copyleaks"

        return analysis, analysis_engine

    # ── process_zip ──────────────────────────────────────────────────────────

    @staticmethod
    async def process_zip(zip_content: bytes, project_id: int, session: Session):
        """Decompress a ZIP in memory and analyse every supported file."""
        from ..services.document_extractor import DocumentExtractor

        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            processed = 0
            for filename in z.namelist():
                if (
                    filename.startswith("__MACOSX/")
                    or "/." in filename
                    or filename.endswith("/")
                ):
                    continue

                with z.open(filename) as f:
                    content_bytes = f.read()

                content = DocumentExtractor.extract_text(filename, content_bytes)
                if not content or len(content.strip()) < 10:
                    continue

                ext = filename.split(".")[-1].lower() if "." in filename else "txt"

                # Llamada asíncrona al análisis
                analysis, analysis_engine = await FileProcessor._run_analysis(content)

                code_file = FileProcessor._build_code_file(
                    filename, ext, content, project_id, analysis, analysis_engine
                )
                session.add(code_file)
                processed += 1

            session.commit()

            # Update project summary
            files = session.exec(
                select(CodeFile).where(CodeFile.project_id == project_id)
            ).all()

            if files:
                avg_score = sum(f.ai_score for f in files) / len(files)
                project = session.get(Project, project_id)
                if project:
                    project.overall_score = round(avg_score, 2)
                    project.files_count = len(files)
                    project.status = "completed"
                    session.add(project)
                    session.commit()

    # ── process_single_file ──────────────────────────────────────────────────

    @staticmethod
    async def process_single_file(
        content_bytes: bytes, filename: str, project_id: int, session: Session
    ):
        """Analyse a single uploaded file."""
        from ..services.document_extractor import DocumentExtractor

        content = DocumentExtractor.extract_text(filename, content_bytes)
        if not content or len(content.strip()) < 10:
            return

        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        analysis, analysis_engine = await FileProcessor._run_analysis(content)

        code_file = FileProcessor._build_code_file(
            filename, ext, content, project_id, analysis, analysis_engine
        )
        session.add(code_file)
        session.commit()

        # Update project
        project = session.get(Project, project_id)
        if project:
            all_files = session.exec(
                select(CodeFile).where(CodeFile.project_id == project_id)
            ).all()
            avg_score = (
                sum(f.ai_score for f in all_files) / len(all_files) if all_files else analysis["score"]
            )
            project.overall_score = round(avg_score, 2)
            project.files_count = len(all_files)
            project.status = "completed"
            session.add(project)
            session.commit()
