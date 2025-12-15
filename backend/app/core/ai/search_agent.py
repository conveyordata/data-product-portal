import json

from app.core.aws.boto3_clients import get_client
from app.datasets.schema_response import DatasetEmbedReturn
from app.utils.singleton import Singleton


class SearchAgent(metaclass=Singleton):
    def __init__(self):
        self.client = get_client("bedrock-runtime")
        self.model = "anthropic.claude-3-haiku-20240307-v1:0"
        self.tool_list = [
            {
                "toolSpec": {
                    "name": "search_dataset",
                    "description": "Output the structured data about datasets. You MUST provide the datasets array containing objects with the dataset information as defined in the DatasetEmbedReturn schema. Include a rank and reason for every returned result, based on the relevance.",
                    "inputSchema": {"json": DatasetEmbedReturn.model_json_schema()},
                }
            }
        ]

    def converse(self, message: str) -> str:
        response = self.client.converse(
            modelId=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"text": message},
                    ],
                },
            ],
            #     toolConfig={
            #     "tools": self.tool_list,
            #     "toolChoice": {
            #         "tool": {
            #             "name": "search_dataset"
            #         }
            #     },
            # },
        )
        # Tools do not work as intended.

        if response.get("stopReason") == "tool_use":
            content_blocks = response["output"]["message"]["content"]
            tool_use = next(
                block["toolUse"] for block in content_blocks if "toolUse" in block
            )
            structured_output = tool_use["input"]
            return json.dumps(structured_output["datasets"], indent=2)
        else:
            return response["output"]["message"]["content"][0]["text"]
