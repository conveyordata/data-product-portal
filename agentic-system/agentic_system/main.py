from agentic_system.router import router
from fastapi import FastAPI

with open("./VERSION", "r") as f:
    API_VERSION = f.read().strip()

TITLE = "Data product portal Agentic System"

app = FastAPI(
    title=TITLE,
    summary="Agentic System implementation for Data product portal",
    version=API_VERSION,
    contact={"name": "Stijn Janssens", "email": "stijn.janssens@dataminded.com"},
    docs_url="/ai/api/docs",
    openapi_url="/ai/api/openapi.json",
)

app.include_router(router, prefix="/ai/api")


# K8S health and liveness check
@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/ai/api/version")
def get_version():
    return {"version": app.version}
