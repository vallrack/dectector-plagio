import os
import logging
from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# ==============================================================================
# MODELOS
# ==============================================================================
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
    ai_analysis: Optional[str] = None

# ==============================================================================
# SISTEMA DE FALLBACK EN CASCADA
# Orden de prioridad: Neon → Supabase → SQLite
# ==============================================================================

def _normalize_url(url: str) -> str:
    """Normaliza URLs postgres:// a postgresql://"""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

def _try_connect(name: str, url: str):
    """Intenta conectarse a una base de datos y verifica la conexión."""
    try:
        normalized = _normalize_url(url)
        eng = create_engine(
            normalized,
            poolclass=NullPool,  # Óptimo para poolers externos y serverless
            connect_args={
                "connect_timeout": 8,
                "sslmode": "require",
            }
        )
        # Prueba real de conectividad
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"✅ [DB] Conectado exitosamente a: {name}")
        return eng, name, normalized
    except Exception as e:
        logger.warning(f"⚠️ [DB] {name} no disponible: {type(e).__name__}: {e}")
        return None, name, None

# Candidatos en orden de prioridad
CANDIDATE_DBS = [
    ("Neon (Primaria)", os.getenv("DATABASE_URL_PRIMARY")),
    ("Supabase (Secundaria)", os.getenv("DATABASE_URL_SECONDARY")),
    ("DATABASE_URL (Legado)", os.getenv("DATABASE_URL")),
]

# Reintento de conexión para mayor estabilidad en la nube
MAX_RETRIES = 3
engine = None
ACTIVE_DB_NAME = "Ninguna"
ACTIVE_DB_URL = None
DB_STATUS = {}

for db_name, db_url in CANDIDATE_DBS:
    if not db_url:
        DB_STATUS[db_name] = "no configurada"
        continue
    
    for attempt in range(MAX_RETRIES):
        eng, name, url = _try_connect(db_name, db_url)
        if eng:
            engine = eng
            ACTIVE_DB_NAME = name
            ACTIVE_DB_URL = url
            DB_STATUS[db_name] = "✅ ACTIVA"
            break
        else:
            logger.warning(f"Intento {attempt + 1} fallido para {db_name}, reintentando...")
            import time
            time.sleep(2)
            
    if engine:
        break
    else:
        DB_STATUS[db_name] = "❌ no disponible tras reintentos"

# Fallback final: SQLite (SOLO EN LOCAL, no en Render)
if engine is None and not os.getenv("RENDER"):
    logger.warning("⚠️ [DB] Usando SQLite local.")
    sqlite_url = "sqlite:///./plagiarism_detector.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    ACTIVE_DB_NAME = "SQLite (Local)"
    DB_STATUS["SQLite"] = "✅ ACTIVA"
elif engine is None:
    logger.error("❌ [DB] ERROR CRÍTICO: No se pudo conectar a ninguna base de datos en la nube.")

logger.info(f"🗄️  [DB] Base de datos activa: {ACTIVE_DB_NAME}")

# ==============================================================================
# FUNCIONES DE BASE DE DATOS
# ==============================================================================

def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        logger.info(f"✅ [DB] Tablas verificadas/creadas en: {ACTIVE_DB_NAME}")
    except Exception as e:
        logger.error(f"❌ [DB] Error al crear tablas: {e}")

def get_session():
    with Session(engine) as session:
        yield session

def get_db_status() -> dict:
    """Retorna el estado de todas las bases de datos configuradas."""
    return {
        "active_db": ACTIVE_DB_NAME,
        "databases": DB_STATUS,
    }
