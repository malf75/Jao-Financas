from sqlmodel import create_engine, Session
from setup.settings import DATABASE_URL

engine = create_engine(f"{DATABASE_URL}", echo=True)

SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

def get_db():
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        {"message":f"Erro ao criar sessão do banco de dados: {e}"}