import customtkinter as ctk
from pymongo import MongoClient, errors
from fastapi import FastAPI
import threading
import sys
import uvicorn
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
import pyperclip
from bson import ObjectId

# Crear la aplicación FastAPI
api_app = FastAPI()
fastapi_thread = None  # Hilo del servidor FastAPI
server_running = False
server_process = None  # Proceso del servidor FastAPI

# Variables globales
client = None  # Cliente de MongoDB
name_bd_mongo = ""  # Nombre de la BD

# Interfaz gráfica
app = ctk.CTk()
app.geometry("400x300")
app.title("Connect MongoDB Atlas")

label = ctk.CTkLabel(app, text="Connect MongoDB Atlas", font=("Arial", 20))
label.pack(pady=20)

# Función para conectar a MongoDB y reiniciar FastAPI
def verinfo(event=None):
    global client  # Para usar en FastAPI
    mongo_url = entry.get().strip()  # Obtener URL de conexión
    
    if not mongo_url.startswith("mongodb+srv://"):
        label.configure(text="❌ URL inválida")
        return
    
    try:
        # Conectar a MongoDB
        global client
        global name_bd_mongo
        client = MongoClient(mongo_url)
        name_bd_mongo = entry_namebd.get()
        db = client[name_bd_mongo]
        collections = db.list_collection_names()
        label.configure(text=f"✅ Conectado")
        if(len(collections) == 0):
            collections = ["No hay colecciones"]
            combo_collections.configure(values=collections[0])  # Cargar en el ComboBox
            combo_collections.set(collections[0])  # Seleccionar la primera por defecto
        else:            
            combo_collections.configure(values=collections)  # Cargar en el ComboBox
            combo_collections.set(collections[0])  # Seleccionar la primera por defecto
            update_url()
        print(f"✅ Conexión exitosa a MongoDB. Colecciones: {collections}")

    except errors.PyMongoError as e:
        label.configure(text="❌ Error al conectar")
        print("❌ Error al conectar a MongoDB:", e)


# Función para limpiar todo al cerrar la aplicación
def on_closing():
    print("🛑 Cerrando aplicación...")
    
    # Cerrar conexión a MongoDB
    if client:
        print("🛑 Cerrando conexión a MongoDB...")
        client.close()
    
    app.destroy()  # Cierra la ventana de Tkinter
    sys.exit()  # Termina completamente el proceso
    
def convert_objectid(data):
    """ Convierte ObjectId en string dentro de documentos anidados. """
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

@api_app.get("/{db}/{collection}", response_class=JSONResponse)
async def get_collections(db: str, collection: str):
    try:
        if db == None:
            return JSONResponse(content={"error": f"La base de datos '{db}' no existe"}, status_code=404)
        
        database = client[db]  # Seleccionar base de datos
        
        if collection not in database.list_collection_names():
            return JSONResponse(content={"error": f"La colección '{collection}' no existe en '{db}'"}, status_code=404)

        data = list(database[collection].find({}))  # Obtener datos
        data = convert_objectid(data)  # Convertir ObjectId

        return {"database": db, "collection": collection, "data": data}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
# Ejecutar FastAPI en un hilo separado
def run_fastapi():
    uvicorn.run(api_app, host="127.0.0.1", port=8000)

# Iniciar FastAPI en otro hilo
threading.Thread(target=run_fastapi, daemon=True).start()


# Entrada para la URL de conexión
entry = ctk.CTkEntry(app, placeholder_text="mongodb+srv://", width=300)
entry.pack(pady=5)
entry.bind("<Return>", verinfo)  # Ejecutar con Enter

# Entrada para la URL de conexión
entry_namebd = ctk.CTkEntry(app, placeholder_text="nameBD", width=300)
entry_namebd.pack(pady=3)
entry_namebd.bind("<Return>", verinfo)

# Botón para conectar
btn = ctk.CTkButton(app, text="Cargar", command=verinfo)
btn.pack(pady=10)

# Etiqueta de estado
label = ctk.CTkLabel(app, text="Esperando conexión...", font=("Arial", 13))
label.pack(pady=0)

# ComboBox para seleccionar la colección
combo_collections = ctk.CTkComboBox(app, values=["collection_1","collection_2"], command=lambda _: update_url(combo_collections.get()),width=200)
combo_collections.pack(pady=1)

url = "http://127.0.0.1:8000"

# Variable para almacenar la URL
url_var = ctk.StringVar(value="")

def copy_to_clipboard():
    """ Copia la URL al portapapeles al hacer clic """
    pyperclip.copy(url_var.get())  # Copiar al portapapeles
    label_links.configure(fg_color="lightgray")  # Cambia color para indicar copia
    label_links.after(100, lambda: label_links.configure(fg_color="white"))  # Restaura color

def update_url(collection=None):
    """ Actualiza el valor del input """
    label_links.configure(state="normal")  # Habilitar
    if collection==None:
        url_var.set(f"{url}/{entry_namebd.get()}/<collection>")  # Cambiar valor
    else:
        url_var.set(f"{url}/{entry_namebd.get()}/{collection}")
    label_links.configure(state="readonly")
    

# Crear el input deshabilitado
label_links = ctk.CTkEntry(app, width=300, font=("Arial", 12), textvariable=url_var, state="readonly", justify="center", placeholder_text="URL")
label_links.pack(pady=10)

# Configurar eventos
label_links.bind("<Enter>", lambda e: label_links.configure(cursor="hand2"))  # Simula pointer
label_links.bind("<Leave>", lambda e: label_links.configure(cursor=""))  # Vuelve a normal

# Asociar la función al evento de clic
label_links.bind("<Button-1>", lambda e: copy_to_clipboard())



# Capturar el cierre de la ventana
app.protocol("WM_DELETE_WINDOW", on_closing)

# Ejecutar la interfaz
app.mainloop()
