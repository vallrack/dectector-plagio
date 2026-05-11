import os
from sqlmodel import SQLModel, Field, create_engine, Session, Relationship
from typing import List, Optional
from datetime import datetime

# Modelos
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = "teacher"

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "processing"
    overall_score: float = 0.0
    files_count: int = 0

class CodeFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    filename: str
    language: str
    content: str
    ai_score: float = 0.0
    entropy: float = 0.0
    is_ai_generated: bool = False
    detected_model: Optional[str] = None
    detected_brand: Optional[str] = None
    detected_version: Optional[str] = None
    attribution_confidence: float = 0.0
    brand_color: Optional[str] = None
    analysis_engine: Optional[str] = "LuminaShield"
    ai_analysis: Optional[str] = None # Almacena JSON con evidencias detalladas

# Configuracion de Motor Dinamico
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Si hay DATABASE_URL (Vercel/Heroku/Supabase)
    # Correccion para URLs de Heroku/Postgres que usan 'postgres://' en vez de 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    # pool_pre_ping ayuda a reconectar si Supabase cierra la conexión por inactividad
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=0)
else:
    # Local (SQLite)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    
    # Asegurar que el directorio de almacenamiento existe
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        
    sqlite_url = f"sqlite:///{os.path.join(STORAGE_DIR, 'plagiarism_detector.db')}"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
