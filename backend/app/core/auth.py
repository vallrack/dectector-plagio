import os
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from ..models.database import User, get_session

# Configuración básica
SECRET_KEY = os.getenv("SECRET_KEY", "7b9e1d2c3f4a5b6e7d8c9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def prepare_password(password: str) -> str:
    """
    BCrypt tiene un límite de 72 bytes. 
    Para evitarlo de forma segura sin perder entropía, pre-hasheamos con SHA-256
    y usamos el resultado (en base64) como entrada para BCrypt.
    """
    sha256_hash = hashlib.sha256(password.encode('utf-8')).digest()
    # Usamos base64 para que sea una cadena compatible con lo que espera passlib
    return base64.b64encode(sha256_hash).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(prepare_password(plain_password), hashed_password)

def get_password_hash(password):
    return pwd_context.hash(prepare_password(password))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user
