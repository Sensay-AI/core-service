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

# aws conf
S3_IMAGE_BUCKET = config("S3_IMAGE_BUCKET", str, default='sensayai-images')
AWS_ACCESS_KEY = config("AWS_ACCESS_KEY", str)
AWS_SECRET_KEY = config("AWS_SECRET_KEY", str)
AWS_REGION = config("AWS_REGION", str)


# Testing--------------
AUTH_TEST_CLIENT_ID = "gJXFX5OnAeozyav7iwYtd5MFGV59YZ5T"
AUTH_TEST_CLIENT_SECRET = (
    "U51UoRGWPnBHOtL2LCdlGG9PDwFa8jiSQ1DmBZDqvItIuJrZK7KOzMVgKkmepsSl"
)
