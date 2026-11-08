from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def conexion():
    print("Conectada con exito")
    return {
        "estado": "ok",
        "sistema": "mini-plataforma"
    }