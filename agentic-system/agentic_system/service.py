from pydantic import BaseModel
from pydantic_ai import Agent

from app.utils.singleton import Singleton


class BaseMessage(BaseModel):
    message: str


class AgenticSystemService(metaclass=Singleton):
    def __init__(self):
        self.agent = Agent(
            "google-gla:gemini-2.0-flash",
            system_prompt=(
                "You are supposed to answer queries about the history of "
                "computer science topics. Be concise, reply with one sentence."
            ),
            result_type=BaseMessage,
        )

    async def test(self) -> BaseMessage:
        result = await self.agent.run('Where does "hello world" come from?')
        return result.data
