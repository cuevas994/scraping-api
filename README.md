# Scraper de La Liga con IPFS

Este proyecto hace scraping de LaLiga desde futbolenlatv.es, obtiene links de IPFS y los guarda en PostgreSQL. También expone una API REST con FastAPI.

## Setup local

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
export DATABASE_URL="postgres://user:pass@host:port/dbname"
python scraper.py
uvicorn app:app --reload
