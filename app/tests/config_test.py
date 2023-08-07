import requests

from app.core.config import (
    API_AUDIENCE,
    AUTH_TEST_CLIENT_ID,
    AUTH_TEST_CLIENT_SECRET,
    DOMAIN_AUTH0,
)


class MockToken:
    @staticmethod
    def get_token() -> str:
        resp = requests.post(
            f"https://{DOMAIN_AUTH0}/oauth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": AUTH_TEST_CLIENT_ID,
                "client_secret": AUTH_TEST_CLIENT_SECRET,
                "audience": API_AUDIENCE,
            },
        )
        assert resp.status_code == 200
        return resp.json()["access_token"]
