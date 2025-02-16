from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Usuario(SQLModel, table=True):
    __tablename__ = 'usuarios'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nome: str = Field(max_length=100)
    email: str = Field(max_length=50)
    senha: str = Field(max_length=30)
    saldo_usuario: float = Field(default=0.0)
    criado_em: datetime = Field(default_factory=datetime.now)
    ativo: bool = Field(default=True)
    transacoes: List['Transacao'] = Relationship(back_populates="usuario", cascade_delete=True)
    conta_bancaria: List['ContaBancaria'] = Relationship(back_populates="usuario", cascade_delete=True)

class ContaBancaria(SQLModel, table=True):
    __tablename__ = 'conta_bancaria'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    usuario: Usuario = Relationship(back_populates="conta_bancaria")
    nome: str = Field(max_length=100)
    saldo_conta: float = Field(default=0.0)
    transacoes: List['Transacao'] = Relationship(back_populates="conta_bancaria", cascade_delete=True)
    criado_em: datetime = Field(default_factory=datetime.now)

class Transacao(SQLModel, table=True):
    __tablename__ = 'transacao'

    id: int | None = Field(default=None, primary_key=True, index=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    conta_bancaria_id: Optional[int] = Field(default=None, foreign_key="conta_bancaria.id")
    conta_bancaria: Optional[ContaBancaria] = Relationship(back_populates="transacoes")
    usuario: Usuario = Relationship(back_populates="transacoes")
    valor: float = Field()
    tipo: str = Field(max_length=10)
    categoria: str = Field(max_length=50)
    data: datetime = Field(default_factory=datetime.now)