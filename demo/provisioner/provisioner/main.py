import logging
from fastapi import FastAPI, Request


app = FastAPI()


@app.get("/")
def read_root(request: Request):
    logging.debug(request)
    client_host = request.client.host
    return {"client_host": client_host}
