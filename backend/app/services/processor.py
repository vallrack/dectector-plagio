import zipfile
import io
import asyncio
import os
import json
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
            ai_analysis=json.dumps({
                "army_details": analysis.get("army_details", []),
                "points_of_interest": analysis.get("points_of_interest", []),
                "evidence": analysis.get("evidence", [])
            }) if analysis.get("army_details") or analysis.get("points_of_interest") else None
        )

    @staticmethod
    async def _run_analysis(content: str) -> tuple[dict, str]:
        """
        Run the heuristic engine + AI Army Consensus + Copyleaks.
        """
        import logging
        logger = logging.getLogger("uvicorn.error")
        
        analysis_engine = "LuminaShield"
        logger.info("Iniciando análisis heurístico local...")
        analysis = AIEngine.detect_ai_signature(content)
        logger.info(f"Análisis local terminado. Score: {analysis['score']}")

        # 1. Consultar al Ejército de IA (Consenso multi-modelo)
        army_keys = ["OPENAI_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY"]
        has_army = any(os.getenv(k) for k in army_keys)

        if analysis.get("is_filler"):
            logger.info("Texto de relleno detectado (ej. =rand()). Se omite el Ejército de IA y Copyleaks.")
            analysis["reasoning"] = "Se detectó texto repetitivo o de prueba (posible =rand() o Lorem Ipsum). Se descarta autoría de IA."
            analysis["score"] = 0  # Force 0 to be completely safe
            analysis["is_suspicious"] = False
            has_army = False # Prevent Army execution

        if has_army:
            logger.info("Consultando al Ejército de IA...")
            army_result = await ArmyService.get_consensus(content)
            logger.info(f"Resultado del Ejército: Score={army_result['army_score']}, Modelos={len(army_result['army_details'])}")
            
            if army_result["army_details"]:
                # Mezclamos el score del ejército con el local
                local_score = analysis["score"]
                army_score = army_result["army_score"]
                
                # Ponderación agresiva: Si el ejército está muy seguro (>70%) o el local está seguro, 
                # tomamos el score más alto en lugar de promediar hacia abajo.
                if army_score > 70 or local_score > 70:
                    analysis["score"] = max(army_score, local_score)
                else:
                    # Si ambos son bajos, promediamos pero con peso al ejército
                    analysis["score"] = round((army_score * 0.8) + (local_score * 0.2), 2)
                
                if analysis["score"] > 60:
                    best_army_model = max(army_result["army_details"], key=lambda x: x.get("probability", 0))
                    if best_army_model.get("detected_model"):
                        model_name = best_army_model["detected_model"]
                        analysis["detected_model"] = model_name
                        
                        brand_map = {
                            "OpenAI": "ChatGPT (OpenAI)", "DeepSeek": "DeepSeek", "xAI": "Grok (xAI)",
                            "Alibaba": "Qwen (Alibaba)", "Gemini": "Gemini (Google)", "Llama": "Groq / Llama",
                            "Groq": "Groq / Llama", "Claude": "Claude (Anthropic)"
                        }
                        
                        analysis["detected_brand"] = next((v for k, v in brand_map.items() if k in model_name), model_name)
                        analysis["brand_color"] = AIEngine.BRAND_COLORS.get(analysis["detected_brand"], "#8B5CF6")
                        analysis["attribution_confidence"] = best_army_model.get("probability", 80)

                analysis["reasoning"] = f"Consenso de IA ({len(army_result['army_details'])} modelos): {army_result['army_verdict']}"
                analysis["army_details"] = army_result["army_details"]
                
                poi = analysis.get("points_of_interest", [])
                for detail in army_result["army_details"]:
                    if detail.get("points_of_interest"):
                        poi.extend(detail["points_of_interest"])
                analysis["points_of_interest"] = list(set(poi))
                
                analysis_engine += " + AI Army"
            else:
                logger.warning("El Ejército de IA no devolvió resultados válidos.")

        # 2. Consultar a Copyleaks si sigue habiendo sospechas
        if analysis["score"] > 60 and os.getenv("COPYLEAKS_API_KEY"):
            logger.info("Consultando a Copyleaks...")
            from ..services.copyleaks_service import CopyleaksService
            deep_result = CopyleaksService.analyze_code(content)

            if "score" in deep_result:
                logger.info(f"Copyleaks terminado. Score: {deep_result['score']}")
                analysis["score"] = deep_result["score"]
                if not analysis.get("reasoning"):
                    analysis["reasoning"] = deep_result.get("reasoning", "")
                
                if deep_result.get("detected_model"):
                    analysis["detected_model"] = deep_result["detected_model"]

                analysis_engine += " + Copyleaks"
            else:
                logger.warning(f"Copyleaks falló: {deep_result.get('error')}")

        return analysis, analysis_engine

    # ── process_zip ──────────────────────────────────────────────────────────
    # ── process_zip ──────────────────────────────────────────────────────────
    @staticmethod
    async def process_zip(zip_content: bytes, project_id: int):
        """Decompress a ZIP in memory and analyse every supported file in parallel."""
        from ..services.document_extractor import DocumentExtractor
        from ..models.database import engine, ACTIVE_DB_NAME
        from ..core.logger import add_debug_log
        import asyncio

        add_debug_log(f"Iniciando tarea ZIP PARALELA para proyecto {project_id} en {ACTIVE_DB_NAME}")
        
        # Limitamos a 3 archivos simultáneos para no saturar memoria ni APIs
        semaphore = asyncio.Semaphore(3)

        async def analyze_and_save(filename, content_bytes):
            async with semaphore:
                try:
                    content = DocumentExtractor.extract_text(filename, content_bytes)
                    if not content or len(content.strip()) < 10:
                        return False

                    ext = filename.split(".")[-1].lower() if "." in filename else "txt"
                    
                    add_debug_log(f"Analizando: {filename}...")
                    analysis, analysis_engine = await FileProcessor._run_analysis(content)
                    
                    with Session(engine) as session:
                        code_file = FileProcessor._build_code_file(
                            filename, ext, content, project_id, analysis, analysis_engine
                        )
                        session.add(code_file)
                        session.commit()
                    
                    add_debug_log(f"Completado: {filename} (Score: {analysis['score']})")
                    return True
                except Exception as e:
                    add_debug_log(f"Error en archivo {filename}: {str(e)}")
                    return False

        try:
            tasks = []
            with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
                files_in_zip = z.namelist()
                add_debug_log(f"Preparando {len(files_in_zip)} archivos...")
                
                for filename in files_in_zip:
                    if filename.startswith("__MACOSX/") or "/." in filename or filename.endswith("/"):
                        continue

                    with z.open(filename) as f:
                        content_bytes = f.read()
                    
                    tasks.append(analyze_and_save(filename, content_bytes))

            # Ejecutar todas las tareas en paralelo (con el límite del semáforo)
            results = await asyncio.gather(*tasks)
            processed_count = sum(1 for r in results if r)

            # Finalizar proyecto
            with Session(engine) as session:
                project = session.get(Project, project_id)
                if project:
                    files = session.exec(select(CodeFile).where(CodeFile.project_id == project_id)).all()
                    if files:
                        avg_score = sum(f.ai_score for f in files) / len(files)
                        project.overall_score = round(avg_score, 2)
                        project.files_count = len(files)
                    
                    project.status = "completed"
                    session.add(project)
                    session.commit()
                    add_debug_log(f"ZIP FINALIZADO: {processed_count} archivos procesados con éxito.")

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            add_debug_log(f"CRASH en process_zip: {str(e)}\n{error_trace}")
            with Session(engine) as session:
                project = session.get(Project, project_id)
                if project:
                    project.status = "error"
                    session.add(project)
                    session.commit()

    # ── process_rar ──────────────────────────────────────────────────────────
    @staticmethod
    async def process_rar(rar_content: bytes, project_id: int):
        """Decompress a RAR in memory and analyse every supported file."""
        from ..services.document_extractor import DocumentExtractor
        from ..models.database import engine
        import rarfile

        with Session(engine) as session:
            try:
                with rarfile.RarFile(io.BytesIO(rar_content)) as r:
                    processed = 0
                    for filename in r.namelist():
                        if (
                            filename.startswith("__MACOSX/")
                            or "/." in filename
                            or filename.endswith("/")
                        ):
                            continue

                        with r.open(filename) as f:
                            content_bytes = f.read()

                        content = DocumentExtractor.extract_text(filename, content_bytes)
                        if not content or len(content.strip()) < 10:
                            continue

                        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

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
            except Exception as e:
                import logging
                logging.error(f"Error procesando RAR: {e}")
                project = session.get(Project, project_id)
                if project:
                    project.status = "error"
                    session.add(project)
                    session.commit()

    # ── process_single_file ──────────────────────────────────────────────────
    @staticmethod
    async def process_single_file(
        content_bytes: bytes, filename: str, project_id: int
    ):
        """Analyse a single uploaded file."""
        from ..services.document_extractor import DocumentExtractor
        from ..models.database import engine

        with Session(engine) as session:
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
