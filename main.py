from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from typing import List
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse

load_dotenv() 

app = FastAPI()
name_bd_mongo = "recommendation"  # Nombre de la BD

# Variable global para el cliente de MongoDB
client = None

@app.on_event("startup")
async def startup_db_client():
    """ Se ejecuta cuando la aplicación inicia """
    global client
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command("ping")  # Comprobar conexión
        print("Conexión exitosa a MongoDB")
    except Exception as e:
        print("Error al conectar a MongoDB:", e)

@app.on_event("shutdown")
async def shutdown_db_client():
    """ Se ejecuta cuando la aplicación se detiene """
    global client
    if client:
        client.close()
        print("Conexión a MongoDB cerrada")

# Función para convertir ObjectId a str
def jsonable_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: jsonable_encoder(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [jsonable_encoder(item) for item in obj]
    return obj

@app.get("/recommendation", response_model=List[dict])
async def get_datos():
    db = client["recommendation"]
    collection = db["reports-recommendation"]
    data = list(collection.find())
    return [jsonable_encoder(document) for document in data]

@app.get("/", response_class=JSONResponse)
async def get_metadata():
    db = client[name_bd_mongo]
    collections = db.list_collection_names()
    return JSONResponse(content={"database": name_bd_mongo, "tables": collections})

@app.get("/data", response_class=JSONResponse)
async def get_collections():
    try:
        db = client[name_bd_mongo]
        collections = db.list_collection_names()
        return {"database": name_bd_mongo, "collections_count": len(collections), "collections": collections}
    except PyMongoError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
