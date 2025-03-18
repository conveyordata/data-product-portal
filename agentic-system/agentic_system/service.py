import json

import requests
from agentic_system.settings import settings
from pydantic import BaseModel
from pydantic_ai import Agent, ModelHTTPError, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel

from app.core.auth.auth import JWTToken
from app.users.schema import User
from app.utils.singleton import Singleton

# I want to create a data product to calculate promo effectiveness. Please give me all the relevant datasets
# Create a data product called promo effectiveness. Please request access to all of the relevant datasets
# Please create requests for all datasets except the employee data for the data product promo effectiveness.
# Can you please approve all of the pending requests for read access on the promo effectiveness product

MESSAGE_HISTORY_LENGTH = 7


class BaseMessage(BaseModel):
    message: str


class AgenticSystemService(metaclass=Singleton):
    def __init__(self):
        self.ENDPOINT = "http://localhost:5050"
        # model = GeminiModel("gemini-3.0-flash", api_key=settings.GEMINI_API_KEY)
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
2. **Workflow Automation**: Automate workflows such as approving requests, creating products, and managing datasets to save users time and effort.
3. **Decision-Making**: Provide well-reasoned recommendations or take actions based on the context and available data.
4. **Proactive Assistance**: Anticipate user needs, suggest next steps, and provide additional information to enhance their experience.

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
   - If you receive a `404`, recheck the OpenAPI spec for a better API call.
4. **Entity Creation**: When creating new entities that link to certain IDs:
   - Examples of this include domain IDs, type IDs, lifecycle IDs. You should query the API to get these IDs from other similar entities.
   - Prefer reusing IDs from existing entities.
   - If IDs cannot be inferred, explicitly ask the user for clarification.

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
                description="Execute an arbitrary API call to the portal using the openapi scheme. Remember that api routes start with /api. For the correct routes look at the openapi spec.",
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
        self.ama_agent._register_tool(
            Tool(
                name="get_dataset_link",
                takes_ctx=True,
                function=self.get_dataset_links,
                description="Get all requests for dataset access.",
            )
        )

        self.approve_agent = Agent(
            instrument=True,
            model=model,
            system_prompt=(
                """
You are an intelligent and responsible agent tasked with approving requests in the Data Product Portal. Your primary goal is to make informed, well-reasoned decisions about whether to approve or deny requests. You must ensure that all actions align with the portal's policies, minimize risks, and maximize opportunities for all parties involved.

Created requests can still need an approval if the dataset is not public.
To approve a requests you have to find the request_id and call the endpoint
/api/data_product_dataset_links/approve/{request_id}
Make sure that you are using the correct dataset and data product ids to approve the correct request.

### Responsibilities:
1. **Information Gathering**: Before making a decision, gather all necessary information:
   - Read the descriptions and about pages of both the requesting and providing parties.
   - Analyze the context, purpose, and potential impact of the request.
2. **Recommendation**: Provide a clear recommendation to approve or deny the request:
   - Base your recommendation on risks, opportunities, and the impact on all parties.
   - Consider costs, data sensitivity, and alignment with the portal's policies.
   - Always provide reasons for your recommendation.
3. **Execution**: If you recommend approval:
   - Execute the approval action automatically.
   - Inform the user of the action taken and its implications.
4. **Sensitive Data Handling**: If the data involved is sensitive:
   - Inform the user about the sensitivity of the data.
   - Request explicit confirmation from the user before proceeding with approval.
   - Avoid approving sensitive requests automatically.

### Guidelines for Approval:
1. **Dataset Access Validation**:
   - Ensure that the requested dataset read access aligns with the data expected to be read by the requesting data product.
   - If there is a mismatch, deny the request and provide a clear explanation.
2. **API Usage**:
   - Use the `/api/data_products/{id}/dataset/{dataset_id}` endpoint to create requests.
   - Always authenticate requests using the provided token in the `Authorization` header as a Bearer token.
3. **Risk and Opportunity Assessment**:
   - Evaluate the potential risks and benefits of approving the request.
   - Consider the impact on both the requesting and providing parties.
   - Take into account the costs and potential consequences of the decision.

### Interaction Guidelines:
1. **Propose and Explain**:
   - Clearly explain your reasoning for the recommendation.
   - Provide actionable insights to help the user make an informed decision.
2. **User Confirmation**:
   - For sensitive or high-impact decisions, request explicit confirmation from the user before proceeding.
   - Ensure the user understands the implications of their decision.
3. **Error Handling**:
   - If an API call fails, provide a meaningful error message with the error code and reason.
   - Suggest corrective actions or alternative approaches if possible.

### Workflow Example:
1. **User Query**: "Approve the request for dataset access."
2. **Plan**:
   - Fetch the pending requests using the `/api/requests` endpoint.
   - Retrieve detailed information about the requesting and providing parties.
   - Validate the dataset access request against the expected data usage.
   - Assess risks, opportunities, and impact.
3. **Execution**:
   - If the request involves sensitive data, inform the user and request explicit confirmation before proceeding.
4. **Response**:
   - "The request for dataset access has been approved successfully. Please note that the data is sensitive, and appropriate precautions should be taken."

### Additional Notes:
- Be proactive in identifying potential issues or opportunities related to the request.
- Always provide clear, actionable, and well-reasoned responses.
- Ensure that all actions are logged and traceable for accountability.
- Never expose sensitive information such as API keys or tokens in your responses.

If you require IDs, fetch them using the call_portal_api tool.

By adhering to these guidelines, you will ensure that all approval decisions are responsible, transparent, and aligned with the portal's policies.
                """
            ),
        )
        self.approve_agent._register_tool(
            Tool(
                name="call_portal_api",
                takes_ctx=True,
                function=self.call_portal_api,
                description="Execute an arbitrary API call to the portal using the openapi scheme.",
            )
        )
        self.approve_agent._register_tool(
            Tool(
                name="request_dataset_link",
                takes_ctx=True,
                function=self.request_dataset_link,
                description="Request access to a dataset for a data product.",
            )
        )
        # self.approve_agent._register_tool(
        #     Tool(
        #       name="approve_dataset_link",
        #         takes_ctx=True,
        #         function=self.approve_dataset_link,
        #         description="Approve the requested dataset access",
        # )
        # )
        self.approve_agent._register_tool(
            Tool(
                name="get_dataset_links",
                takes_ctx=True,
                function=self.get_dataset_links,
                description="Returns a list of dataset links, both pending and accepted requests, available in the portal.",
            )
        )

        self.approve_agent._register_tool(
            Tool(
                name="get_datasets",
                takes_ctx=True,
                function=self.get_datasets,
                description="Returns a list of datasets available in the portal.",
            )
        )
        self.approve_agent._register_tool(
            Tool(
                name="get_data_products",
                takes_ctx=True,
                function=self.get_data_products,
                description="Returns a list of data products available in the portal.",
            )
        )

        self.model_router_agent = Agent(
            instrument=True,
            model=model,
            system_prompt=(
                """
You are Bifrost, an intelligent agent delegator responsible for coordinating tasks between other specialized agents in the Data Product Portal. Your primary role is to delegate work to the appropriate agents while ensuring that all actions and responses adhere to the portal's policies and guidelines.
For detailed information make sure to request the individual api calls.
E.g. Get general information on data products at /api/data_products, but get detailed info on /api/data_products/{id}
### Core Responsibilities:
1. **Delegation**: Delegate tasks to the appropriate agents:
   - Use the AMA bot to query the portal for information or to retrieve data.
   - Use the Approve Me bot to approve requests or generate new requests.
2. **Scope Limitation**: Only answer questions or perform actions related to the Data Product Portal. Do not handle unrelated queries.

### General Guidelines:
1. **Strict Portal Interaction**:
   - All questions must involve retrieving information from the portal.
   - All actions must result in explicit API calls to the portal, leading to changes in the underlying data.
   - Never claim to have performed an action without actually executing the required API calls.

2. **Ownership and Context**:
   - When creating new entities (e.g., data products, requests), always assign ownership to the current authenticated user.
   - Use the current user's information (e.g., name, email) as the owner or creator of the entity.

3. **Change Execution**:
   - For actions that modify the portal (e.g., POST, PUT, DELETE requests), always propose a detailed plan before execution.
   - Include the following in your plan:
     - The purpose of the change.
     - The API endpoints to be called.
     - The HTTP methods to be used.
     - Any required parameters or payloads.
   - Request explicit approval from the user before proceeding with the plan.

4. **Information Completeness**:
   - Provide all necessary details to help the user make an informed decision.
   - Ensure that your responses are clear, concise, and actionable.

### Workflow Examples:
1. **Querying Information**:
   - **User Query**: "What datasets are available in the portal?"
   - **Delegation**: Use the AMA bot to query the `/api/datasets` endpoint.
   - **Response**: "Here is the list of datasets available in the portal: [list of datasets]."

2. **Approving a Request**:
   - **User Query**: "Approve the request for dataset access."
   - **Delegation**: Use the Approve Me bot to fetch pending requests and approve the relevant one.
   - **Response**: "The request for dataset access has been approved successfully."

3. **Creating a Data Product**:
   - **User Query**: "Create a new data product for the marketing team."
   - **Plan**:
     - Use the `/api/data_products` endpoint to create the data product.
     - Assign the current user as the owner.
     - Request access to the required datasets using the `/api/data_products/{id}/dataset/{dataset_id}` endpoint.
   - **Execution**: After user approval, execute the API calls to create the data product and request dataset access.
   - **Response**: "The data product 'Marketing Insights' has been created successfully, and access to the required datasets has been requested."

### Interaction Guidelines:
1. **Clarify Missing Information**:
   - If required details are missing, interact with the user to gather the necessary information.
   - Avoid making assumptions about user intent or missing parameters.

2. **Error Handling**:
   - If an API call fails, provide a meaningful error message with the error code and reason.
   - Suggest corrective actions or alternative approaches if possible.

3. **Proactive Assistance**:
   - Anticipate user needs and suggest next steps or additional actions to enhance their experience.
   - Be explicit about the results retrieved from the portal. Do not omit or obscure any information.

4. **Individual details**:
    - Most requests will require to look at an individual entity level. First fetch the UUID, then execute the api call with /{id} to get the detailed info.

### Additional Notes:
- Always ensure that actions and responses are traceable and align with the portal's policies.
- Be transparent about the steps you take and the reasoning behind your decisions.
- Never expose sensitive information such as API keys or tokens in your responses.

By adhering to these guidelines, you will ensure that all tasks are delegated effectively, actions are executed responsibly, and users receive accurate and actionable responses.
After explicit approvals of the plan, make sure you actually execute the calls.
If you need to create things, make sure you actually execute POST, PUT or DELETES.

Always look at the openapi spec to fetch the correct endpoints to execute your requests.
                """
            ),
        )
        self.model_router_agent._register_tool(
            Tool(
                name="ask_me_anything",
                takes_ctx=True,
                function=self.ask_me_anything_tool,
                description="Ask the AMA agent any question. The AMA agent can execute arbitrary calls to the portal. Including creation or change requests with POST, PUTs and DELETEs",
            )
        )
        self.model_router_agent._register_tool(
            Tool(
                name="approve_me",
                takes_ctx=True,
                function=self.approve_me_tool,
                description="Approve or create requests for access to datasets. Reason about why a request should or should not be approved automatically.",
            )
        )
        self.model_router_agent._register_tool(
            Tool(
                description="Fetches the full openapi spec of the data product portal. Use these requests together with the token to make authenticated requests to the portal to answer questions",
                name="get_openapi_json",
                function=self.get_openapi_json,
            )
        )

    async def ask_me_anything_tool(
        self, ctx: RunContext, question: str, token: JWTToken
    ) -> BaseMessage:
        print(question)
        result = await self.ama_agent.run(question)
        print(result.data)
        return result.data

    async def approve_me_tool(self, ctx, question: str) -> BaseMessage:
        result = await self.approve_agent.run(question)
        return result.data

    async def respond(self, question: str, token: JWTToken) -> BaseMessage:
        self.token = token.token
        try:
            result = await self.model_router_agent.run(
                question, message_history=self.conversation_history
            )
            # result = await self.ama_agent.run(
            #     question, message_history=self.conversation_history
            # )
        except ModelHTTPError:
            self.conversation_history = []
            result = await self.model_router_agent.run(
                question, message_history=self.conversation_history
            )
        self.conversation_history.extend(result.new_messages())
        if len(self.conversation_history) > MESSAGE_HISTORY_LENGTH:
            self.conversation_history.pop(0)
        print("router response", result.data)
        return BaseMessage(message=result.data)

    def call_portal_api(
        self,
        ctx: RunContext,
        endpoint: str,
        method: str = "GET",
        params=None,
        body=None,
    ):
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
        else:
            return {"error": "Invalid method"}

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

    def request_dataset_link(self, ctx, dataset_id: str, data_product_id: str):
        response = self.call_portal_api(
            ctx,
            f"api/data_products/{data_product_id}/dataset/{dataset_id}",
            method="POST",
        )
        return response

    def get_dataset_links(self, ctx):
        response = self.call_portal_api(ctx, f"api/data_product_dataset_links")
        return response

    # async def approve_dataset_link(self, ctx, data_product_name: str, dataset_name: str):
    #     result = await self.approve_agent.run(f"Please approve the request by fetching all the data_product_dataset_links, then find the request for dataset {dataset_name} data_product{data_product_name}, then call api/data_product_dataset_links/approve/request_id")
    #     return result.data
    #     # headers = {"Authorization": f"{self.token}"}
    #     # datasets = requests.get(f"{self.ENDPOINT}/api/datasets", headers=headers)
    #     # for dataset in datasets.json():
    #     #     if dataset["name"] == dataset_name:
    #     #         dataset_id = dataset["id"]

    #     # # dataset_id = await self.ama_agent.run(f"Please give me the dataset id corresponding with the name {dataset_name}")
    #     # # dataset_id = dataset_id.data.message
    #     # data_products = requests.get(f"{self.ENDPOINT}/api/data_products", headers=headers)
    #     # for data_product in data_products.json():
    #     #     if data_product["name"] == data_product_name:
    #     #         data_product_id = data_product["id"]

    #     # # dataproduct_id = await self.ama_agent.run(f"Please give me the dataproduct id corresponding with the name {data_product_name}")
    #     # # dataproduct_id = dataproduct_id.data.message
    #     # request_id = await self.ama_agent.run(f"Please give me the request id corresponding with the dataset {dataset_id} and data product {data_product_id}")
    #     # request_id = request_id.data.message
    #     # response = self.get_datasets(ctx)
    #     # response = self.call_portal_api(ctx, f"api/data_product_dataset_links/approve/{request_id}", method="POST")
    #     # return response
