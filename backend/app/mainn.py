import json

import boto3

client = boto3.client("bedrock-runtime")


def main():
    model_id = "cohere.embed-english-v3"
    input_text = ["This is a test sentence to generate embeddings."]
    input_type = "search_document"
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps({"texts": input_text, "input_type": input_type}),
    )
    model_response = json.loads(response["body"].read())

    # The embedding vectors are found under the 'embeddings' key
    model_response["embeddings"]

    # Output results


if __name__ == "__main__":
    main()
