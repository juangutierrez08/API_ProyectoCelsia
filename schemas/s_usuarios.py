from pydantic import BaseModel

class UsuarioBase(BaseModel):
    email: str
    nombreCompleto: str

class UsuarioCreate(UsuarioBase):
    password: str


class Usuario(UsuarioBase):
    id: int
    
    class Config:
        orm_mode = True