from sqlmodel import SQLModel, create_engine, Session, select
from setup.settings import DATABASE_URL
from database.models import Usuario, ContaBancaria, Transacao

engine = create_engine(f"{DATABASE_URL}", echo=True)

SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def select_usuario(db: Session, email: str):
    with db:
        statement = select(Usuario).where(Usuario.email == email)
        results = db.exec(statement).first()
        return results.nome