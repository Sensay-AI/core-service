from http import HTTPStatus
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import API_AUDIENCE, AUTH0_ALGORITHMS, AUTH0_ISSUER, DOMAIN_AUTH0
from app.schemas.users import Auth0User


async def check_user(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> Auth0User:
    return Auth0Helper.verify_token(token.credentials)


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


class Auth0Helper(object):
    _jwks_url = f"https://{DOMAIN_AUTH0}/.well-known/jwks.json"
    _jwks_client = jwt.PyJWKClient(_jwks_url)

    @staticmethod
    def verify_token(
        token: str,
        permissions: Any = None,
        scopes: Any = None,
    ) -> Auth0User:
        try:
            signing_key = Auth0Helper._jwks_client.get_signing_key_from_jwt(token).key
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
                algorithms=AUTH0_ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=AUTH0_ISSUER,
            )
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=str(e),
            )

        if scopes:
            _check_claims(payload, "scope", str, scopes)

        if permissions:
            _check_claims(payload, "permissions", list, permissions)

        user = Auth0User(**payload)
        user.permissions = payload["scope"].split(" ")
        return user
