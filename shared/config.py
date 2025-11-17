"""
Configurazioni comuni per tutti i microservizi
"""
import os
from typing import Optional

class Settings:
    """Configurazioni globali del sistema"""

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database Settings
    DATABASE_DIR: str = os.getenv("DATABASE_DIR", "./databases")
    INIT_SCRIPTS_DIR: str = os.getenv("INIT_SCRIPTS_DIR", "./databases/init_scripts")

    # API Settings
    API_V1_PREFIX: str = "/api/v1"

    # Service Ports
    API_GATEWAY_PORT: int = 8000
    AUTH_SERVICE_PORT: int = 8001
    BENEFICIARY_SERVICE_PORT: int = 8002
    REQUEST_SERVICE_PORT: int = 8003
    CALCULATION_SERVICE_PORT: int = 8004
    ADMIN_SERVICE_PORT: int = 8005
    SYSTEM_SERVICE_PORT: int = 8006

    # Service URLs (per comunicazione interna)
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    BENEFICIARY_SERVICE_URL: str = os.getenv("BENEFICIARY_SERVICE_URL", "http://localhost:8002")
    REQUEST_SERVICE_URL: str = os.getenv("REQUEST_SERVICE_URL", "http://localhost:8003")
    CALCULATION_SERVICE_URL: str = os.getenv("CALCULATION_SERVICE_URL", "http://localhost:8004")
    ADMIN_SERVICE_URL: str = os.getenv("ADMIN_SERVICE_URL", "http://localhost:8005")
    SYSTEM_SERVICE_URL: str = os.getenv("SYSTEM_SERVICE_URL", "http://localhost:8006")

    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

settings = Settings()
