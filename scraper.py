import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import re
import json
import unicodedata

URL_LALIGA = "https://www.futbolenlatv.es/competicion/la-liga"
URL_IPFS = "https://ipfs.io/ipns/elcano.top"

# Función para normalizar texto y eliminar acentos
def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto.strip()

def limpiar_ipfs_name(name):
    # Renombrar prefijo M. LaLiga a M+ LALIGA
    if name.startswith("M. LaLiga"):
        name = name.replace("M. LaLiga", "M+ LALIGA", 1)
    # Eliminar sufijos de resolución o audio
    name = re.sub(r'\s*(1080P|1080 MultiAudio|720 MultiAudio|1080|720)$', '', name)
    return name.strip()

def obtener_links_ipfs():
    response = requests.get(URL_IPFS)
    if response.status_code != 200:
        print("No se pudo acceder a IPFS")
        return {}
    
    match = re.search(r'const linksData\s*=\s*(\{.*?\});', response.text, re.DOTALL)
    if not match:
        print("No se encontró linksData en IPFS")
        return {}
    
    js_text = match.group(1)
    js_text = re.sub(r',\s*([\]}])', r'\1', js_text)
    data = json.loads(js_text)
    
    links_dict = {}
    for item in data.get("links", []):
        name = item.get("name", "").strip()
        url = item.get("url", "").strip()
        if not url or url == "acestream://":
            continue  # Ignorar URLs vacías
        name = limpiar_ipfs_name(name)
        norm_name = normalizar(name)
        if norm_name not in links_dict:
            links_dict[norm_name] = []
        links_dict[norm_name].append(url)  # Acumular todas las URLs posibles
    return links_dict

def scrapear():
    links_dict = obtener_links_ipfs()
    
    conn = sqlite3.connect("scraping.db")
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS partidos")
    cursor.execute("""
        CREATE TABLE partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo_local TEXT,
            equipo_visitante TEXT,
            hora TEXT,
            canales TEXT,
            urls_ipfs TEXT
        )
    """)

    response = requests.get(URL_LALIGA)
    soup = BeautifulSoup(response.text, "html.parser")
    tabla = soup.find("table", class_="tablaPrincipal")
    if not tabla:
        print("No se encontró la tabla")
        return

    for fila in tabla.find_all("tr"):
        if "cabeceraTabla" in fila.get("class", []):
            continue

        celdas = fila.find_all("td")
        if len(celdas) < 4:
            continue

        hora = celdas[0].get_text(strip=True)
        equipo_local = celdas[2].find("span").get_text(strip=True)
        equipo_visitante = celdas[3].find("span").get_text(strip=True)

        canales = []
        for li in celdas[4].select("ul.listaCanales li"):
            texto = li.get_text(strip=True)
            if "(" in texto:
                texto = texto.split("(", 1)[0].strip()
            if texto:
                canales.append(texto)

        urls_partido = []
        for canal in canales:
            canal_norm = normalizar(canal)
            if canal_norm in links_dict:
                urls_partido.extend(links_dict[canal_norm])  # Añadir todas las coincidencias

        # Eliminar duplicados
        urls_partido = list(dict.fromkeys(urls_partido))

        cursor.execute("""
            INSERT INTO partidos (equipo_local, equipo_visitante, hora, canales, urls_ipfs)
            VALUES (?, ?, ?, ?, ?)
        """, (equipo_local, equipo_visitante, hora, ", ".join(canales), ", ".join(urls_partido)))

    conn.commit()
    conn.close()
    print("Scraping completado con URLs IPFS filtradas y match exacto de canales.")

if __name__ == "__main__":
    scrapear()
