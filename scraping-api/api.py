from fastapi import FastAPI
import sqlite3

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect("scraping.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/partidos")
def obtener_partidos():
    conn = get_db_connection()
    partidos = conn.execute("SELECT * FROM partidos ORDER BY fecha_scraping DESC").fetchall()
    conn.close()
    return [dict(row) for row in partidos]
