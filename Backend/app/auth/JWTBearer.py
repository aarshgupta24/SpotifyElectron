"""JWT Token validation and injection for endpoints"""

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import app.auth.security_service as security_service
from app.auth.security_schema import (
    BadJWTTokenProvidedException,
    JWTValidationException,
    TokenData,
)
from app.auth.security_service import get_jwt_token_data
from app.logging.logging_constants import LOGGING_JWT_BEARER
from app.logging.logging_schema import SpotifyElectronLogger

jwt_bearer_logger = SpotifyElectronLogger(LOGGING_JWT_BEARER).getLogger()

TOKEN_HEADER_NAME = "authorization"
BEARER_SCHEME_NAME = "Bearer"


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> TokenData:
        """Returns Token data or 403 Code if credentials are invalid

        Args:
            request (Request): the incoming request

        Raises:
            BadJWTTokenProvidedException: invalid credentials

        Returns:
            TokenData: the token data
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)  # type: ignore
        if not credentials or credentials.scheme != BEARER_SCHEME_NAME:
            raise BadJWTTokenProvidedException
        try:
            jwt_raw = credentials.credentials
            security_service.validate_jwt(jwt_raw)
            jwt_token_data = get_jwt_token_data(credentials.credentials)
        except (JWTValidationException, Exception):
            jwt_bearer_logger.exception(f"Request with invalid JWT {jwt_raw} {request}")
            raise BadJWTTokenProvidedException
        else:
            return jwt_token_data
