from fastapi import FastAPI
import psycopg2
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/partidos")
def get_partidos():
    if not DATABASE_URL:
        return {"error": "DATABASE_URL no configurada"}
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT equipo_local, equipo_visitante, hora, canales, urls_ipfs FROM partidos ORDER BY hora")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    partidos = []
    for row in rows:
        partidos.append({
            "equipo_local": row[0],
            "equipo_visitante": row[1],
            "hora": row[2],
            "canales": row[3].split(", "),
            "urls_ipfs": row[4].split(", ")
        })
    return {"partidos": partidos}
