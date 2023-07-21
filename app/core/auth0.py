import jwt
from app.core.config import DOMAIN_AUTH0, API_AUDIENCE, ISSUER, ALGORITHMS
from fastapi.security import HTTPBearer
from fastapi import Depends
from typing import Any
from app.schemas.users import Auth0User

token_auth_scheme = HTTPBearer()


async def check_user(token: str = Depends(token_auth_scheme)):
    return VerifyToken(token.credentials).verify()


def _check_claims(payload, claim_name, claim_type, expected_value):
    instance_check = isinstance(payload[claim_name], claim_type)
    result = {"status": "success", "status_code": 200}

    payload_claim = payload[claim_name]

    if claim_name not in payload or not instance_check:
        result["status"] = "error"
        result["status_code"] = 400

        result["code"] = f"missing_{claim_name}"
        result["msg"] = f"No claim '{claim_name}' found in token."
        return result

    if claim_name == 'scope':
        payload_claim = payload[claim_name].split(' ')

    for value in expected_value:
        if value not in payload_claim:
            result["status"] = "error"
            result["status_code"] = 403

            result["code"] = f"insufficient_{claim_name}"
            result["msg"] = (f"Insufficient {claim_name} ({value}). You "
                             "don't have access to this resource")
            return result
    return result


class VerifyToken:
    def __init__(self, token):
        self.signing_key = None
        self.token = token
        self.permissions = None
        self.scopes = None
        self.jwks_url = f'https://{DOMAIN_AUTH0}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(self.jwks_url)

    def verify(self) -> Auth0User:
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=ISSUER,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
        if self.scopes:
            result = _check_claims(payload, 'scope', str, self.scopes.split(' '))
            if result.get("error"):
                return result

        if self.permissions:
            result = _check_claims(payload, 'permissions', list, self.permissions)
            if result.get("error"):
                return result

        user = Auth0User(**payload)
        user.permissions = payload['scope'].split(' ')
        return user
