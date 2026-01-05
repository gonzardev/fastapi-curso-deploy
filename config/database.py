import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Detectar la base de datos (Postgres en Render o SQLite local)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Si Render nos da la URL, corregimos el protocolo para SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Si estamos en tu PC, usamos SQLite como lo tenías antes
    directorio = os.path.dirname(os.path.realpath(__file__))
    DATABASE_URL = f"sqlite:///{os.path.join(directorio, '../datos.sqlite')}"

# 2. Crear el motor (motor)
# El argumento connect_args solo se necesita si estamos usando SQLite
if "sqlite" in DATABASE_URL:
    motor = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
else:
    motor = create_engine(DATABASE_URL, echo=False)

# 3. Crear la sesión y la base
sesion = sessionmaker(bind=motor)
base = declarative_base()