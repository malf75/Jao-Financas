from fastapi.responses import RedirectResponse
from setup.settings import app
from sqlmodel import SQLModel, create_engine
from setup.settings import DATABASE_URL
from database.models import Usuario, ContaBancaria, Transacao

engine = create_engine(f"{DATABASE_URL}", echo=True)
from sqlmodel import Session

def create_db_and_tables():
    print("Criando tabelas no banco de dados...")
    SQLModel.metadata.drop_all(engine)  # Deleta tudo antes
    print(SQLModel.metadata.tables.keys())
    SQLModel.metadata.create_all(engine)  # Cria do zero
    print("Tabelas criadas com sucesso!")

    with Session(engine) as session:
        session.commit()

create_db_and_tables()

@app.get("/")
async def redirect_index():
    return RedirectResponse("/docs")