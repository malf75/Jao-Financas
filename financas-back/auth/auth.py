from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from starlette import status
from database.db import get_db
from database.models import Usuario
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from setup.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS
from pydantic import BaseModel, EmailStr
from auth.m2f import *

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')

class CreateUserRequest(BaseModel):
    nome: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    try:
        secret_encoded, qrcode = m2f(create_user_request.email)
        create_user_model = Usuario(
            nome=create_user_request.nome,
            email=create_user_request.email,
            senha=bcrypt_context.hash(create_user_request.password),
            secret_key=secret_encoded,
            qrcode=qrcode
        )
        query = select(Usuario).where(Usuario.email == create_user_model.email)
        consulta = db.exec(query).first()
        if consulta:
            raise HTTPException(status_code=400, detail="Usuário Já Existente")
        else:
            db.add(create_user_model)
            db.commit()
            return {"201": "Usuário Criado"}
    except Exception as e:
        return {"message":f"Erro ao criar usuário: {e}"}

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Credenciais incorretas")
        if user.primeiro_login == True:
            return RedirectResponse(f"/qr/{user.id}", status_code=status.HTTP_302_FOUND)
        return RedirectResponse(f"/m2f/{user.id}", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return {"message":f"Erro ao realizar login: {e}"}

@router.get("/qr/{id}")
async def qrcode(id: int, db: db_dependency):
    try:
        statement = select(Usuario).where(Usuario.id == id)
        query = db.exec(statement).first()
        return {"qrcode": query.qrcode}
    except Exception as e:
        return {"message":f"Erro ao requisitar qrcode: {e}"}

@router.post("/m2f/{id}")
async def m2f_verification(id: str, otp: str, db: db_dependency):
    try:
        statement = select(Usuario).where(Usuario.id == int(id))
        query = db.exec(statement).first()
        verify = m2f_verify(query.secret_key, otp)
        if verify == True:
            query.primeiro_login = False
            query.qrcode = ''
            db.commit()
            token = create_access_token(query.email, query.id, timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
            return {"access_token": token, "token_type": "bearer", "expires_in": f"{ACCESS_TOKEN_EXPIRE_HOURS} Hours"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="OTP inválido")
    except Exception as e:
        return {"message":f"Erro ao verificar OTP: {e}"}

def authenticate_user(email: str, password: str, db):
    try:
        user = select(Usuario).where(Usuario.email == email)
        query = db.exec(user).first()
        if not query or not bcrypt_context.verify(password, query.senha):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Credenciais Incorretas")
        return query
    except Exception as e:
        return {"message":f"Erro ao autenticar usuário {e}"}

def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    try:
        encode = {"sub": email, "id": user_id}
        expires = datetime.now(timezone.utc) + expires_delta
        encode.update({"exp": expires})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Erro ao gerar token o usuário:{e}")

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Não pode verificar o usuário.")
        return {"email": email, "id": user_id}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Erro ao verificar o usuário:{e}")
    
