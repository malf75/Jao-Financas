from fastapi.responses import RedirectResponse
from setup.settings import app
from database.db import select_usuario, SessionLocal

@app.get("/")
async def redirect_index():
    return RedirectResponse("/docs")

@app.get("/test")
async def test():
    return select_usuario(SessionLocal,"malfbf6@gmail.com")