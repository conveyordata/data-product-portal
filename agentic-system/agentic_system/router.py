from agentic_system.service import AgenticSystemService, BaseMessage
from fastapi import APIRouter

router = APIRouter(prefix="", tags=["AI"])


@router.get("")
async def hello_world() -> BaseMessage:
    return await AgenticSystemService().test()
