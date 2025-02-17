from fastapi import APIRouter

router = APIRouter(prefix="", tags=["AI"])


@router.get("")
def hello_world():
    return {"message": "Hello World"}
