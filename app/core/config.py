import pathlib

from starlette.config import Config

ROOT = pathlib.Path(__file__).resolve().parent.parent  # app/
BASE_DIR = ROOT.parent  # ./
API_V1_STR = "/api/v1"
config = Config(BASE_DIR / ".env")

API_USERNAME = config("API_USERNAME", str)
API_PASSWORD = config("API_PASSWORD", str)

# Auth configs.
API_SECRET_KEY = config("API_SECRET_KEY", str)
API_ALGORITHM = config("API_ALGORITHM", str)
API_ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "API_ACCESS_TOKEN_EXPIRE_MINUTES", int
)  # infinity

# auth0 conf
DOMAIN_AUTH0 = config("DOMAIN_AUTH0", str)
API_AUDIENCE = config("API_AUDIENCE", str)
AUTH0_ISSUER = config("AUTH0_ISSUER", str)
AUTH0_ALGORITHMS = config("AUTH0_ALGORITHMS", str)
# ------------------
POSTGRESQL_URI = config("POSTGRESQL_URI", str)
