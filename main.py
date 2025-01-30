from fastapi import FastAPI, WebSocket
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from typing import List
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os

load_dotenv() 
app = FastAPI()
name_bd_mongo = os.getenv("MONGO_DB")

try:
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command("ping")  # Comprobar conexión
    print("✅ Conexión exitosa a MongoDB")
except Exception as e:
    print("❌ Error al conectar a MongoDB:", e)

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
    # Obtén todos los documentos de la colección
    db = client["recommendation"]
    collection = db["reports-recommendation"]
    data = list(collection.find())
    
    # Convertir todos los documentos con ObjectId a str
    return [jsonable_encoder(document) for document in data]

@app.get("/token_data/tokens", response_model=List[dict])
async def get_datos():
    # Obtén todos los documentos de la colección
    db = client["token_data"]
    collection = db["tokens"]
    data = list(collection.find())
    
    # Convertir todos los documentos con ObjectId a str
    return [jsonable_encoder(document) for document in data]

@app.get("/token_data/users", response_model=List[dict])
async def get_datos():
    # Obtén todos los documentos de la colección
    db = client["token_data"]
    collection = db["users"] 
    data = list(collection.find())
    
    # Convertir todos los documentos con ObjectId a str
    return [jsonable_encoder(document) for document in data]