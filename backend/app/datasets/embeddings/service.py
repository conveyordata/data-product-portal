import json
from typing import Sequence
from uuid import UUID

import boto3
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.datasets.embeddings.model import DatasetEmbedding
from app.datasets.schema_response import DatasetEmbed

model_id = "cohere.embed-english-v3"
max_distance = 0.4


class DatasetEmbeddingsService:
    def __init__(self, db: Session):
        self.db = db

    def insert_embeddings_for_datasets(self, datasets: Sequence[DatasetEmbed]):
        client = boto3.client("bedrock-runtime")

        input_text = [ds.model_dump_json(exclude={"id"}) for ds in datasets]
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({"texts": input_text, "input_type": "search_document"}),
        )
        model_response = json.loads(response["body"].read())
        for idx, embedding in enumerate(model_response["embeddings"]):
            self.db.add(DatasetEmbedding(id=datasets[idx].id, embeddings=embedding))
        self.db.commit()

    def search(self, query: str) -> Sequence[UUID]:
        client = boto3.client("bedrock-runtime")
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({"texts": [query], "input_type": "search_document"}),
        )
        query_vec = json.loads(response["body"].read())["embeddings"][0]
        distance = DatasetEmbedding.embeddings.cosine_distance(query_vec)
        stmt = select(DatasetEmbedding.id).order_by(distance).limit(10)
        return self.db.scalars(stmt).unique().all()
