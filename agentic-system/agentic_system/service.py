from agentic_system.settings import settings
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

from app.utils.singleton import Singleton


class BaseMessage(BaseModel):
    message: str


class AgenticSystemService(metaclass=Singleton):
    def __init__(self):
        model = GroqModel(
            "deepseek-r1-distill-llama-70b", api_key=settings.AGENT_API_KEY
        )
        self.agent = Agent(
            model=model,
            system_prompt=(
                "You are supposed to answer queries about the history of "
                "computer science topics. Be concise, reply with one sentence."
            ),
            result_type=BaseMessage,
        )

    async def test(self) -> BaseMessage:
        result = await self.agent.run('Where does "hello world" come from?')
        return result.data
