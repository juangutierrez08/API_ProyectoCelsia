from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.conn import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    nombreCompleto = Column(String)