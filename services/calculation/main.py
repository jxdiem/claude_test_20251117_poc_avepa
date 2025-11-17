"""
Calculation Service - Calcolo contributi
"""
from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import httpx
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.database import DatabaseManager
from shared.auth_utils import JWTManager

app = FastAPI(
    title="Calculation Service",
    description="Servizio di calcolo contributi",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(settings.DATABASE_DIR, "calculations.db")
db = DatabaseManager(DB_PATH)

# Database per lettura dati da altri servizi
REQUEST_DB_PATH = os.path.join(settings.DATABASE_DIR, "requests.db")
ADMIN_DB_PATH = os.path.join(settings.DATABASE_DIR, "admin.db")
request_db = DatabaseManager(REQUEST_DB_PATH)
admin_db = DatabaseManager(ADMIN_DB_PATH)


def init_database():
    init_script_path = os.path.join(settings.DATABASE_DIR, "init_scripts", "init_calculation.sql")
    if os.path.exists(init_script_path):
        with open(init_script_path, 'r') as f:
            db.execute_script(f.read())
        print(f"Database inizializzato: {DB_PATH}")


@app.on_event("startup")
async def startup_event():
    init_database()


def get_user_from_header(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    try:
        scheme, token = authorization.split()
        payload = JWTManager.decode_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido")
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticazione fallita")


@app.get("/")
async def root():
    return {"service": "calculation", "status": "running", "version": "1.0.0"}


@app.post("/calcola/{domanda_id}")
async def calcola_contributo(domanda_id: int, authorization: str = Header(None)):
    """
    Calcola il contributo per una domanda

    Args:
        domanda_id: ID della domanda
        authorization: Token JWT

    Returns:
        Calcolo del contributo
    """
    user = get_user_from_header(authorization)

    # Recupera domanda
    domanda = request_db.execute_query("SELECT * FROM domande WHERE id = ?", (domanda_id,))
    if not domanda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domanda non trovata")

    domanda = domanda[0]
    anno_campagna = domanda['anno_campagna']

    # Recupera campagna
    campagna = admin_db.execute_query("SELECT * FROM campagne WHERE anno = ?", (anno_campagna,))
    if not campagna:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campagna non trovata")

    campagna_id = campagna[0]['id']

    # Recupera colture dichiarate
    colture_dichiarate = request_db.execute_query(
        "SELECT * FROM colture_dichiarate WHERE domanda_id = ?",
        (domanda_id,)
    )

    if not colture_dichiarate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nessuna coltura dichiarata")

    # Calcola contributo per ogni coltura
    importo_totale = 0
    dettagli = []

    for coltura_dich in colture_dichiarate:
        coltura_id = coltura_dich['coltura_id']
        superficie_mq = coltura_dich['superficie_mq']

        # Recupera contributo unitario
        contributo = admin_db.execute_query(
            """SELECT * FROM contributi_unitari
               WHERE campagna_id = ? AND coltura_id = ?""",
            (campagna_id, coltura_id)
        )

        if not contributo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contributo non trovato per coltura {coltura_id}"
            )

        contributo = contributo[0]
        importo_per_mq = contributo['importo_per_mq']
        massimale_superficie = contributo['massimale_superficie']
        massimale_importo = contributo['massimale_importo']

        # Calcola importo
        superficie_calcolata = min(superficie_mq, massimale_superficie) if massimale_superficie else superficie_mq
        importo = superficie_calcolata * importo_per_mq

        if massimale_importo and importo > massimale_importo:
            importo = massimale_importo

        importo_totale += importo

        dettagli.append({
            "coltura_id": coltura_id,
            "superficie_mq": superficie_mq,
            "superficie_calcolata": superficie_calcolata,
            "importo_unitario": importo_per_mq,
            "importo": importo,
            "massimale_applicato": importo < (superficie_mq * importo_per_mq)
        })

    # Verifica se esiste già un calcolo per questa domanda
    existing = db.execute_query("SELECT id FROM calcoli WHERE domanda_id = ?", (domanda_id,))

    if existing:
        # Aggiorna
        calcolo_id = existing[0]['id']
        db.execute_update(
            "UPDATE calcoli SET importo_totale = ?, dettaglio_json = ?, data_calcolo = datetime('now') WHERE id = ?",
            (importo_totale, json.dumps(dettagli), calcolo_id)
        )
    else:
        # Inserisci nuovo calcolo
        calcolo_id = db.execute_update(
            "INSERT INTO calcoli (domanda_id, importo_totale, dettaglio_json) VALUES (?, ?, ?)",
            (domanda_id, importo_totale, json.dumps(dettagli))
        )

        # Inserisci dettagli
        for dettaglio in dettagli:
            db.execute_update(
                """INSERT INTO dettaglio_calcolo (calcolo_id, coltura_id, superficie_mq, importo_unitario, importo_totale)
                   VALUES (?, ?, ?, ?, ?)""",
                (calcolo_id, dettaglio['coltura_id'], dettaglio['superficie_mq'],
                 dettaglio['importo_unitario'], dettaglio['importo'])
            )

    # Aggiorna importo nella domanda
    request_db.execute_update(
        "UPDATE domande SET importo_calcolato = ? WHERE id = ?",
        (importo_totale, domanda_id)
    )

    return {
        "success": True,
        "data": {
            "calcolo_id": calcolo_id,
            "domanda_id": domanda_id,
            "importo_totale": importo_totale,
            "dettagli": dettagli
        }
    }


@app.get("/calcoli/{domanda_id}")
async def get_calcolo(domanda_id: int, authorization: str = Header(None)):
    """Recupera calcolo per una domanda"""
    user = get_user_from_header(authorization)

    calcolo = db.execute_query("SELECT * FROM calcoli WHERE domanda_id = ?", (domanda_id,))

    if not calcolo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calcolo non trovato")

    calcolo = calcolo[0]
    dettagli = json.loads(calcolo['dettaglio_json']) if calcolo['dettaglio_json'] else []

    return {
        "success": True,
        "data": {
            **calcolo,
            "dettagli": dettagli
        }
    }


if __name__ == "__main__":
    import uvicorn
    # Railway usa la variabile PORT, altrimenti usa la porta di default
    port = int(os.getenv("PORT", settings.CALCULATION_SERVICE_PORT))
    uvicorn.run(app, host="0.0.0.0", port=port)
