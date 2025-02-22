from fastapi.responses import RedirectResponse
from setup.settings import app
from auth.auth import router, get_current_user
from typing import Annotated
from database.db import get_db
from controller.conta_bancaria_controller import *
from sqlmodel import Session
from fastapi import Depends

app.include_router(router)
user_dependency = Annotated[dict, Depends(get_current_user)]
db = Annotated[Session, Depends(get_db)]

@app.get("/")
def redirect_index():
    return RedirectResponse("/docs")

@app.get("/dashboard")
async def dashboard(user: user_dependency):
    pass

@app.get("/contabancaria")
async def conta_bancaria(user: user_dependency, db: Session = Depends(get_db)):
    results = await retorna_contas_usuario(user, db)
    return results

@app.post("/contabancaria/criaconta")
async def cria_conta(nome: str, saldo_conta: float, user: user_dependency, db: Session = Depends(get_db)):
    result = await cria_conta_usuario(nome, saldo_conta, user, db)
    return result