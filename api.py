from fastapi import FastAPI
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir que tu app Android acceda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/partidos")
def obtener_partidos():
    conn = sqlite3.connect("scraping.db")
    cursor = conn.cursor()
    cursor.execute("SELECT equipo_local, equipo_visitante, hora, canales, urls_ipfs FROM partidos")
    rows = cursor.fetchall()
    conn.close()
    return [{"local": r[0], "visitante": r[1], "hora": r[2], "canales": r[3], "urls": r[4]} for r in rows]
