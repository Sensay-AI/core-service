from http import HTTPStatus
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from singleton_decorator import singleton

from app.core.config import API_AUDIENCE, AUTH0_ALGORITHMS, AUTH0_ISSUER, DOMAIN_AUTH0
from app.schemas.users import Auth0User


async def check_user(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> Auth0User:
    return Auth0Helper(token.credentials).verify_token()


def _check_claims(
    payload: dict[str, Any],
    claim_name: str,
    claim_type: Any,
    expected_value: list[str],
) -> None:
    instance_check = isinstance(payload[claim_name], claim_type)

    payload_claim = payload[claim_name]

    if claim_name not in payload or not instance_check:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"No claim '{claim_name}' found in token.",
        )

    if claim_name == "scope":
        payload_claim = payload[claim_name].split(" ")

    for value in expected_value:
        if value not in payload_claim:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=f"Insufficient {claim_name} ({value}). You "
                "don't have access to this resource",
            )


@singleton
class Auth0Helper(object):
    def __init__(
        self,
        token: str,
        permissions: Any = None,
        scopes: Any = None,
    ):
        self.signing_key = None
        self.token = token
        self.permissions: list[str] = permissions
        self.scopes: list[str] = scopes
        self.jwks_url = f"https://{DOMAIN_AUTH0}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(self.jwks_url)

    def verify_token(self) -> Auth0User:
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=error.__str__(),
            )
        except jwt.exceptions.DecodeError as error:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=error.__str__(),
            )

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=AUTH0_ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=AUTH0_ISSUER,
            )
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=str(e),
            )

        if self.scopes:
            _check_claims(payload, "scope", str, self.scopes)

        if self.permissions:
            _check_claims(payload, "permissions", list, self.permissions)

        user = Auth0User(**payload)
        user.permissions = payload["scope"].split(" ")
        return user
