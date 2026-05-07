import zipfile
import io
from ..core.ai_engine import AIEngine
from ..models.database import CodeFile, Project
from sqlmodel import Session, select


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
    def _run_analysis(content: str) -> tuple[dict, str]:
        """
        Run the heuristic engine.  If the file is suspicious, also run
        Copyleaks for a second opinion.  Returns (analysis_dict, engine_label).
        """
        analysis_engine = "LuminaShield"
        analysis = AIEngine.detect_ai_signature(content)

        if analysis["is_suspicious"]:
            from ..services.copyleaks_service import CopyleaksService
            deep_result = CopyleaksService.analyze_code(content)

            if "score" in deep_result:
                # Copyleaks overrides the score – keep our brand attribution
                analysis["score"] = deep_result["score"]
                analysis["reasoning"] = deep_result.get("reasoning", "")

                # Only override brand if Copyleaks returned something specific
                if deep_result.get("detected_model"):
                    analysis["detected_model"] = deep_result["detected_model"]

                analysis_engine = "LuminaShield + Copyleaks"

        return analysis, analysis_engine

    # ── process_zip ──────────────────────────────────────────────────────────

    @staticmethod
    def process_zip(zip_content: bytes, project_id: int, session: Session):
        """Decompress a ZIP in memory and analyse every supported file."""
        from ..services.document_extractor import DocumentExtractor

        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            processed = 0
            for filename in z.namelist():
                # Ignore folders and hidden/junk files
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

                analysis, analysis_engine = FileProcessor._run_analysis(content)

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
    def process_single_file(
        content_bytes: bytes, filename: str, project_id: int, session: Session
    ):
        """Analyse a single uploaded file."""
        from ..services.document_extractor import DocumentExtractor

        content = DocumentExtractor.extract_text(filename, content_bytes)
        if not content or len(content.strip()) < 10:
            return

        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        analysis, analysis_engine = FileProcessor._run_analysis(content)

        code_file = FileProcessor._build_code_file(
            filename, ext, content, project_id, analysis, analysis_engine
        )
        session.add(code_file)
        session.commit()

        # Update project
        project = session.get(Project, project_id)
        if project:
            # Recalculate average across all files in the project
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
