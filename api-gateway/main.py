"""
API Gateway - Entry point centralizzato per tutti i microservizi
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from typing import Optional
import sys
import os

# Aggiungi la directory root al path per import shared
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.config import settings
from shared.auth_utils import JWTManager
from shared.schemas import ErrorResponse

# Inizializzazione app
app = FastAPI(
    title="API Gateway - Sistema Aiuti Agricoltura",
    description="Gateway centralizzato per accesso ai microservizi",
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

# Mapping servizi
SERVICE_URLS = {
    "auth": settings.AUTH_SERVICE_URL,
    "beneficiary": settings.BENEFICIARY_SERVICE_URL,
    "request": settings.REQUEST_SERVICE_URL,
    "calculation": settings.CALCULATION_SERVICE_URL,
    "admin": settings.ADMIN_SERVICE_URL,
    "system": settings.SYSTEM_SERVICE_URL,
}


# Dependency per validazione token
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Valida il token JWT e ritorna i dati utente

    Args:
        authorization: Header Authorization con Bearer token

    Returns:
        Payload del token decodificato

    Raises:
        HTTPException: Se il token non è valido
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token di autenticazione mancante",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Schema di autenticazione non valido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization malformato",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = JWTManager.decode_token(token)
    if not payload or payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def proxy_request(
    service: str,
    path: str,
    method: str,
    request: Request,
    token: Optional[str] = None,
    require_auth: bool = True
):
    """
    Proxy di una richiesta verso un microservizio

    Args:
        service: Nome del servizio di destinazione
        path: Path relativo al servizio
        method: Metodo HTTP
        request: Request FastAPI originale
        token: Token JWT da inoltrare
        require_auth: Se True, richiede autenticazione

    Returns:
        Risposta del microservizio

    Raises:
        HTTPException: In caso di errore
    """
    if service not in SERVICE_URLS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servizio '{service}' non trovato"
        )

    target_url = f"{SERVICE_URLS[service]}{path}"

    # Prepara headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Rimuovi host header

    # Body della richiesta
    try:
        body = await request.body()
    except Exception:
        body = None

    # Effettua la richiesta al microservizio
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Timeout nella comunicazione con {service}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Errore di connessione con {service}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Errore nella comunicazione con {service}: {str(e)}"
            )


# Root endpoint (Health check per Railway)
@app.get("/health")
async def health():
    """Health check API Gateway"""
    return {
        "service": "api-gateway",
        "status": "running",
        "version": "1.0.0",
        "services": list(SERVICE_URLS.keys())
    }


# Auth routes (pubbliche, no autenticazione richiesta)
@app.post(f"{settings.API_V1_PREFIX}/auth/login")
async def auth_login(request: Request):
    """Login utente"""
    return await proxy_request("auth", "/login", "POST", request, require_auth=False)


@app.post(f"{settings.API_V1_PREFIX}/auth/refresh")
async def auth_refresh(request: Request):
    """Refresh token"""
    return await proxy_request("auth", "/refresh", "POST", request, require_auth=False)


# Auth routes (protette)
@app.post(f"{settings.API_V1_PREFIX}/auth/users")
async def create_user(request: Request, current_user: dict = Depends(get_current_user)):
    """Crea nuovo utente (solo amministratori)"""
    if current_user.get('role') != 'AMMINISTRATORE':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli amministratori possono creare utenti"
        )
    return await proxy_request("auth", "/users", "POST", request)


@app.get(f"{settings.API_V1_PREFIX}/auth/users/{{user_id}}")
async def get_user(user_id: int, request: Request, current_user: dict = Depends(get_current_user)):
    """Recupera dati utente"""
    return await proxy_request("auth", f"/users/{user_id}", "GET", request)


# Beneficiary routes
@app.get(f"{settings.API_V1_PREFIX}/beneficiaries/fascicolo")
async def get_fascicolo(request: Request, current_user: dict = Depends(get_current_user)):
    """Recupera fascicolo beneficiario"""
    return await proxy_request("beneficiary", "/fascicolo", "GET", request)


@app.post(f"{settings.API_V1_PREFIX}/beneficiaries/fascicolo")
async def create_fascicolo(request: Request, current_user: dict = Depends(get_current_user)):
    """Crea fascicolo beneficiario"""
    return await proxy_request("beneficiary", "/fascicolo", "POST", request)


@app.get(f"{settings.API_V1_PREFIX}/beneficiaries/particelle")
async def get_particelle(request: Request, current_user: dict = Depends(get_current_user)):
    """Recupera particelle catastali"""
    return await proxy_request("beneficiary", "/particelle", "GET", request)


@app.post(f"{settings.API_V1_PREFIX}/beneficiaries/particelle")
async def create_particella(request: Request, current_user: dict = Depends(get_current_user)):
    """Aggiungi particella catastale"""
    return await proxy_request("beneficiary", "/particelle", "POST", request)


# Request routes
@app.get(f"{settings.API_V1_PREFIX}/requests/domande")
async def get_domande(request: Request, current_user: dict = Depends(get_current_user)):
    """Lista domande"""
    return await proxy_request("request", "/domande", "GET", request)


@app.post(f"{settings.API_V1_PREFIX}/requests/domande")
async def create_domanda(request: Request, current_user: dict = Depends(get_current_user)):
    """Crea nuova domanda"""
    return await proxy_request("request", "/domande", "POST", request)


@app.post(f"{settings.API_V1_PREFIX}/requests/domande/{{domanda_id}}/presenta")
async def presenta_domanda(domanda_id: int, request: Request, current_user: dict = Depends(get_current_user)):
    """Presenta domanda"""
    return await proxy_request("request", f"/domande/{domanda_id}/presenta", "POST", request)


# Calculation routes
@app.post(f"{settings.API_V1_PREFIX}/calculations/calcola/{{domanda_id}}")
async def calcola_contributo(domanda_id: int, request: Request, current_user: dict = Depends(get_current_user)):
    """Calcola contributo per domanda"""
    if current_user.get('role') not in ['ISTRUTTORE', 'AMMINISTRATORE']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo istruttori e amministratori possono calcolare contributi"
        )
    return await proxy_request("calculation", f"/calcola/{domanda_id}", "POST", request)


# Admin routes
@app.get(f"{settings.API_V1_PREFIX}/admin/colture")
async def get_colture(request: Request, current_user: dict = Depends(get_current_user)):
    """Lista colture"""
    return await proxy_request("admin", "/colture", "GET", request)


@app.post(f"{settings.API_V1_PREFIX}/admin/colture")
async def create_coltura(request: Request, current_user: dict = Depends(get_current_user)):
    """Crea coltura"""
    if current_user.get('role') != 'AMMINISTRATORE':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli amministratori possono gestire le colture"
        )
    return await proxy_request("admin", "/colture", "POST", request)


@app.get(f"{settings.API_V1_PREFIX}/admin/contributi")
async def get_contributi(request: Request, current_user: dict = Depends(get_current_user)):
    """Lista contributi unitari"""
    return await proxy_request("admin", "/contributi", "GET", request)


# System routes
@app.get(f"{settings.API_V1_PREFIX}/system/health")
async def system_health(request: Request, current_user: dict = Depends(get_current_user)):
    """Health check di tutti i servizi"""
    if current_user.get('role') != 'SISTEMISTA':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i sistemisti possono accedere al monitoring"
        )
    return await proxy_request("system", "/health", "GET", request)


# Mount static files (frontend) - deve essere dopo tutti gli endpoint API
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    # Railway usa la variabile PORT, altrimenti usa la porta di default
    port = int(os.getenv("PORT", settings.API_GATEWAY_PORT))
    uvicorn.run(app, host="0.0.0.0", port=port)
