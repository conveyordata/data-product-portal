import contextlib
from uuid import UUID

import requests
from agentic_system.settings import settings
from pydantic import BaseModel
from pydantic_ai import Agent, Tool
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.openai import OpenAIModel
from requests import Response

from app.core.auth.auth import JWTToken, get_authenticated_user
from app.data_products.schema import DataProduct
from app.data_products.service import DataProductService
from app.database.database import get_db_session
from app.users.schema import User
from app.utils.singleton import Singleton


class BaseMessage(BaseModel):
    message: str


class AgenticSystemService(metaclass=Singleton):
    def __init__(self):
        self.ENDPOINT = "http://localhost:5050"

        model = OpenAIModel("o3-mini", api_key=settings.OPEN_AI_API_KEY)
        self.conversation_history = []
        self.agent = Agent(
            instrument=True,
            model=model,
            system_prompt=(
                """
                You are an intelligent assistant designed to answer queries about the data product portal. You have access to the full API specification in the openapi.json file. Use these API endpoints to fetch data and provide accurate responses to user queries. Follow these guidelines:
                If you are planning to use the portal API first always retrieve the openapi spec.
                Never use API calls that are not defined in the openAPI spec.
                Also make sure that the parameters for POST actually exist and that all required parameters are filled in.
                Also POST calls need to be fetched from the openapi spec.

                1. **API Usage**: Always use the API endpoints defined in the openapi.json file to fetch data. Do not make assumptions or provide information that cannot be retrieved from the API.
                2. **Authentication**: Use the provided token for authenticated requests. Include the token in the Authorization header as a Bearer token.
                3. **Conciseness**: Provide concise and accurate responses. Aim to answer in one sentence unless additional context is necessary.
                4. **Planning and Execution**: Clearly specify your plan before executing any API call. Verify the output of each call to ensure accuracy.
                5. **Error Handling**: Handle errors gracefully. If an API call fails, provide a meaningful error message to the user.
                6. **Context Awareness**: Maintain context of the conversation. Use previous interactions to provide relevant and coherent responses.
                7. **Security**: Do not expose sensitive information such as API keys or tokens in the responses.

                Example Workflow:
                - User Query: "Show me all the data products I have access to."
                - Plan: "I will use the /data_products endpoint to fetch the list of data products accessible to the user."
                - Execution: Make an authenticated GET request to /data_products.
                - Verification: Ensure the response contains the list of data products.
                - Response: "Here are the data products you have access to: [list of data products]."

                Remember, your primary goal is to assist users by leveraging the API endpoints available in the openapi.json file. Always verify your output and provide clear, concise, and accurate responses.

                Key points to remember when calling the api:
                - most calls work with UUIDs. To find the right one, first fetch all of the items e.g. through /datasets, then filter for the name or other attribute you are looking for to extract the UUID and then make the individual request with /datasets/{uuid}
                If you need more information, often you will find it by calling the individual endpoints with /{id}
                - all routes start with /api
                - data_product_links are not the same as data_output_links.

                Do note that data products and data outputs are two different concepts.
                Make sure you use the correct API endpoint methods for the separate calls.

                The end result should be a nicely formatted Markdown table of the data. Include new lines and other proper formatting.

                Be more explicit about the result you get from the Data Product Portal api
                Don't hide any information.
                Never represent IDs unless explicitly asked for. Always use the names for representation.

                Interact with the user to fetch missing information.
                Make sure you fill in the correct information and required parameters when making a POST call.

                When unsure what to do, please respond back so we can help.
                Ask for more input when needed.
                If the API returns error codes, please show them and try to reason what went wrong.

                If you get a 422 status code, please read the error message to identify which fields are missing and try again.
                """
            ),
            result_type=BaseMessage,
        )

        # self.agent._register_tool(Tool(name="get_data_products", function=self.get_data_products))
        self.agent._register_tool(
            Tool(
                description="Fetches the full openapi spec of the data product portal. Use these requests together with the token to make authenticated requests to the portal to answer questions",
                name="get_openapi_json",
                function=self.get_openapi_json,
            )
        )
        self.agent._register_tool(
            Tool(
                name="call_portal_api",
                takes_ctx=True,
                function=self.call_portal_api,
                description="Execute an arbitrary api call to portal, make use of the openapi scheme to decide the correct one",
            )
        )
        self.agent._register_tool(
            Tool(
                name="post_portal_api",
                takes_ctx=True,
                function=self.post_portal_api,
                description="Execute an arbitrary post api call to portal, make use of the openapi scheme to decide the correct one",
            )
        )
        self.agent._register_tool(
            Tool(
                name="put_portal_api",
                takes_ctx=True,
                function=self.put_portal_api,
                description="Execute an arbitrary put api call to portal, make use of the openapi scheme to decide the correct one",
            )
        )
        self.agent._register_tool(
            Tool(
                name="delete_portal_api",
                takes_ctx=True,
                function=self.delete_portal_api,
                description="Execute an arbitrary delete api call to portal, make use of the openapi scheme to decide the correct one",
            )
        )

    async def test(self) -> BaseMessage:
        result = await self.agent.run('Where does "hello world" come from?')
        return result.data

    async def respond(self, question: str, token: JWTToken) -> BaseMessage:
        print(token)
        self.token = token.token
        # self.conversation_history.append({"question": question, "token": token})
        result = await self.agent.run(
            question, message_history=self.conversation_history
        )
        self.conversation_history.extend(result.new_messages())
        print(result.data)
        return result.data

    def call_portal_api(self, ctx, endpoint):
        print(f"Executing ", f"{self.ENDPOINT}/{endpoint}")
        response = requests.get(
            f"{self.ENDPOINT}/{endpoint}", headers={"Authorization": f"{self.token}"}
        )
        print(response.content)
        return response.status_code, response.content

    def post_portal_api(self, ctx, endpoint, param):
        response = requests.post(
            f"{self.ENDPOINT}/{endpoint}",
            headers={"Authorization": f"{self.token}"},
            json=param,
        )
        return response.status_code, response.content
        # return response.content

    def put_portal_api(self, ctx, endpoint, param):
        response = requests.put(
            f"{self.ENDPOINT}/{endpoint}",
            headers={"Authorization": f"{self.token}"},
            json=param,
        )
        return response.status_code, response.content
        # return response.content

    def delete_portal_api(self, ctx, endpoint, param):
        response = requests.delete(
            f"{self.ENDPOINT}/{endpoint}",
            headers={"Authorization": f"{self.token}"},
            json=param,
        )
        return response.status_code, response.content
        # return response.content

    def get_openapi_json(self):
        response = requests.get(f"{self.ENDPOINT}/api/openapi.json")
        return response.status_code, response.content
