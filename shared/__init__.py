"""
Modulo shared con componenti comuni per tutti i microservizi
"""
from shared.config import settings
from shared.database import DatabaseManager
from shared.auth_utils import PasswordHasher, JWTManager, get_role_permissions
from shared.schemas import (
    UserRole,
    DomandaStato,
    BaseResponse,
    ErrorResponse,
    LoginRequest,
    LoginResponse,
)

__all__ = [
    "settings",
    "DatabaseManager",
    "PasswordHasher",
    "JWTManager",
    "get_role_permissions",
    "UserRole",
    "DomandaStato",
    "BaseResponse",
    "ErrorResponse",
    "LoginRequest",
    "LoginResponse",
]
