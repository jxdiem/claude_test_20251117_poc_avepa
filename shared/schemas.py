"""
Schemi Pydantic comuni per validazione dati
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enumerazioni comuni

class UserRole(str, Enum):
    """Ruoli utente"""
    BENEFICIARIO = "BENEFICIARIO"
    ISTRUTTORE = "ISTRUTTORE"
    AMMINISTRATORE = "AMMINISTRATORE"
    SISTEMISTA = "SISTEMISTA"


class DomandaStato(str, Enum):
    """Stati domanda"""
    BOZZA = "BOZZA"
    PRESENTATA = "PRESENTATA"
    IN_ISTRUTTORIA = "IN_ISTRUTTORIA"
    APPROVATA = "APPROVATA"
    RESPINTA = "RESPINTA"
    LIQUIDATA = "LIQUIDATA"


# Schemi base

class BaseResponse(BaseModel):
    """Schema base per risposte API"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """Schema per risposte paginate"""
    success: bool
    data: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Schema per errori"""
    success: bool = False
    error: str
    detail: Optional[str] = None


# Schemi Auth

class LoginRequest(BaseModel):
    """Schema per richiesta login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    """Schema per risposta login"""
    success: bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: UserRole


class TokenRefreshRequest(BaseModel):
    """Schema per richiesta refresh token"""
    refresh_token: str


class UserCreate(BaseModel):
    """Schema per creazione utente"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole


class UserResponse(BaseModel):
    """Schema per risposta utente"""
    id: int
    username: str
    email: str
    role: UserRole
    active: bool
    created_at: str


# Schemi Fascicolo

class DatiBancariCreate(BaseModel):
    """Schema per creazione dati bancari"""
    iban: str = Field(..., min_length=15, max_length=34)
    bic: Optional[str] = Field(None, max_length=11)
    intestatario: str = Field(..., max_length=200)

    @validator('iban')
    def validate_iban(cls, v):
        """Validazione IBAN base"""
        v = v.replace(' ', '').upper()
        if not v.startswith('IT'):
            raise ValueError('IBAN deve iniziare con IT')
        if len(v) != 27:
            raise ValueError('IBAN italiano deve essere di 27 caratteri')
        return v


class ParticellaCatastaleCreate(BaseModel):
    """Schema per creazione particella catastale"""
    comune: str = Field(..., max_length=100)
    foglio: str = Field(..., max_length=20)
    particella: str = Field(..., max_length=20)
    subalterno: Optional[str] = Field(None, max_length=20)
    superficie_mq: float = Field(..., gt=0)
    superficie_calcolata_mq: Optional[float] = Field(None, gt=0)
    coordinate_geojson: Optional[str] = None  # GeoJSON Polygon/MultiPolygon
    centroid_lat: Optional[float] = Field(None, ge=-90, le=90)
    centroid_lng: Optional[float] = Field(None, ge=-180, le=180)


class MacchinarioCreate(BaseModel):
    """Schema per creazione macchinario"""
    tipo: str = Field(..., max_length=100)
    marca: str = Field(..., max_length=100)
    modello: str = Field(..., max_length=100)
    anno: Optional[int] = Field(None, ge=1900, le=2100)
    targa: Optional[str] = Field(None, max_length=20)


class FascicoloCreate(BaseModel):
    """Schema per creazione fascicolo"""
    ragione_sociale: str = Field(..., max_length=200)
    cf_piva: str = Field(..., min_length=11, max_length=16)
    indirizzo: str = Field(..., max_length=200)
    cap: str = Field(..., pattern=r'^\d{5}$')
    comune: str = Field(..., max_length=100)
    provincia: str = Field(..., min_length=2, max_length=2)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


# Schemi Domanda

class ColturaCreate(BaseModel):
    """Schema per associazione coltura a particella"""
    particella_id: int
    coltura_id: int
    superficie_mq: float = Field(..., gt=0)


class DomandaCreate(BaseModel):
    """Schema per creazione domanda"""
    anno_campagna: int = Field(..., ge=2020, le=2100)
    colture: List[ColturaCreate]


class DomandaUpdate(BaseModel):
    """Schema per aggiornamento domanda"""
    colture: Optional[List[ColturaCreate]] = None


# Schemi Admin

class ColturaCreateAdmin(BaseModel):
    """Schema per creazione coltura (admin)"""
    codice: str = Field(..., max_length=20)
    descrizione: str = Field(..., max_length=200)
    attiva: bool = True


class ContributoUnitarioCreate(BaseModel):
    """Schema per creazione contributo unitario"""
    campagna_id: int
    coltura_id: int
    importo_per_mq: float = Field(..., gt=0)
    massimale_superficie: Optional[float] = Field(None, gt=0)
    massimale_importo: Optional[float] = Field(None, gt=0)


class CampagnaCreate(BaseModel):
    """Schema per creazione campagna"""
    anno: int = Field(..., ge=2020, le=2100)
    descrizione: str = Field(..., max_length=200)
    data_inizio: str  # ISO format
    data_fine: str  # ISO format
    attiva: bool = True
