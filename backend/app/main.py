from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from .models.database import create_db_and_tables, get_session, Project, CodeFile
from .services.processor import FileProcessor
from datetime import datetime

from .api import auth
from .core.auth import get_current_user, User

app = FastAPI(title="Detector de Plagio e IA API")

# Incluir rutas de autenticación
app.include_router(auth.router)

# Configuración de CORS dinámica
# NOTA: allow_credentials=True NO es compatible con allow_origins=['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

import logging

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejo global de errores con logs detallados y respuesta informativa."""
    import traceback
    error_detail = str(exc)
    error_type = type(exc).__name__
    stack_trace = traceback.format_exc()
    
    logger.error(f"CRITICAL ERROR en {request.url.path}: {error_detail}")
    logger.error(stack_trace)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Error del Servidor: {error_detail}",
            "type": error_type,
            "path": request.url.path
        },
        headers={"Access-Control-Allow-Origin": "*"},
    )

@app.get("/")
def read_root():
    return {"message": "AI Plagiarism Detector Backend is running"}

@app.get("/health")
def health_check():
    import os
    return {
        "status": "ok",
        "database_url_set": bool(os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_PRIMARY")),
        "secret_key_set": bool(os.getenv("SECRET_KEY")),
        "ai_keys": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        }
    }

@app.get("/debug/db")
def debug_db():
    """Endpoint de diagnóstico: muestra el estado de todas las bases de datos."""
    from .models.database import get_db_status
    try:
        status = get_db_status()
        return {
            "status": "ok",
            "active_database": status["active_db"],
            "all_databases": status["databases"],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/projects")
def get_user_projects(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    projects = session.exec(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.id.desc())
    ).all()
    
    # También queremos el conteo de archivos para cada proyecto
    result = []
    for p in projects:
        files_count = session.exec(select(CodeFile).where(CodeFile.project_id == p.id)).all()
        result.append({
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "files_count": len(files_count),
            "created_at": p.id # Usamos el ID como proxy de fecha si no tenemos created_at
        })
    
    return result

@app.post("/upload")
async def upload_project(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    allowed_extensions = {
        '.zip', '.rar', '.py', '.js', '.ts', '.tsx', '.java', '.cpp', '.c', '.html', '.css',
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.txt', '.md', '.json', '.csv', '.xml', '.yaml', '.yml', '.php', '.rb', '.go', '.rs', '.sql'
    }
    ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    import logging
    logger = logging.getLogger("uvicorn.error")
    logger.info(f"DEBUG: Filename={file.filename}, Ext={ext}")
    
    if ext not in allowed_extensions:
        logger.error(f"DEBUG: Extension {ext} not in {allowed_extensions}")
        raise HTTPException(status_code=400, detail=f"Extension {ext} not supported")
    
    # Crear registro del proyecto
    project = Project(name=file.filename, user_id=current_user.id)
    session.add(project)
    session.commit()
    session.refresh(project)
    
    # Leer contenido del archivo
    content = await file.read()
    
    # Procesar en segundo plano
    if ext == '.zip':
        background_tasks.add_task(FileProcessor.process_zip, content, project.id)
    elif ext == '.rar':
        background_tasks.add_task(FileProcessor.process_rar, content, project.id)
    else:
        # Es un archivo individual
        background_tasks.add_task(FileProcessor.process_single_file, content, file.filename, project.id)
    
    return {
        "project_id": project.id,
        "message": "Analysis started in background",
        "status": "processing"
    }

@app.get("/project/{project_id}")
def get_project_status(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = session.exec(select(CodeFile).where(CodeFile.project_id == project_id)).all()
    
    return {
        "id": project.id,
        "name": project.name,
        "status": project.status,
        "files_count": len(files),
        "files": files
    }

@app.get("/project/{project_id}/report")
def download_report(project_id: int, session: Session = Depends(get_session)):
    from .services.report_service import ReportService
    from fastapi.responses import StreamingResponse
    
    pdf_buffer = ReportService.generate_project_pdf(project_id, session)
    if not pdf_buffer:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="reporte_ia_{project_id}.pdf"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
