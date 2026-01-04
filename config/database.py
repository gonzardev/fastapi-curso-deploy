import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

fichero = '../datos.sqlite'

directorio = os.path.dirname(os.path.realpath(__file__))

ruta = f"sqlite:///{os.path.join(directorio, fichero)}"

motor = create_engine(ruta, echo=True)

sesion = sessionmaker(bind=motor)

base = declarative_base()



