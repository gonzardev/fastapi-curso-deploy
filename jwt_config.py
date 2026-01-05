from jose import jwt
def dame_token(dato:dict) -> str:
    token: str = jwt.encode(payload=dato, key='mi_clave', algorithm='HS256')
    return token

def valida_token(token:str) -> dict:
    dato:dict = jwt.decode(token, key='mi_clave', algorithms=['HS256'])
    return dato