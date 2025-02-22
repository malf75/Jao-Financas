from sqlmodel import SQLModel, create_engine, Session, select
from setup.settings import DATABASE_URL
from database.models import Usuario, ContaBancaria, Transacao

engine = create_engine(f"{DATABASE_URL}", echo=True)

SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

def get_db():
    with Session(engine) as session:
        yield session

def select_usuario(db: Session, email: str):
    with db:
        statement = select(Usuario).where(Usuario.email == email)
        results = db.exec(statement).first()
        return {"nome": results.nome, "email": results.email, "saldo": results.saldo_usuario, "contas": results.conta_bancaria, "status": results.ativo}