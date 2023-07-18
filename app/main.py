from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import API_V1_STR
from app.core import auth
from app.routes import views
from app.routes.api_v1 import api as api_v1

app = FastAPI()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_v1.router, prefix=API_V1_STR)
app.include_router(auth.router)
app.include_router(views.router)
