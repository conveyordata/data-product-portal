import json
from typing import Any, Dict, Optional
import requests
from agentic_system.settings import settings
from pydantic import BaseModel
from pydantic_ai import Agent, ModelHTTPError, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel

from app.core.auth.auth import JWTToken
from app.utils.singleton import Singleton
from app.users.schema import User


class BaseMessage(BaseModel):
    message: str

class AgenticSystemService(metaclass=Singleton):
    def __init__(self):
        self.ENDPOINT = "http://localhost:5050"
        #model = GeminiModel("gemini-3.0-flash", api_key=settings.GEMINI_API_KEY)
        model = OpenAIModel("o3-mini", api_key=settings.OPEN_AI_API_KEY)
        self.conversation_history = []
        self.openapi_spec = json.loads(self.get_openapi_json()[1])
        self.ama_agent = Agent(
            instrument=True,
            model=model,
            system_prompt=(
                """
You are an advanced and intelligent assistant for the Data Product Portal. Your primary goal is to assist users with complex queries, automate workflows, and perform actions such as approving requests, creating products, and managing datasets. You achieve this by leveraging the API endpoints defined in the `openapi.json` file. Always ensure your responses are accurate, actionable, and based solely on the data retrieved from the API.

### Core Capabilities:
1. **Advanced Query Handling**: Answer complex questions by combining data from multiple API endpoints and applying logical reasoning.
2. **Workflow Automation**: Proactively assist users by automating workflows such as approving requests, creating products, and managing datasets.
3. **Decision-Making**: Provide recommendations or take actions based on the context and available data.
4. **Proactive Assistance**: Anticipate user needs and suggest next steps or additional information to enhance their experience.

### General Guidelines:
1. **Strict API Usage**: Only use the API endpoints defined in the `openapi.json` file. Never make assumptions or provide information that cannot be retrieved from the API.
   - Always refer to the OpenAPI spec to ensure you use all relevant routes for the request.
   - **Endpoint Structure**: All routes start with `/api`.
2. **Authentication**: Use the provided token for authenticated requests. Include the token in the `Authorization` header as a Bearer token for all API calls.
3. **Conciseness and Clarity**: Provide clear, concise, and actionable responses. Use structured formats like tables or lists to enhance readability.
4. **Planning and Execution**: Before executing any API call:
   - Clearly outline your plan.
   - Verify the output of each call to ensure accuracy.
   - Use the results to construct meaningful and actionable responses.
5. **Error Handling**: Handle errors gracefully:
   - If an API call fails, provide a meaningful error message to the user.
   - Include the error code and reason for failure.
   - Suggest corrective actions or alternative approaches if possible.
6. **Context Awareness**: Maintain the context of the conversation:
   - Use previous interactions to provide relevant and coherent responses.
   - Avoid redundant questions by leveraging prior responses.
7. **Security**: Never expose sensitive information such as API keys or tokens in your responses.

### Workflow Examples:
1. **Approving a Request**:
   - **User Query**: "Approve the request for dataset access."
   - **Plan**: Use the `/api/requests` endpoint to fetch pending requests, identify the relevant request, and approve it using the `/api/requests/{uuid}/approve` endpoint.
   - **Execution**: Make authenticated API calls to fetch, verify, and approve the request.
   - **Response**: "The request for dataset access has been approved successfully."

2. **Creating a Data Product**:
   - **User Query**: "Create a new data product for the marketing team."
   - **Plan**: Use the `/api/data_products` endpoint to create a new data product with the provided details.
   - **Execution**: Validate the input parameters, make an authenticated `POST` request, and confirm the creation.
   - **Response**: "The data product 'Marketing Insights' has been created successfully."

3. **Complex Query**:
   - **User Query**: "Show me all datasets linked to the 'Sales Dashboard' data product."
   - **Plan**: Use the `/api/data_products` endpoint to fetch the UUID of the 'Sales Dashboard' product, then use `/api/data_products/{uuid}/datasets` to retrieve the linked datasets.
   - **Execution**: Make authenticated API calls to fetch and verify the data.
   - **Response**: "Here are the datasets linked to 'Sales Dashboard': [list of datasets]."

### Key Points for API Calls:
1. **UUID Handling**: Most API calls require UUIDs. To find the correct UUID:
   - Fetch all items (e.g., via `/datasets` or `/data_products`).
   - Filter the results by name or other attributes to extract the UUID.
   - Use the UUID for subsequent requests (e.g., `/datasets/{uuid}`).
2. **Data Product vs. Data Output**: Understand the distinction:
   - `data_product_links` are the data products that read from a dataset.
   - `data_output_links` are the data outputs that provide input into the dataset.
   - Lineage-wise, datasets depend on data outputs (`data_output_links`), and data products depend on datasets (`data_product_links`).
3. **Validation**: Always validate input parameters against the OpenAPI spec before making API calls. Interact with the user to gather missing details if necessary.

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
   - If you receive a `404`, your reflex should be to search the openapi spec again for a better API call.

### Additional Notes:
- Be proactive in suggesting actions or next steps based on the user's query.
- When unsure about how to proceed, ask for clarification or additional input from the user.
- Always provide actionable insights and recommendations to help users achieve their goals efficiently.
- Be explicit about the results retrieved from the API. Do not omit or obscure any information.

By adhering to these guidelines, you will provide accurate, helpful, and context-aware responses to user queries, automate workflows, and assist with decision-making in the Data Product Portal.
                """
            ),
            result_type=BaseMessage,
        )

        self.ama_agent._register_tool(
            Tool(
                description="Fetches the full openapi spec of the data product portal. Use these requests together with the token to make authenticated requests to the portal to answer questions",
                name="get_openapi_json",
                function=self.get_openapi_json,
            )
        )
        self.ama_agent._register_tool(
            Tool(
                name="call_portal_api",
                takes_ctx=True,
                function=self.call_portal_api,
                description="Execute an arbitrary API call to the portal using the openapi scheme.",
            )
        )
        self.ama_agent._register_tool(
            Tool(
                name="who_am_I",
                takes_ctx=True,
                function=self.who_am_I,
                description="Returns information about the authenticated user.",
            )
        )
        self.ama_agent._register_tool(
            Tool(
                name="get_datasets",
                takes_ctx=True,
                function=self.get_datasets,
                description="Returns a list of datasets available in the portal.",
            )
        )
        self.ama_agent._register_tool(
            Tool(
                name="get_data_products",
                takes_ctx=True,
                function=self.get_data_products,
                description="Returns a list of data products available in the portal.",
            )
        )
        self.ama_agent._register_tool(
            Tool(
                name="get_data_outputs",
                takes_ctx=True,
                function=self.get_data_outputs,
                description="Returns a list of data outputs available in the portal.",
            )
        )
        
        self.approve_agent = Agent(
            instrument=True,
            model=model,
            system_prompt=(
                """
You are an agent that has the responsibility to approve requests in Portal.
Please make sure you inform yourself of all the necessary information. Read the descriptions and about pages of both parties in the approval request.
Then make a recommendation on whether or not the request should be approved or denied.
Provide reasons on why you give the recommendation. Take into account risks and opportunity and the impact on the parties and costs.
If you provide a possitive recommendation, execute the action as well.
If the data is sensitive, make sure to inform the user that the data is sensitive and that they should be careful with it, ask for an explicit recommendation from the user instead of approving on your own.

Check whether the requested dataset read access is in line with the data that is expected to be read from the data product requesting it.
                """
            )
        )

        self.model_router_agent = Agent(
            instrument=True,
            model=model,
            system_prompt=(
                """
You are an agent delegator. You delegate work to the other available agents.
                """
        )
    )
        self.model_router_agent._register_tool(
            Tool(
                name="ask_me_anything",
                takes_ctx=True,
                function=self.ask_me_anything_tool,
                description="Ask the AMA agent any question.",
            )
        )
        self.model_router_agent._register_tool(
            Tool(
                name="approve_me",
                takes_ctx=True,
                function=self.approve_me_tool,
                description="Approve a request.",
            )
        )
    
    def ask_me_anything_tool(self, ctx, question: str, token: JWTToken)-> BaseMessage:
        self.ama_agent.run(question)

    def approve_me_tool(self, ctx)-> BaseMessage:
        self.approve_agent.run()

    async def respond(self, question: str, token: JWTToken) -> BaseMessage:
        self.token = token.token
        try:
            # result = await self.model_router_agent.run(
            #     question, message_history=self.conversation_history
            # )
            result = await self.ama_agent.run(
                question, message_history=self.conversation_history
            )
        except ModelHTTPError:
            self.conversation_history = []
            result = await self.ama_agent.run(
                question, message_history=self.conversation_history
            )
        self.conversation_history.extend(result.new_messages())
        if len(self.conversation_history) > 5:
            self.conversation_history.pop(0)
        return result.data
    
    def call_portal_api(self, ctx: RunContext, endpoint: str, method: str="GET", params=None, body=None):
        """
        Executes an API call to the portal. Caches results to avoid redundant calls.
        """
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
            return response.json()
        else:
            return {"error": response.status_code, "message": response.text}

    def who_am_I(self, ctx) -> User:
        response = self.call_portal_api(ctx, "api/auth/user")
        return response

    def get_openapi_json(self):
        response = requests.get(f"{self.ENDPOINT}/api/openapi.json")
        return response.status_code, response.content

    def get_datasets(self, ctx):
        response = self.call_portal_api(ctx, "api/datasets")
        return response
    
    def get_data_products(self, ctx):
        response = self.call_portal_api(ctx, "api/data_products")
        return response
    
    def get_data_outputs(self, ctx):
        response = self.call_portal_api(ctx, "api/data_outputs")
        return response
    
    