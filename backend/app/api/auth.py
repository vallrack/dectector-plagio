from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from ..models.database import User, get_session
from ..core.auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    # Verificar si el usuario ya existe
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        role="teacher"
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return {"message": "Usuario registrado exitosamente", "id": new_user.id}

@router.post("/login")
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "id": user.id, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }
