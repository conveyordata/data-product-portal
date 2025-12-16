import json
from typing import Sequence

import boto3
from fastembed import TextEmbedding
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.datasets.embeddings.model import DatasetEmbedding
from app.datasets.schema_response import DatasetEmbed2, DatasetEmbeddingResult

# model_id = "cohere.embed-english-v3"
model_id = "cohere.embed-v4:0"


class DatasetEmbeddingsService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def generate_embeddings_with_bedrock(texts: list[str]) -> list[list[float]]:
        client = boto3.client("bedrock-runtime")
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({"texts": texts, "input_type": "search_document"}),
        )
        model_response = json.loads(response["body"].read())
        return model_response["embeddings"]["float"]
        # return model_response["embeddings"]
        # return DatasetEmbed(id=dataset_id)

    @staticmethod
    def generate_embeddings_local(texts: list[str]) -> list[list[float]]:
        model = TextEmbedding()
        return [bl.tolist() for bl in model.embed(texts)]

    @staticmethod
    def generate_embeddings(texts: list[str]) -> list[list[float]]:
        return DatasetEmbeddingsService.generate_embeddings_local(texts)

    def serialize_dataset(self, dataset: DatasetEmbed2) -> str:
        # 1. Start with the core identity
        lines = [
            f"Dataset: {dataset.name}",
            f"Status: {dataset.status}",
            f"Domain: {dataset.domain.name}Description: {dataset.description}",
        ]

        # 2. Add optional context
        if dataset.about:
            lines.append(f"About: {dataset.about}")

        # 3. Integrate the Data Product context naturally
        if dataset.data_product:
            lines.append(f"Parent Data Product: {dataset.data_product.name}")
            lines.append(f"Product Context: {dataset.data_product.description}")

        # 4. Flatten the Data Outputs into a concise list
        if dataset.data_output_links:
            outputs = []
            for link in dataset.data_output_links:
                # We skip 'namespace' usually, unless it's critical for search differentiation
                output_str = (
                    f"- {link.data_output.name}: {link.data_output.description}"
                )
                outputs.append(output_str)

            lines.append("Contains Data Outputs:")
            lines.extend(outputs)

        # 5. Join with newlines to create distinct "thoughts" for the model
        return "\n".join(lines)

    def insert_embeddings_for_datasets(self, datasets: Sequence[DatasetEmbed2]):
        embeddings = self.generate_embeddings(
            [self.serialize_dataset(ds) for ds in datasets]
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
            # .where(distance <= max_distance)
            .order_by(distance)
            .limit(10)
        )
        return self.db.execute(stmt).all()
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
                logger.info("Cutoff")
                cutoff_index = i + 1
                break

        return results[:cutoff_index]
