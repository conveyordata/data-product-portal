from agentic_system.service import AgenticSystemService, BaseMessage
from fastapi import APIRouter, Security

from app.core.auth.auth import api_key_authenticated
from app.core.config.env_var_parser import get_boolean_variable

router = (
    APIRouter(dependencies=[Security(api_key_authenticated)])
    if get_boolean_variable("OIDC_ENABLED", False)
    else APIRouter()
)
ai_router = APIRouter(prefix="", tags=["AI"])


@router.get("")
async def hello_world() -> BaseMessage:
    return await AgenticSystemService().test()


@router.post("")
async def ask_question(question: str) -> BaseMessage:
    return await AgenticSystemService().respond(question)


router.include_router(ai_router)
