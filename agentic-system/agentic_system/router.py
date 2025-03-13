from agentic_system.service import AgenticSystemService, BaseMessage
from fastapi import APIRouter, Depends, Security

# from app.core.auth.auth import api_key_authenticated, JWTToken
from app.core.auth.jwt import JWTToken, JWTTokenValid, PyJWTError, oidc
from app.core.config.env_var_parser import get_boolean_variable

# from app.core.auth.auth import api_key_authenticated


def secured_call(token: str = Depends(oidc.oidc_dependency)) -> JWTToken:
    jwt = JWTTokenValid(token)
    if not jwt.is_valid():
        raise PyJWTError()
    return JWTToken(sub=jwt.valid_jwt_token.get("sub"), token=token)


router = (
    APIRouter(dependencies=[Security(secured_call)])
    if get_boolean_variable("OIDC_ENABLED", False)
    else APIRouter()
)
ai_router = APIRouter(prefix="", tags=["AI"])


@router.get("")
async def hello_world() -> BaseMessage:
    return await AgenticSystemService().test()


@router.post("")
async def ask_question(
    question: str, token: JWTToken = Depends(secured_call)
) -> BaseMessage:
    return await AgenticSystemService().respond(question, token)


router.include_router(ai_router)
