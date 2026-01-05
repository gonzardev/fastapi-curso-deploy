from fastapi import FastAPI, Body, Path, Query, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from jwt_config import *
from config.database import sesion, motor, base
from modelos.ventas import Ventas as VentasModelo

#creando instancia de fastAPI
app = FastAPI()
app.title = 'Aplicacion de Ventas'
app.version = '1.0.1'
base.metadata.create_all(bind=motor)

#Puente para CSS
app.mount("/static", StaticFiles(directory="frontend"), name="static")

#Creando el permiso
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Modelo usuario
class Usuario(BaseModel):
    email:str
    clave:str
    

#Creando modelo
class Ventas(BaseModel):
    id: Optional[int] = None
    fecha: str = Field(..., examples=["22/12/26"])
    tienda: str = Field(..., min_length=4, max_length=100, examples=["Tienda01"])
    importe: float = Field(..., examples=[999.99])
    #Usando modelconfig
    model_config = ConfigDict(
        from_attributes= True,
        json_schema_extra = {
            "examples": [{
                "id":1,
                "fecha": "22/12/26",
                "tienda": "Tienda01",
                "importe": 999.99
            }]
        }
    )

#portador token
class Portador(HTTPBearer):
    async def __call__(self, request:Request):
        autorizacion = await super().__call__(request)
        dato = valida_token(autorizacion.credentials)
        if dato['email'] != 'gonzaneke@gmail.com':
            raise HTTPException(status_code=403, detail='No autorizado')
        


#crear endpoint usando un decorador
@app.get('/', tags=['Inicio'])
def root():
    return FileResponse('frontend/index.html')

@app.get('/dashboard', tags=['Inicio'])
def dashboard():
    return FileResponse('frontend/dashboard.html')

@app.get('/ventas', tags=['Ventas'], response_model=List[Ventas], status_code=200, dependencies=[Depends(Portador())])
def dame_ventas() -> List[Ventas]:
    db = sesion()
    resultado = db.query(VentasModelo).all()
    return JSONResponse(status_code= 200, content=jsonable_encoder(resultado))

@app.get('/ventas/{id}', tags=['Ventas'], response_model=List[Ventas])
def dame_ventas_por_id(id: int = Path(ge=1, le=1000)) -> List[Ventas]:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(status_code=404, content={"message": "No se encontro ese id"})
    return JSONResponse(status_code = 200, content=jsonable_encoder(resultado))

@app.get('/ventas/', tags=['Ventas'], response_model=List[Ventas])
def dame_ventas_por_tienda(tienda: str = Query(min_length=4, max_length=100)) -> List[Ventas]:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.tienda == tienda).all()
    if not resultado:
        return JSONResponse(status_code=404, content={"message": "No se encontro esa tienda"})
    return JSONResponse(status_code = 200, content=jsonable_encoder(resultado))

@app.post('/ventas', tags=['Ventas'], response_model=dict)
def crear_venta(venta:Ventas) -> dict:
    db = sesion()
    nueva_venta = VentasModelo(**venta.model_dump())
    db.add(nueva_venta)
    db.commit()
    return JSONResponse(content={'mensaje': 'Venta registrada'}, status_code=200)

@app.put('/ventas/{id}', tags=['Ventas'], response_model=dict)
def actualizar_venta(id:int, venta: Ventas) -> dict:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(status_code=404, content={'message':'No se ha podido actualizar'})
    resultado.fecha = venta.fecha
    resultado.tienda = venta.tienda
    resultado.importe = venta.importe
    db.commit()
    return JSONResponse(content={'mensaje': 'Venta actualizada'}, status_code=200)

@app.delete('/ventas/{id}', tags=['Ventas'], response_model=dict)
def borrar_venta(id: int) -> dict:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(status_code=404, content={'message':'No se ha podido eliminar'})
    db.delete(resultado)
    db.commit()
    return JSONResponse(content={'mensaje': 'Venta eliminada'}, status_code=200)
    
#Creando ruta para login
@app.post('/login', tags=['Autenticacion'])
def login(usuario:Usuario):
    if usuario.email == 'gonzaneke@gmail.com' and usuario.clave == '1234':
        token:str = dame_token({"email": usuario.email})
        return JSONResponse(status_code=200 , content={'token': token})
    return JSONResponse(status_code=401, content={"message": "Usuario o clave incorrectos"})
        