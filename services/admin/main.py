"""
Admin Service - Gestione parametri normativi
"""
from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.database import DatabaseManager
from shared.auth_utils import JWTManager
from shared.schemas import ColturaCreateAdmin, ContributoUnitarioCreate, CampagnaCreate

app = FastAPI(
    title="Admin Service",
    description="Servizio di gestione parametri normativi",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(settings.DATABASE_DIR, "admin.db")
db = DatabaseManager(DB_PATH)


def init_database():
    init_script_path = os.path.join(settings.DATABASE_DIR, "init_scripts", "init_admin.sql")
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
    return {"service": "admin", "status": "running", "version": "1.0.0"}


# Gestione Colture

@app.get("/colture")
async def get_colture(attiva: Optional[bool] = None):
    """Recupera colture"""
    if attiva is not None:
        colture = db.execute_query("SELECT * FROM colture WHERE attiva = ?", (1 if attiva else 0,))
    else:
        colture = db.execute_query("SELECT * FROM colture")

    return {"success": True, "data": colture}


@app.post("/colture", status_code=status.HTTP_201_CREATED)
async def create_coltura(coltura_data: ColturaCreateAdmin, authorization: str = Header(None)):
    """Crea coltura (solo amministratori)"""
    user = get_user_from_header(authorization)

    if user.get('role') != 'AMMINISTRATORE':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo amministratori")

    coltura_id = db.execute_update(
        "INSERT INTO colture (codice, descrizione, attiva) VALUES (?, ?, ?)",
        (coltura_data.codice, coltura_data.descrizione, 1 if coltura_data.attiva else 0)
    )

    coltura = db.execute_query("SELECT * FROM colture WHERE id = ?", (coltura_id,))[0]
    return {"success": True, "message": "Coltura creata", "data": coltura}


# Gestione Contributi

@app.get("/contributi")
async def get_contributi(campagna_id: Optional[int] = None):
    """Recupera contributi unitari"""
    if campagna_id:
        contributi = db.execute_query(
            """SELECT c.*, col.codice as coltura_codice, col.descrizione as coltura_descrizione
               FROM contributi_unitari c
               JOIN colture col ON c.coltura_id = col.id
               WHERE c.campagna_id = ?""",
            (campagna_id,)
        )
    else:
        contributi = db.execute_query(
            """SELECT c.*, col.codice as coltura_codice, col.descrizione as coltura_descrizione
               FROM contributi_unitari c
               JOIN colture col ON c.coltura_id = col.id"""
        )

    return {"success": True, "data": contributi}


@app.post("/contributi", status_code=status.HTTP_201_CREATED)
async def create_contributo(contributo_data: ContributoUnitarioCreate, authorization: str = Header(None)):
    """Crea contributo unitario (solo amministratori)"""
    user = get_user_from_header(authorization)

    if user.get('role') != 'AMMINISTRATORE':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo amministratori")

    contributo_id = db.execute_update(
        """INSERT INTO contributi_unitari (campagna_id, coltura_id, importo_per_mq, massimale_superficie, massimale_importo)
           VALUES (?, ?, ?, ?, ?)""",
        (
            contributo_data.campagna_id,
            contributo_data.coltura_id,
            contributo_data.importo_per_mq,
            contributo_data.massimale_superficie,
            contributo_data.massimale_importo
        )
    )

    contributo = db.execute_query("SELECT * FROM contributi_unitari WHERE id = ?", (contributo_id,))[0]
    return {"success": True, "message": "Contributo creato", "data": contributo}


# Gestione Campagne

@app.get("/campagne")
async def get_campagne(attiva: Optional[bool] = None):
    """Recupera campagne"""
    if attiva is not None:
        campagne = db.execute_query("SELECT * FROM campagne WHERE attiva = ?", (1 if attiva else 0,))
    else:
        campagne = db.execute_query("SELECT * FROM campagne")

    return {"success": True, "data": campagne}


@app.post("/campagne", status_code=status.HTTP_201_CREATED)
async def create_campagna(campagna_data: CampagnaCreate, authorization: str = Header(None)):
    """Crea campagna (solo amministratori)"""
    user = get_user_from_header(authorization)

    if user.get('role') != 'AMMINISTRATORE':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo amministratori")

    campagna_id = db.execute_update(
        "INSERT INTO campagne (anno, descrizione, data_inizio, data_fine, attiva) VALUES (?, ?, ?, ?, ?)",
        (campagna_data.anno, campagna_data.descrizione, campagna_data.data_inizio, campagna_data.data_fine, 1 if campagna_data.attiva else 0)
    )

    campagna = db.execute_query("SELECT * FROM campagne WHERE id = ?", (campagna_id,))[0]
    return {"success": True, "message": "Campagna creata", "data": campagna}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.ADMIN_SERVICE_PORT)
