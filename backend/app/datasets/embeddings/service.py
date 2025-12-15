import json
from typing import Sequence

import boto3
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.datasets.embeddings.model import DatasetEmbedding
from app.datasets.schema_response import DatasetEmbed, DatasetEmbeddingResult

# model_id = "cohere.embed-english-v3"
model_id = "cohere.embed-v4:0"


class DatasetEmbeddingsService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def generate_embeddings(texts: list[str]) -> list[list[float]]:
        client = boto3.client("bedrock-runtime")
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({"texts": texts, "input_type": "search_document"}),
        )
        model_response = json.loads(response["body"].read())
        return model_response["embeddings"]["float"]
        # return model_response["embeddings"]
        # return DatasetEmbed(id=dataset_id)

    def insert_embeddings_for_datasets(self, datasets: Sequence[DatasetEmbed]):
        embeddings = self.generate_embeddings(
            [ds.model_dump_json(exclude={"id"}) for ds in datasets]
        )
        for idx, embedding in enumerate(embeddings):
            self.db.add(DatasetEmbedding(id=datasets[idx].id, embeddings=embedding))
        self.db.commit()

    def search(
        self, query: str, sensitivity: float = 0.04, max_distance: float = 0.75
    ) -> Sequence[DatasetEmbeddingResult]:
        embeddings = self.generate_embeddings([query])
        distance = DatasetEmbedding.embeddings.cosine_distance(embeddings[0])
        stmt = (
            select(DatasetEmbedding.id, distance.label("distance"))
            .where(distance <= max_distance)
            .order_by(distance)
            .limit(30)
        )
        results = self.db.execute(stmt).all()

        # 2. Handle edge cases (empty or single result)
        if len(results) < 2:
            return results

        # 3. The Elbow Logic (Adaptive Cutoff)
        cutoff_index = len(results)  # Default to keeping all if no drop is found

        for i in range(len(results) - 1):
            current_score = results[i].distance
            next_score = results[i + 1].distance

            # Calculate the "jump" in distance
            slope = next_score - current_score

            # If the gap is wider than our sensitivity, stop here.
            if slope > sensitivity:
                cutoff_index = i + 1
                break

        return results[:cutoff_index]
