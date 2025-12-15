import boto3

client = boto3.client("bedrock-runtime")


def main():
    model = "anthropic.claude-3-haiku-20240307-v1:0"
    client.converse(
        modelId=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": "Give me a good name for a puppy!"},
                ],
            },
        ],
        # system=[
        #     {
        #         'text': 'string',
        #         'guardContent': {
        #             'text': {
        #                 'text': 'string',
        #                 'qualifiers': [
        #                     'grounding_source' | 'query' | 'guard_content',
        #                 ]
        #             },
        #             'image': {
        #                 'format': 'png' | 'jpeg',
        #                 'source': {
        #                     'bytes': b'bytes'
        #                 }
        #             }
        #         },
        #         'cachePoint': {
        #             'type': 'default'
        #         }
        #     },
        # ],
        # inferenceConfig={
        #     'maxTokens': 123,
        #     'temperature': ...,
        #     'topP': ...,
        #     'stopSequences': [
        #         'string',
        #     ]
        # },
        #     toolConfig={
        #         'tools': [
        #             {
        #                 'toolSpec': {
        #                     'name': 'string',
        #                     'description': 'string',
        #                     'inputSchema': {
        #                         'json': {...} | [...] | 123 | 123.4 | 'string' | True | None
        #                     }
        #                 },
        #                 'systemTool': {
        #                     'name': 'string'
        #                 },
        #                 'cachePoint': {
        #                     'type': 'default'
        #                 }
        #             },
        #         ],
        #         'toolChoice': {
        #             'auto': {}
        #             ,
        #             'any': {}
        #             ,
        #             'tool': {
        #                 'name': 'string'
        #             }
        #         }
        #     },
        #     guardrailConfig={
        #         'guardrailIdentifier': 'string',
        #         'guardrailVersion': 'string',
        #         'trace': 'enabled' | 'disabled' | 'enabled_full'
        #     },
        #     additionalModelRequestFields={...} | [...] | 123 | 123.4 | 'string' | True | None,
        #     promptVariables={
        #         'string': {
        #             'text': 'string'
        #         }
        #     },
        #     additionalModelResponseFieldPaths=[
        #         'string',
        #     ],
        #     requestMetadata={
        #         'string': 'string'
        #     },
        #     performanceConfig={
        #         'latency': 'standard' | 'optimized'
        #     },
        #     serviceTier={
        #         'type': 'priority' | 'default' | 'flex' | 'reserved'
        #     }
    )


if __name__ == "__main__":
    main()
