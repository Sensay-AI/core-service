from fastapi import FastAPI, Response, Request
from starlette.middleware.cors import CORSMiddleware

from app.container.containers import Container
from app.routes.api_v1 import api as api_v1

API_V1_STR = "/api/v1"


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # you probably want some kind of logging here
        print(e)
        return Response("Internal server error", status_code=500)


def create_app() -> FastAPI:
    container = Container()
    db = container.db()
    container.auth()
    db.create_database()
    container.init_resources()

    fast_api_app = FastAPI()
    fast_api_app.container = container
    fast_api_app.include_router(api_v1.router, prefix=API_V1_STR)
    # Set all CORS enabled origins
    fast_api_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_api_app.middleware('http')(catch_exceptions_middleware)

    return fast_api_app


app = create_app()
