import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime

def scrapear():
    url = "https://www.futbolenlatv.es/competicion/la-liga"  # <-- cambia a la página que quieras scrapear
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Buscar la tabla que empieza con "Partidos de hoy"
    tabla = soup.find("table", class_="tablaPrincipal detalleVacio")

    if not tabla:
        print("⚠️ No se encontró la tabla de partidos")
        return

    filas = tabla.find_all("tr")

    conn = sqlite3.connect("scraping.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS partidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_scraping TIMESTAMP,
        fecha_partido TEXT,
        hora TEXT,
        competicion TEXT,
        equipo_local TEXT,
        equipo_visitante TEXT,
        estadio TEXT,
        canales TEXT
    )
    """)

    fecha_partido = None

    for fila in filas:
        # Caso 1: cabecera con fecha
        cabecera = fila.find("td", colspan="5")
        if cabecera and "Partidos de hoy" in cabecera.get_text():
            fecha_partido = cabecera.get_text(strip=True)
            continue

        # Caso 2: filas de partidos
        hora = fila.find("td", class_="hora")
        detalles = fila.find("td", class_="detalles")
        local = fila.find("td", class_="local")
        visitante = fila.find("td", class_="visitante")
        canales = fila.find("td", class_="canales")

        if not (hora and local and visitante):
            continue  # saltar filas que no son partidos

        # Extraer datos
        hora_txt = hora.get_text(strip=True)
        competicion = detalles.get_text(strip=True) if detalles else ""
        equipo_local = local.get_text(strip=True)
        equipo_visitante = visitante.get_text(strip=True)

        # Estadio: viene en meta dentro de canales
        estadio_meta = canales.find("meta", itemprop="name") if canales else None
        estadio = estadio_meta["content"] if estadio_meta else ""

        # Canales: lista separada por comas
        canales_list = []
        if canales:
            for li in canales.find_all("li"):
                canales_list.append(li.get_text(strip=True))
        canales_txt = ", ".join(canales_list)

        # Insertar en DB
        cursor.execute("""
        INSERT INTO partidos (
            fecha_scraping, fecha_partido, hora, competicion,
            equipo_local, equipo_visitante, estadio, canales
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.datetime.now(),
            fecha_partido,
            hora_txt,
            competicion,
            equipo_local,
            equipo_visitante,
            estadio,
            canales_txt
        ))

    conn.commit()
    conn.close()
    print("✅ Partidos guardados en scraping.db")

if __name__ == "__main__":
    scrapear()
