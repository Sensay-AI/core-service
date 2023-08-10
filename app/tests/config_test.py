# import pytest
from typing import Generator

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import (
    API_AUDIENCE,
    AUTH_TEST_CLIENT_ID,
    AUTH_TEST_CLIENT_SECRET,
    DOMAIN_AUTH0,
    POSTGRESQL_URI,
)
from app.db.database import Base

engine = create_engine(
    POSTGRESQL_URI,
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#
#
# @pytest.fixture(scope="module")
def db_session() -> Generator:
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


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
