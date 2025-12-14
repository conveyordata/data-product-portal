import logging
from fastapi import FastAPI, Request


app = FastAPI()


@app.get("/")
def get_root(request: Request):
    logging.debug(request)
    client_host = request.client.host
    return {"client_host": client_host}


@app.post("/")
def post_root(request: Request):
    logging.debug(request)
    client_host = request.client.host
    return {"client_host": client_host}


@app.put("/")
def put_root(request: Request):
    logging.debug(request)
    client_host = request.client.host
    return {"client_host": client_host}


@app.delete("/")
def delete_root(request: Request):
    logging.debug(request)
    client_host = request.client.host
    return {"client_host": client_host}
