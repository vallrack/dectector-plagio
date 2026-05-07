from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from .models.database import create_db_and_tables, get_session, Project, CodeFile
from .services.processor import FileProcessor
from datetime import datetime

app = FastAPI(title="Detector de Plagio e IA API")

# Configuración de CORS para Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are present even on unhandled 500 errors."""
    import logging
    logging.getLogger("uvicorn.error").error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "*"},
    )

@app.get("/")
def read_root():
    return {"message": "AI Plagiarism Detector Backend is running"}

@app.post("/upload")
async def upload_project(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    allowed_extensions = {
        '.zip', '.py', '.js', '.ts', '.tsx', '.java', '.cpp', '.c', '.html', '.css',
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.txt', '.md', '.json', '.csv', '.xml', '.yaml', '.yml', '.php', '.rb', '.go', '.rs'
    }
    ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    import logging
    logger = logging.getLogger("uvicorn.error")
    logger.info(f"DEBUG: Filename={file.filename}, Ext={ext}")
    
    if ext not in allowed_extensions:
        logger.error(f"DEBUG: Extension {ext} not in {allowed_extensions}")
        raise HTTPException(status_code=400, detail=f"Extension {ext} not supported")
    
    # Crear registro del proyecto
    project = Project(name=file.filename, user_id=1)
    session.add(project)
    session.commit()
    session.refresh(project)
    
    # Leer contenido del archivo
    content = await file.read()
    
    # Procesar en segundo plano
    if ext == '.zip':
        background_tasks.add_task(FileProcessor.process_zip, content, project.id, session)
    else:
        # Es un archivo individual
        background_tasks.add_task(FileProcessor.process_single_file, content, file.filename, project.id, session)
    
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
