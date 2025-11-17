"""
System Service - Monitoring e diagnostica
"""
from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import httpx
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.database import DatabaseManager
from shared.auth_utils import JWTManager

app = FastAPI(
    title="System Service",
    description="Servizio di monitoring e diagnostica",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(settings.DATABASE_DIR, "system.db")
db = DatabaseManager(DB_PATH)


def init_database():
    init_script_path = os.path.join(settings.DATABASE_DIR, "init_scripts", "init_system.sql")
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
    return {"service": "system", "status": "running", "version": "1.0.0"}


@app.get("/health")
async def health_check(authorization: str = Header(None)):
    """
    Verifica lo stato di tutti i microservizi

    Args:
        authorization: Token JWT

    Returns:
        Stato di tutti i servizi
    """
    user = get_user_from_header(authorization)

    if user.get('role') not in ['SISTEMISTA', 'AMMINISTRATORE']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo sistemisti e amministratori possono accedere"
        )

    services = {
        "auth": settings.AUTH_SERVICE_URL,
        "beneficiary": settings.BENEFICIARY_SERVICE_URL,
        "request": settings.REQUEST_SERVICE_URL,
        "calculation": settings.CALCULATION_SERVICE_URL,
        "admin": settings.ADMIN_SERVICE_URL,
    }

    results = {}

    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in services.items():
            start_time = time.time()
            try:
                response = await client.get(f"{service_url}/")
                response_time = (time.time() - start_time) * 1000  # ms
                status_text = "healthy" if response.status_code == 200 else "unhealthy"

                results[service_name] = {
                    "status": status_text,
                    "response_time_ms": round(response_time, 2),
                    "http_status": response.status_code
                }

                # Salva health check
                db.execute_update(
                    "INSERT INTO health_checks (servizio, status, response_time) VALUES (?, ?, ?)",
                    (service_name, status_text, response_time)
                )

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                results[service_name] = {
                    "status": "down",
                    "error": str(e),
                    "response_time_ms": round(response_time, 2)
                }

                # Salva health check
                db.execute_update(
                    "INSERT INTO health_checks (servizio, status, response_time, error_message) VALUES (?, ?, ?, ?)",
                    (service_name, "down", response_time, str(e))
                )

    # Calcola overall status
    all_healthy = all(r["status"] == "healthy" for r in results.values())
    overall_status = "healthy" if all_healthy else "degraded"

    return {
        "success": True,
        "overall_status": overall_status,
        "services": results,
        "timestamp": time.time()
    }


@app.get("/stats")
async def get_statistics(authorization: str = Header(None)):
    """
    Recupera statistiche di utilizzo

    Args:
        authorization: Token JWT

    Returns:
        Statistiche del sistema
    """
    user = get_user_from_header(authorization)

    if user.get('role') not in ['SISTEMISTA', 'AMMINISTRATORE']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo sistemisti e amministratori possono accedere"
        )

    # Conta database records (esempio)
    stats = {}

    try:
        # Auth DB
        auth_db = DatabaseManager(os.path.join(settings.DATABASE_DIR, "auth.db"))
        users_count = auth_db.execute_query("SELECT COUNT(*) as count FROM users")[0]['count']
        stats['total_users'] = users_count

        # Beneficiary DB
        ben_db = DatabaseManager(os.path.join(settings.DATABASE_DIR, "beneficiaries.db"))
        fascicoli_count = ben_db.execute_query("SELECT COUNT(*) as count FROM fascicoli")[0]['count']
        particelle_count = ben_db.execute_query("SELECT COUNT(*) as count FROM particelle_catastali")[0]['count']
        stats['total_fascicoli'] = fascicoli_count
        stats['total_particelle'] = particelle_count

        # Request DB
        req_db = DatabaseManager(os.path.join(settings.DATABASE_DIR, "requests.db"))
        domande_count = req_db.execute_query("SELECT COUNT(*) as count FROM domande")[0]['count']
        domande_by_stato = req_db.execute_query(
            "SELECT stato, COUNT(*) as count FROM domande GROUP BY stato"
        )
        stats['total_domande'] = domande_count
        stats['domande_by_stato'] = {row['stato']: row['count'] for row in domande_by_stato}

        # Admin DB
        admin_db_mgr = DatabaseManager(os.path.join(settings.DATABASE_DIR, "admin.db"))
        colture_count = admin_db_mgr.execute_query("SELECT COUNT(*) as count FROM colture WHERE attiva = 1")[0]['count']
        stats['total_colture_attive'] = colture_count

    except Exception as e:
        stats['error'] = str(e)

    return {
        "success": True,
        "data": stats
    }


@app.get("/logs/audit")
async def get_audit_logs(limit: int = 100, authorization: str = Header(None)):
    """Recupera audit logs"""
    user = get_user_from_header(authorization)

    if user.get('role') != 'SISTEMISTA':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo sistemisti possono accedere ai log"
        )

    logs = db.execute_query(
        "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )

    return {
        "success": True,
        "data": logs
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SYSTEM_SERVICE_PORT)
