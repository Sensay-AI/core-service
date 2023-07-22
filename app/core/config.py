import pathlib

from starlette.config import Config

ROOT = pathlib.Path(__file__).resolve().parent.parent  # app/
BASE_DIR = ROOT.parent  # ./

config = Config(BASE_DIR / ".env")

API_USERNAME = config("API_USERNAME", str)
API_PASSWORD = config("API_PASSWORD", str)

# Auth configs.
API_SECRET_KEY = config("API_SECRET_KEY", str)
API_ALGORITHM = config("API_ALGORITHM", str)
API_ACCESS_TOKEN_EXPIRE_MINUTES = config("API_ACCESS_TOKEN_EXPIRE_MINUTES", int)  # infinity

# auth0 conf
DOMAIN_AUTH0 = ""
API_AUDIENCE = ""
ISSUER = ""
ALGORITHMS = "RS256"
# ------------------
DATABASE_URL = "postgresql://lie.temp2000:TxBrP8VCe6un@ep-lucky-bar-509389-pooler.us-east-2.aws.neon.tech/neondb"
API_V1_STR = "/api/v1"
