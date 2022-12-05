from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File

from sqlalchemy.orm import Session

from modelos import m_telemetria,m_usuarios
from schemas import s_telemetria, s_usuarios

import csv
from io import StringIO

import autenticacion 
app = FastAPI()

#Creación usuario
@app.post("/usuario/crear", response_model=s_usuarios.Usuario, tags=["Usuario"])
def crear_usuario( usuario: s_usuarios.UsuarioCreate, db: Session = Depends(autenticacion.get_db)):
    db_usuario =  db.query(m_usuarios.Usuario).filter(m_usuarios.Usuario.email == usuario.email).first() 
    if db_usuario:
        raise HTTPException(status_code=400, detail="Usuario ya existe en sistema")
    else:
        fake_hashed_password = autenticacion.get_password_hash(usuario.password)
        db_user = m_usuarios.Usuario(email=usuario.email, password=fake_hashed_password, nombreCompleto=usuario.nombreCompleto)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

#Mostrar usuario
@app.get("/usuario/", tags=["Usuario"])
def  usuario(current_user: m_usuarios.Usuario = Depends(autenticacion.get_current_user)):
    return current_user




#Cargar telelemetria
@app.post("/telemetria/cargar", tags=["Telemetría"])
def cargar_telemetria(
    file: UploadFile = File(...),
    db: Session = Depends(autenticacion.get_db)):
    data = []
    contents = file.file.read()
    buffer = StringIO(contents.decode('utf-8'))
    csvReader = csv.DictReader(buffer)
    for row in csvReader:
        dt = datetime.strptime(row["timestamp"][0:19], '%Y-%m-%d %H:%M:%S')
        telemetria = m_telemetria.Telemetria(
            ConnectionDeviceId = row["ConnectionDeviceId"],
            EventProcessedUtcTime = row["EventProcessedUtcTime"],
            HEFESTO_ID = row["HEFESTO_ID"],
            timestamp = dt,
            var_name = row["var-name"],
            value = row["value"],
            plugin = row["plugin"],
            request = row["request"],
            var_name_1 = row["var_name_1"],
            device = row["device"]
        )
        db_tele =  db.query(m_telemetria.Telemetria).filter(
            m_telemetria.Telemetria.ConnectionDeviceId == telemetria.ConnectionDeviceId,
            m_telemetria.Telemetria.timestamp == telemetria.timestamp
        ).first()
        if not db_tele:
            db.add(telemetria)
            db.commit()
            db.refresh(telemetria)
            data.append(row)
    buffer.close()
    file.file.close()
    return data

#Mostrar telemetría
@app.get("/telemetria/", tags=["Telemetría"])
def mostrar_Telemetría(
    desde: datetime,
    hasta: datetime,
    db: Session = Depends(autenticacion.get_db)
    ):
    db_telemetria = db.query(m_telemetria.Telemetria).filter(
        m_telemetria.Telemetria.timestamp >= desde,
        m_telemetria.Telemetria.timestamp <= hasta
    ).all()
    if not db_telemetria:
        return {"mensaje":"No se encontró telemetría en ese periodo"}
    return db_telemetria

    return {"Hola":"Mundo"}

#Autenticación Login
@app.post("/token", response_model=autenticacion.Token, tags=["Autenticación"])
async def login_for_access_token(form_data: autenticacion.OAuth2PasswordRequestForm = Depends()):
    user = autenticacion.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = autenticacion.timedelta(minutes=autenticacion.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = autenticacion.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}