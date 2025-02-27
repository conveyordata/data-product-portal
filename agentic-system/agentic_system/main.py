import logfire
from agentic_system.router import router
from agentic_system.settings import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.auth.jwt import oidc

logfire.configure()
logfire.instrument_asyncpg()

with open("./VERSION", "r") as f:
    API_VERSION = f.read().strip()

TITLE = "Data product portal Agentic System"


oidc_kwargs = (
    {
        "swagger_ui_init_oauth": {
            "clientId": oidc.client_id,
            "appName": TITLE,
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": "openid email profile",
        },
        "swagger_ui_oauth2_redirect_url": "/",
    }
    if settings.OIDC_ENABLED
    else {}
)

app = FastAPI(
    title=TITLE,
    summary="Agentic System implementation for Data product portal",
    version=API_VERSION,
    contact={"name": "Stijn Janssens", "email": "stijn.janssens@dataminded.com"},
    docs_url="/ai/api/docs",
    openapi_url="/ai/api/openapi.json",
    **oidc_kwargs
)

app.include_router(router, prefix="/ai/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# K8S health and liveness check
@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/ai/api/version")
def get_version():
    return {"version": app.version}
