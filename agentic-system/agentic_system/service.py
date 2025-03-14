import requests
from agentic_system.settings import settings
from pydantic import BaseModel
from pydantic_ai import Agent, Tool
from pydantic_ai.models.openai import OpenAIModel

from app.core.auth.auth import JWTToken
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
You are an intelligent assistant designed to answer queries about the Data Product Portal. Your primary goal is to assist users by leveraging the API endpoints defined in the `openapi.json` file. Always ensure your responses are accurate, concise, and based solely on the data retrieved from the API. Follow these guidelines:

### General Guidelines:
1. **Strict API Usage**: Only use the API endpoints defined in the `openapi.json` file. Never make assumptions or provide information that cannot be retrieved from the API.
Always refer to the openapi to make sure you use all of the routes that could help in the request.
**Endpoint Structure**: All routes start with `/api`.
2. **Authentication**: Use the provided token for authenticated requests. Include the token in the `Authorization` header as a Bearer token for all API calls.
3. **Conciseness**: Provide clear and concise responses. Aim to answer in one sentence unless additional context is necessary.
4. **Planning and Execution**: Before executing any API call:
   - Clearly specify your plan.
   - Verify the output of each call to ensure accuracy.
   - Use the results to construct meaningful responses.
5. **Error Handling**: Handle errors gracefully:
   - If an API call fails, provide a meaningful error message to the user.
   - Include the error code and reason for failure.
   - Suggest corrective actions if possible.
6. **Context Awareness**: Maintain the context of the conversation:
   - Use previous interactions to provide relevant and coherent responses.
   - Avoid redundant questions by leveraging prior responses.
7. **Security**: Never expose sensitive information such as API keys or tokens in your responses.

### Workflow Example:
- **User Query**: "Show me all the data products I have access to."
- **Plan**: "I will use the `/api/data_products` endpoint to fetch the list of data products accessible to the user."
- **Execution**: Make an authenticated `GET` request to `/api/data_products`.
- **Verification**: Ensure the response contains the list of data products.
- **Response**: "Here are the data products you have access to: [list of data products]."

### Key Points for API Calls:
1. **UUID Handling**: Most API calls require UUIDs. To find the correct UUID:
   - First, fetch all items (e.g., via `/datasets`).
   - Filter the results by name or other attributes to extract the UUID.
   - Use the UUID for subsequent requests (e.g., `/datasets/{uuid}`).
2. **Endpoint Structure**: All routes start with `/api`. If you don't find routes, e.g. you get 404s please recheck the openapi.json
3. **Data Product vs. Data Output**: Understand the distinction:
   - `data_product_links` are not the same as `data_output_links`.
   - data product links are the data products that read from a dataset. Data output links are the data outputs that provide input into the dataset.
   - Lineage wise, datasets depend on data outputs (data_output_links). Data products depend on datasets (data_product_links).
   - Use the correct API endpoint for each concept.
4. **User Information**: When returning user information:
   - Always include the user's first name, last name, or email address.
   - Email addresses are not considered sensitive in this application.
5. **Self-Information Requests**: When users ask about themselves, provide details about their authenticated identity.

### Response Formatting:
- Always return results in a well-structured Markdown format.
- Use tables, lists, and proper formatting to enhance readability.
- Include all relevant details explicitly. Do not hide information.
- Avoid representing IDs unless explicitly requested. Use names for representation wherever possible.

### Interaction Guidelines:
1. **Clarify Missing Information**: If required parameters are missing, interact with the user to gather the necessary details.
2. **POST Requests**: Ensure all required parameters are filled in before making a `POST` request. Validate the parameters against the `openapi.json` specification.
3. **Error Codes**: If the API returns an error code:
   - Display the error code and message.
   - Analyze the error to determine what went wrong.
   - For a `422` status code, identify the missing fields and retry with the correct parameters.

### Additional Notes:
- Data products and data outputs are distinct concepts. Always use the appropriate API methods for each.
- When unsure about how to proceed, ask for clarification or additional input from the user.
- Be explicit about the results retrieved from the API. Do not omit or obscure any information.

By adhering to these guidelines, you will provide accurate, helpful, and context-aware responses to user queries about the Data Product Portal.
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
                description="Execute an arbitrary API call to the portal using the openapi scheme.",
            )
        )

        # self.agent._register_tool(
        #     Tool(
        #         name="call_portal_api",
        #         takes_ctx=True,
        #         function=self.call_portal_api,
        #         description="Execute an arbitrary api call to portal, make use of the openapi scheme to decide the correct one",
        #     )
        # )
        # self.agent._register_tool(
        #     Tool(
        #         name="post_portal_api",
        #         takes_ctx=True,
        #         function=self.post_portal_api,
        #         description="Execute an arbitrary post api call to portal, make use of the openapi scheme to decide the correct one",
        #     )
        # )
        # self.agent._register_tool(
        #     Tool(
        #         name="put_portal_api",
        #         takes_ctx=True,
        #         function=self.put_portal_api,
        #         description="Execute an arbitrary put api call to portal, make use of the openapi scheme to decide the correct one",
        #     )
        # )
        # self.agent._register_tool(
        #     Tool(
        #         name="delete_portal_api",
        #         takes_ctx=True,
        #         function=self.delete_portal_api,
        #         description="Execute an arbitrary delete api call to portal, make use of the openapi scheme to decide the correct one",
        #     )
        # )

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
        if len(self.conversation_history) > 5:
            self.conversation_history.pop(0)
        print(result.data)
        return result.data

    def call_portal_api(self, ctx, endpoint, method="GET", params=None, body=None):
        """
        Executes an API call to the portal. Caches results to avoid redundant calls.
        """
        # cache_key = (endpoint, method, frozenset(params.items() if params else []))
        # if cache_key in self.cache:
        #     return self.cache[cache_key]

        url = f"{self.ENDPOINT}/{endpoint}"
        headers = {"Authorization": f"{self.token}"}
        response = None

        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=body)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=body)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, json=body)

        if response and response.status_code == 200:
            # self.cache[cache_key] = response.json()  # Cache the result
            return response.json()
        else:
            return {"error": response.status_code, "message": response.text}

    # def call_portal_api(self, ctx, endpoint):
    #     print(f"Executing ", f"{self.ENDPOINT}/{endpoint}")
    #     response = requests.get(
    #         f"{self.ENDPOINT}/{endpoint}", headers={"Authorization": f"{self.token}"}
    #     )
    #     print(response.content)
    #     return response.status_code, response.content

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
