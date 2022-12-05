from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from pydantic import BaseModel

from schemas import s_usuarios
from db.conn import SessionLocal, engine

from modelos import m_telemetria, m_usuarios
from schemas import s_telemetria, s_usuarios

SECRET_KEY = "9675bad123f7a15ed1862c24b8092311c9df72f42408251c283b1111a8610e5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#Inicio jwt y hashed
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#Fin jwt y hashed
m_usuarios.Base.metadata.create_all(bind=engine)
m_telemetria.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def get_user(username:str):
    db = get_db()
    db_usuario =  next(db).query(m_usuarios.Usuario).filter(m_usuarios.Usuario.email == username).first()
    if db_usuario:
        return db_usuario

#Inicio jwt y hashed
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt    
#Fin jwt y hashed


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    usuario = get_user(username=token_data.username)
    if usuario is None:
        raise credentials_exception
    return usuario