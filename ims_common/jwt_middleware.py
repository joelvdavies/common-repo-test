"""
Module for providing an implementation of the `JWTBearer` class.
"""

import logging
import sys

import jwt
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from ims_common.config import AuthenticationConfig

logger = logging.getLogger()

security = HTTPBearer(auto_error=True)


def create_jwt_middleware(auth_config: AuthenticationConfig):

    # Read the content of the public key file into a constant. This is used for decoding of JWT access tokens.
    try:
        with open(auth_config.public_key_path, "r", encoding="utf-8") as file:
            PUBLIC_KEY = file.read()
    except FileNotFoundError as exc:
        sys.exit(f"Cannot find public key: {exc}")

    class JWTMiddleware(BaseHTTPMiddleware):
        """
        A middleware class to provide JSON Web Token (JWT) based authentication/authorization.
        """

        async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
        ) -> Response:
            """
            Performs JWT access token authentication/authorization before processing the request.

            :param request: The Starlette `Request` object.
            :param call_next: The next function to call to process the `Request` object.
            :return: The JWT access token if authentication is successful.
            :raises HTTPException: If the supplied JWT access token is invalid or has expired.
            """
            # `config.api.root_path` is not part of `request.url.path` so we are not checking for it
            if request.url.path not in ["/docs", "/openapi.json"]:
                try:
                    credentials: HTTPAuthorizationCredentials = await security(request)
                except HTTPException as exc:
                    # Cannot raise HttpException here, so must do manually
                    return JSONResponse(
                        status_code=exc.status_code, content={"detail": exc.detail}
                    )

                if not self._is_jwt_access_token_valid(credentials.credentials):
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Invalid token or expired token"},
                    )

            return await call_next(request)

        def _is_jwt_access_token_valid(self, access_token: str) -> bool:
            """
            Check if the JWT access token is valid.

            It does this by checking that it was signed by the corresponding private key and has not expired. It also
            requires the payload to contain a username.
            :param access_token: The JWT access token to check.
            :return: `True` if the JWT access token is valid and its payload contains a username, `False` otherwise.
            """
            logger.info("Checking if JWT access token is valid")
            try:
                payload = jwt.decode(
                    access_token,
                    PUBLIC_KEY,
                    algorithms=[auth_config.jwt_algorithm],
                )
            except Exception:  # pylint: disable=broad-exception-caught)
                logger.exception("Error decoding JWT access token")
                payload = None

            return payload is not None and "username" in payload

    return JWTMiddleware
