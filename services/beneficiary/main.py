"""
Beneficiary Service - Gestione fascicoli aziendali
"""
from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import sys
import os

# Aggiungi la directory root al path per import shared
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.database import DatabaseManager
from shared.auth_utils import JWTManager
from shared.schemas import (
    FascicoloCreate,
    DatiBancariCreate,
    ParticellaCatastaleCreate,
    MacchinarioCreate,
    BaseResponse
)

# Inizializzazione app
app = FastAPI(
    title="Beneficiary Service",
    description="Servizio di gestione fascicoli aziendali",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DB_PATH = os.path.join(settings.DATABASE_DIR, "beneficiaries.db")
db = DatabaseManager(DB_PATH)


def init_database():
    """Inizializza il database con lo schema"""
    init_script_path = os.path.join(settings.INIT_SCRIPTS_DIR, "init_beneficiary.sql")
    if os.path.exists(init_script_path):
        with open(init_script_path, 'r') as f:
            db.execute_script(f.read())
        print(f"Database inizializzato: {DB_PATH}")


@app.on_event("startup")
async def startup_event():
    init_database()


def get_user_from_header(authorization: Optional[str] = Header(None)) -> dict:
    """Estrae e valida user da JWT token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token mancante"
        )

    try:
        scheme, token = authorization.split()
        payload = JWTManager.decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token non valido"
            )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticazione fallita"
        )


# Endpoints

@app.get("/")
async def root():
    """Health check"""
    return {"service": "beneficiary", "status": "running", "version": "1.0.0"}


# Gestione Fascicoli

@app.post("/fascicolo", status_code=status.HTTP_201_CREATED)
async def create_fascicolo(
    fascicolo_data: FascicoloCreate,
    authorization: str = Header(None)
):
    """
    Crea un nuovo fascicolo aziendale

    Args:
        fascicolo_data: Dati del fascicolo
        authorization: Token JWT

    Returns:
        Fascicolo creato
    """
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])

    # Verifica che l'utente non abbia già un fascicolo
    existing = db.execute_query(
        "SELECT id FROM fascicoli WHERE user_id = ?",
        (user_id,)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fascicolo già esistente per questo utente"
        )

    # Verifica che CF/PIVA non sia già usato
    existing_cf = db.execute_query(
        "SELECT id FROM fascicoli WHERE cf_piva = ?",
        (fascicolo_data.cf_piva,)
    )

    if existing_cf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CF/PIVA già registrato"
        )

    # Inserisci fascicolo
    fascicolo_id = db.execute_update(
        """INSERT INTO fascicoli
           (user_id, ragione_sociale, cf_piva, indirizzo, cap, comune, provincia, telefono, email)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            fascicolo_data.ragione_sociale,
            fascicolo_data.cf_piva,
            fascicolo_data.indirizzo,
            fascicolo_data.cap,
            fascicolo_data.comune,
            fascicolo_data.provincia,
            fascicolo_data.telefono,
            fascicolo_data.email
        )
    )

    # Recupera fascicolo creato
    fascicolo = db.execute_query("SELECT * FROM fascicoli WHERE id = ?", (fascicolo_id,))[0]

    return {
        "success": True,
        "message": "Fascicolo creato con successo",
        "data": fascicolo
    }


@app.get("/fascicolo")
async def get_fascicolo(authorization: str = Header(None)):
    """
    Recupera il fascicolo dell'utente autenticato

    Args:
        authorization: Token JWT

    Returns:
        Fascicolo dell'utente
    """
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])
    role = user.get('role')

    # Se è BENEFICIARIO, mostra solo il suo fascicolo
    if role == 'BENEFICIARIO':
        fascicoli = db.execute_query(
            "SELECT * FROM fascicoli WHERE user_id = ?",
            (user_id,)
        )
    else:
        # ISTRUTTORE, AMMINISTRATORE, SISTEMISTA possono vedere tutti
        fascicoli = db.execute_query("SELECT * FROM fascicoli")

    return {
        "success": True,
        "data": fascicoli
    }


@app.get("/fascicolo/{fascicolo_id}")
async def get_fascicolo_by_id(fascicolo_id: int, authorization: str = Header(None)):
    """
    Recupera un fascicolo specifico per ID

    Args:
        fascicolo_id: ID del fascicolo
        authorization: Token JWT

    Returns:
        Fascicolo richiesto
    """
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])
    role = user.get('role')

    fascicolo = db.execute_query(
        "SELECT * FROM fascicoli WHERE id = ?",
        (fascicolo_id,)
    )

    if not fascicolo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fascicolo non trovato"
        )

    # Verifica permessi
    if role == 'BENEFICIARIO' and fascicolo[0]['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato ad accedere a questo fascicolo"
        )

    return {
        "success": True,
        "data": fascicolo[0]
    }


# Gestione Dati Bancari

@app.post("/fascicolo/{fascicolo_id}/dati-bancari", status_code=status.HTTP_201_CREATED)
async def create_dati_bancari(
    fascicolo_id: int,
    dati: DatiBancariCreate,
    authorization: str = Header(None)
):
    """
    Aggiungi dati bancari al fascicolo

    Args:
        fascicolo_id: ID del fascicolo
        dati: Dati bancari
        authorization: Token JWT

    Returns:
        Dati bancari creati
    """
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])

    # Verifica che il fascicolo appartenga all'utente
    fascicolo = db.execute_query(
        "SELECT * FROM fascicoli WHERE id = ? AND user_id = ?",
        (fascicolo_id, user_id)
    )

    if not fascicolo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fascicolo non trovato o non autorizzato"
        )

    # Inserisci dati bancari
    dati_id = db.execute_update(
        """INSERT INTO dati_bancari (fascicolo_id, iban, bic, intestatario)
           VALUES (?, ?, ?, ?)""",
        (fascicolo_id, dati.iban, dati.bic, dati.intestatario)
    )

    dati_bancari = db.execute_query(
        "SELECT * FROM dati_bancari WHERE id = ?",
        (dati_id,)
    )[0]

    return {
        "success": True,
        "message": "Dati bancari aggiunti con successo",
        "data": dati_bancari
    }


@app.get("/fascicolo/{fascicolo_id}/dati-bancari")
async def get_dati_bancari(fascicolo_id: int, authorization: str = Header(None)):
    """Recupera dati bancari di un fascicolo"""
    user = get_user_from_header(authorization)

    dati = db.execute_query(
        "SELECT * FROM dati_bancari WHERE fascicolo_id = ?",
        (fascicolo_id,)
    )

    return {
        "success": True,
        "data": dati
    }


# Gestione Particelle Catastali

@app.post("/particelle", status_code=status.HTTP_201_CREATED)
async def create_particella(
    particella_data: ParticellaCatastaleCreate,
    fascicolo_id: int,
    authorization: str = Header(None)
):
    """
    Aggiungi particella catastale

    Args:
        particella_data: Dati particella
        fascicolo_id: ID fascicolo (query param)
        authorization: Token JWT

    Returns:
        Particella creata
    """
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])

    # Verifica fascicolo
    fascicolo = db.execute_query(
        "SELECT * FROM fascicoli WHERE id = ? AND user_id = ?",
        (fascicolo_id, user_id)
    )

    if not fascicolo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fascicolo non trovato"
        )

    # Inserisci particella
    particella_id = db.execute_update(
        """INSERT INTO particelle_catastali
           (fascicolo_id, comune, foglio, particella, subalterno, superficie_mq,
            superficie_calcolata_mq, coordinate_geojson, centroid_lat, centroid_lng)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            fascicolo_id,
            particella_data.comune,
            particella_data.foglio,
            particella_data.particella,
            particella_data.subalterno,
            particella_data.superficie_mq,
            particella_data.superficie_calcolata_mq,
            particella_data.coordinate_geojson,
            particella_data.centroid_lat,
            particella_data.centroid_lng
        )
    )

    particella = db.execute_query(
        "SELECT * FROM particelle_catastali WHERE id = ?",
        (particella_id,)
    )[0]

    return {
        "success": True,
        "message": "Particella aggiunta con successo",
        "data": particella
    }


@app.get("/particelle")
async def get_particelle(fascicolo_id: Optional[int] = None, authorization: str = Header(None)):
    """
    Recupera particelle catastali

    Args:
        fascicolo_id: Filtra per fascicolo (opzionale)
        authorization: Token JWT

    Returns:
        Lista particelle
    """
    user = get_user_from_header(authorization)

    if fascicolo_id:
        particelle = db.execute_query(
            "SELECT * FROM particelle_catastali WHERE fascicolo_id = ?",
            (fascicolo_id,)
        )
    else:
        particelle = db.execute_query("SELECT * FROM particelle_catastali")

    return {
        "success": True,
        "data": particelle
    }


# Gestione Macchinari

@app.post("/macchinari", status_code=status.HTTP_201_CREATED)
async def create_macchinario(
    macchinario_data: MacchinarioCreate,
    fascicolo_id: int,
    authorization: str = Header(None)
):
    """Aggiungi macchinario"""
    user = get_user_from_header(authorization)
    user_id = int(user['sub'])

    # Verifica fascicolo
    fascicolo = db.execute_query(
        "SELECT * FROM fascicoli WHERE id = ? AND user_id = ?",
        (fascicolo_id, user_id)
    )

    if not fascicolo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fascicolo non trovato"
        )

    # Inserisci macchinario
    macchinario_id = db.execute_update(
        """INSERT INTO macchinari (fascicolo_id, tipo, marca, modello, anno, targa)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            fascicolo_id,
            macchinario_data.tipo,
            macchinario_data.marca,
            macchinario_data.modello,
            macchinario_data.anno,
            macchinario_data.targa
        )
    )

    macchinario = db.execute_query(
        "SELECT * FROM macchinari WHERE id = ?",
        (macchinario_id,)
    )[0]

    return {
        "success": True,
        "message": "Macchinario aggiunto con successo",
        "data": macchinario
    }


@app.get("/macchinari")
async def get_macchinari(fascicolo_id: Optional[int] = None, authorization: str = Header(None)):
    """Recupera macchinari"""
    user = get_user_from_header(authorization)

    if fascicolo_id:
        macchinari = db.execute_query(
            "SELECT * FROM macchinari WHERE fascicolo_id = ?",
            (fascicolo_id,)
        )
    else:
        macchinari = db.execute_query("SELECT * FROM macchinari")

    return {
        "success": True,
        "data": macchinari
    }


if __name__ == "__main__":
    import uvicorn
    # Railway usa la variabile PORT, altrimenti usa la porta di default
    port = int(os.getenv("PORT", settings.BENEFICIARY_SERVICE_PORT))
    uvicorn.run(app, host="0.0.0.0", port=port)
