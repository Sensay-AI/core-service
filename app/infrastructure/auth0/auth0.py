import logging
from http import HTTPStatus
from typing import Any

import jwt
from fastapi import HTTPException

from app.models.schemas.users import Auth0User


def check_claims(
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


class Auth0Service:
    auth0_issuer: str
    api_audience: str
    auth0_algorithms: str

    def __init__(
        self, domain: str, algorithms: str, audience: str, issuer: str
    ) -> None:
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )
        self._jwks_url = f"https://{domain}/.well-known/jwks.json"
        self._jwks_client = jwt.PyJWKClient(self._jwks_url)
        self.auth0_algorithms = algorithms
        self.api_audience = audience
        self.auth0_issuer = issuer

    def verify_token(
        self,
        token: str,
        permissions: Any = None,
        scopes: Any = None,
    ) -> Auth0User:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token).key
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
                token,
                signing_key,
                algorithms=self.auth0_algorithms,
                audience=self.api_audience,
                issuer=self.auth0_issuer,
            )
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=str(e),
            )

        if scopes:
            check_claims(payload, "scope", str, scopes)

        if permissions:
            check_claims(payload, "permissions", list, permissions)

        user = Auth0User(**payload)
        user.permissions = payload["scope"].split(" ")
        return user
