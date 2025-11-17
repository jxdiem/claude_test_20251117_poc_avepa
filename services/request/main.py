"""
Request Service - Gestione domande di aiuto
"""
from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.database import DatabaseManager
from shared.auth_utils import JWTManager
from shared.schemas import DomandaStato, DomandaCreate

app = FastAPI(
    title="Request Service",
    description="Servizio di gestione domande di aiuto",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(settings.DATABASE_DIR, "requests.db")
db = DatabaseManager(DB_PATH)


def init_database():
    init_script_path = os.path.join(settings.INIT_SCRIPTS_DIR, "init_request.sql")
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
    return {"service": "request", "status": "running", "version": "1.0.0"}


@app.post("/domande", status_code=status.HTTP_201_CREATED)
async def create_domanda(domanda_data: DomandaCreate, fascicolo_id: int, authorization: str = Header(None)):
    """Crea una nuova domanda di aiuto"""
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])

    # Inserisci domanda
    domanda_id = db.execute_update(
        "INSERT INTO domande (fascicolo_id, anno_campagna, stato) VALUES (?, ?, 'BOZZA')",
        (fascicolo_id, domanda_data.anno_campagna)
    )

    # Inserisci colture dichiarate
    for coltura in domanda_data.colture:
        db.execute_update(
            """INSERT INTO colture_dichiarate (domanda_id, particella_id, coltura_id, superficie_mq)
               VALUES (?, ?, ?, ?)""",
            (domanda_id, coltura.particella_id, coltura.coltura_id, coltura.superficie_mq)
        )

    domanda = db.execute_query("SELECT * FROM domande WHERE id = ?", (domanda_id,))[0]
    colture = db.execute_query("SELECT * FROM colture_dichiarate WHERE domanda_id = ?", (domanda_id,))

    return {
        "success": True,
        "message": "Domanda creata con successo",
        "data": {
            "domanda": domanda,
            "colture": colture
        }
    }


@app.get("/domande")
async def get_domande(authorization: str = Header(None)):
    """Recupera domande"""
    user = get_user_from_header(authorization)
    role = user.get('role')

    if role == 'BENEFICIARIO':
        # Mostra solo domande proprie (tramite fascicolo_id)
        domande = db.execute_query("SELECT * FROM domande")
    else:
        # Istruttori e admin vedono tutto
        domande = db.execute_query("SELECT * FROM domande")

    return {"success": True, "data": domande}


@app.get("/domande/{domanda_id}")
async def get_domanda(domanda_id: int, authorization: str = Header(None)):
    """Recupera dettagli domanda"""
    user = get_user_from_header(authorization)

    domanda = db.execute_query("SELECT * FROM domande WHERE id = ?", (domanda_id,))
    if not domanda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domanda non trovata")

    colture = db.execute_query("SELECT * FROM colture_dichiarate WHERE domanda_id = ?", (domanda_id,))
    note = db.execute_query("SELECT * FROM note_istruttoria WHERE domanda_id = ?", (domanda_id,))

    return {
        "success": True,
        "data": {
            "domanda": domanda[0],
            "colture": colture,
            "note": note
        }
    }


@app.post("/domande/{domanda_id}/presenta")
async def presenta_domanda(domanda_id: int, authorization: str = Header(None)):
    """Presenta domanda (da BOZZA a PRESENTATA)"""
    user = get_user_from_header(authorization)

    domanda = db.execute_query("SELECT * FROM domande WHERE id = ?", (domanda_id,))
    if not domanda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domanda non trovata")

    if domanda[0]['stato'] != 'BOZZA':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo domande in bozza possono essere presentate")

    db.execute_update(
        "UPDATE domande SET stato = 'PRESENTATA', data_presentazione = ? WHERE id = ?",
        (datetime.now().isoformat(), domanda_id)
    )

    return {"success": True, "message": "Domanda presentata con successo"}


@app.post("/domande/{domanda_id}/istruttoria")
async def avvia_istruttoria(domanda_id: int, authorization: str = Header(None)):
    """Avvia istruttoria (da PRESENTATA a IN_ISTRUTTORIA)"""
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])
    role = user.get('role')

    if role not in ['ISTRUTTORE', 'AMMINISTRATORE']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo istruttori possono avviare l'istruttoria")

    domanda = db.execute_query("SELECT * FROM domande WHERE id = ?", (domanda_id,))
    if not domanda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domanda non trovata")

    db.execute_update(
        "UPDATE domande SET stato = 'IN_ISTRUTTORIA', istruttore_id = ?, data_istruttoria = ? WHERE id = ?",
        (user_id, datetime.now().isoformat(), domanda_id)
    )

    return {"success": True, "message": "Istruttoria avviata"}


@app.post("/domande/{domanda_id}/approva")
async def approva_domanda(domanda_id: int, authorization: str = Header(None)):
    """Approva domanda"""
    user = get_user_from_header(authorization)
    role = user.get('role')

    if role not in ['ISTRUTTORE', 'AMMINISTRATORE']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo istruttori possono approvare")

    db.execute_update("UPDATE domande SET stato = 'APPROVATA' WHERE id = ?", (domanda_id,))
    return {"success": True, "message": "Domanda approvata"}


@app.post("/domande/{domanda_id}/respingi")
async def respingi_domanda(domanda_id: int, motivo: str, authorization: str = Header(None)):
    """Respingi domanda"""
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])
    role = user.get('role')

    if role not in ['ISTRUTTORE', 'AMMINISTRATORE']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo istruttori possono respingere")

    db.execute_update("UPDATE domande SET stato = 'RESPINTA' WHERE id = ?", (domanda_id,))
    db.execute_update(
        "INSERT INTO note_istruttoria (domanda_id, istruttore_id, nota) VALUES (?, ?, ?)",
        (domanda_id, user_id, f"RESPINTA: {motivo}")
    )

    return {"success": True, "message": "Domanda respinta"}


if __name__ == "__main__":
    import uvicorn
    # Railway usa la variabile PORT, altrimenti usa la porta di default
    port = int(os.getenv("PORT", settings.REQUEST_SERVICE_PORT))
    uvicorn.run(app, host="0.0.0.0", port=port)
