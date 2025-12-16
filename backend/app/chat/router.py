from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.aws.boto3_clients import get_client
from app.database.database import get_db_session
from app.datasets.router import search_datasets_embeddings
from app.datasets.schema_response import DatasetsGet


class ChatResponse(BaseModel):
    response: str
    search_result: Sequence[DatasetsGet]
    thoughts: list[str]


router = APIRouter(prefix="/chat", tags=["Chat"])

tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "output_port_search",
                "description": "Search the Data product portal for output ports the users can use",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query",
                            }
                        },
                        "required": ["query"],
                    }
                },
            }
        }
    ]
}


class Message(BaseModel):
    role: str
    text: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[Message]


system_prompt = [
    {
        "text": (
            "You are a helpful assistant for the Data Product Portal. "
            "If a tool returns search results, strictly answer with: "
            "'Here are the datasets I found related to your query:' "
            "Do not invent details you cannot see."
        )
    }
]


@router.post("")
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db_session),
) -> ChatResponse:
    client = get_client("bedrock-runtime")
    bedrock_messages = []
    for msg in request.messages:
        if msg.text:  # Only include text messages to keep it simple for POC
            bedrock_messages.append({"role": msg.role, "content": [{"text": msg.text}]})

    search_result: list[DatasetsGet] = []
    thought_process: list[str] = []

    while True:
        response = client.converse(
            modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            messages=bedrock_messages,
            toolConfig=tool_config,
            system=system_prompt,
        )

        output_message = response["output"]["message"]
        stop_reason = response["stopReason"]

        # Add AI response to our temporary history
        bedrock_messages.append(output_message)

        if stop_reason == "tool_use":
            tool_requests = output_message["content"]
            tool_results_content = []

            for item in tool_requests:
                if "toolUse" in item:
                    t_use = item["toolUse"]
                    if t_use["name"] == "output_port_search":
                        search_data = search_datasets_embeddings(
                            t_use["input"]["query"], db
                        )
                        thought_process.append(
                            f"Searching output ports for: '{t_use['input']['query']}'"
                        )
                        for ds in search_data:
                            search_result.append(ds)

                        tool_results_content.append(
                            {
                                "toolResult": {
                                    "toolUseId": t_use["toolUseId"],
                                    "content": [
                                        {
                                            "json": {
                                                "results": [
                                                    DatasetsGet.model_validate(
                                                        ds
                                                    ).model_dump_json()
                                                    for ds in search_data
                                                ]
                                            }
                                        }
                                    ],
                                }
                            }
                        )

            bedrock_messages.append({"role": "user", "content": tool_results_content})
        else:
            # We are done
            return ChatResponse(
                response=output_message["content"][0]["text"],
                search_result=search_result,
                thoughts=thought_process,
            )
