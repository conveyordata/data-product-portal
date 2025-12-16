import copy
import json
import time
from typing import Iterable, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Float, Integer, asc, column, desc, func, select, values
from sqlalchemy.orm import Session, joinedload, raiseload, selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.configuration.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import ensure_tag_exists
from app.core.ai.search_agent import SearchAgent
from app.core.authz import Authorization
from app.core.aws.boto3_clients import get_client
from app.core.logging import logger
from app.core.namespace.validation import (
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
    NamespaceValidator,
    NamespaceValidityType,
)
from app.data_outputs.model import DataOutput
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.datasets.enums import OutputPortAccessType
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.datasets.schema_request import (
    DatasetAboutUpdate,
    DatasetCreate,
    DatasetEmbed,
    DatasetStatusUpdate,
    DatasetUpdate,
    DatasetUsageUpdate,
)
from app.datasets.schema_response import (
    DatasetEmbeddingResult,
    DatasetGet,
    DatasetsAIGet,
    DatasetsAISearch,
    DatasetsAISearchResult,
    DatasetsGet,
    DatasetsSearch,
)
from app.datasets.search_dataset import (
    recalculate_search_vector_dataset_statement,
    recalculate_search_vector_datasets_statement,
)
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.settings import settings
from app.users.model import User as UserModel
from app.users.schema import User


def get_dataset_load_options():
    return [
        selectinload(DatasetModel.data_product_links)
        .selectinload(DataProductDatasetAssociationModel.data_product)
        .raiseload("*"),
        selectinload(DatasetModel.data_output_links)
        .selectinload(DataOutputDatasetAssociationModel.data_output)
        .options(
            joinedload(DataOutput.configuration),
            joinedload(DataOutput.owner),
            raiseload("*"),
        ),
    ]


class DatasetService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = NamespaceValidator(DatasetModel)
        self.client = get_client("bedrock-runtime")
        self.model = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    def get_dataset(self, id: UUID, user: UserModel) -> DatasetGet:
        dataset = self.db.get(
            DatasetModel,
            id,
            options=[
                selectinload(DatasetModel.data_product_links),
                selectinload(DatasetModel.data_output_links),
            ],
        )

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
            )

        if not self.is_visible_to_user(dataset, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private dataset",
            )

        rolled_up_tags = set()
        for output_link in dataset.data_output_links:
            rolled_up_tags.update(output_link.data_output.tags)

        dataset.rolled_up_tags = rolled_up_tags

        if not dataset.lifecycle:
            default_lifecycle = self.db.scalar(
                select(DataProductLifeCycleModel).where(
                    DataProductLifeCycleModel.is_default
                )
            )
            dataset.lifecycle = default_lifecycle

        return dataset

    def explain_query_match_with_AI(self, query: str, id: UUID, user: User) -> str:
        dataset = self.get_dataset(id, user)
        response = self.client.converse(
            modelId=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": f"Explain the users why this search query: {query} matches the results: {DatasetGet.model_validate(dataset).model_dump_json()}"
                        },
                    ],
                },
            ],
            system=[
                {
                    "text": "Keep it short and simple, at most 2 short sentences. Do not use markdown",
                }
            ],
        )
        return response["output"]["message"]["content"][0]["text"]

    def search_datasets_with_AI(
        self, query: str, limit: int, user: UserModel
    ) -> DatasetsAISearchResult:
        # Currently, this method just calls the regular search_datasets method.
        # In the future, this can be extended to include AI-based search enhancements.
        # Profile the time taken for the AI search
        start_time = time.time()

        datasets = self.get_datasets(user)
        full_datasets = [DatasetsAIGet.model_validate(dataset) for dataset in datasets]
        embed_datasets = [DatasetEmbed.model_validate(dataset) for dataset in datasets]
        stop_time = time.time()
        logger.info(
            f"Fetched and prepared {len(datasets)} datasets in {stop_time - start_time} seconds for AI search."
        )
        start_time = time.time()
        search_agent = SearchAgent()
        response = search_agent.converse(f"""
You are a strict dataset relevance filter.

Task:
Select the most relevant datasets for the user query below.

User query:
"{query}"

Candidate datasets (JSON, authoritative, do not invent new ones):
{json.dumps([d.model_dump_json() for d in embed_datasets], indent=2)}

Rules:
- Only select datasets that are HIGHLY relevant to the query.
- If a dataset is not clearly relevant, DO NOT include it.
- NEVER hallucinate datasets or IDs.
- NEVER modify dataset IDs.
- Base your decision only on the provided dataset content.

For each selected dataset, assign:
- rank: a float between 0 and 1 indicating relevance confidence
- reason:
  - If relevance is HIGH → provide a concrete explanation
  - Otherwise → do NOT include the dataset at all

Output constraints:
- Return at most {limit} datasets
- You may return fewer or an empty list
- Output MUST be valid JSON
- Output MUST have a single overlapping reasoning, that does not repeat the user query.
- Output MUST be a descending order list by rank
- Output MUST match this exact schema:

[
  {{
    "id": "UUID",
    "rank": 0.0,
    "reason": "string"
  }}
]

Return JSON only. No commentary. No markdown.
Before the JSON list, show a generic reply or summary of why you have added these datasets.
Keep this reasoning brief (1-2 sentences). Don't repeat the query in the reasoning. Only add your reasoning.
""")
        # Parse response into Sequence[DatasetsAISearch] object
        # drop everything not between [ and ]
        reasoning = response[: response.index("[")].strip()
        reasoning = reasoning.strip("```json").strip("```").strip()
        response = response[response.index("[") : response.rindex("]") + 1]
        stop_time = time.time()
        logger.info(f"AI search completed in {stop_time - start_time} seconds.")
        start_time = time.time()
        datasets = json.loads(response)
        result: list[DatasetsAISearch] = []
        for dataset in datasets:
            matched_dataset = [d for d in full_datasets if d.id == UUID(dataset["id"])]
            if len(matched_dataset) != 1:
                logger.warning(
                    f"Dataset with id {dataset['id']} not found in database. Or multiple returned!"
                )
            base = matched_dataset[0].model_dump()
            result.append(
                DatasetsAISearch.model_validate(
                    {
                        **base,
                        "rank": dataset["rank"],
                        "reason": dataset["reason"],
                    }
                )
            )
        stop_time = time.time()
        logger.info(f"Processed AI search results in {stop_time - start_time} seconds.")
        return DatasetsAISearchResult(datasets=result, reasoning=reasoning)

    def search_datasets_with_AI_stream(
        self, query: str, limit: int, user: UserModel
    ) -> DatasetsAISearchResult:
        # Currently, this method just calls the regular search_datasets method.
        # In the future, this can be extended to include AI-based search enhancements.
        # Profile the time taken for the AI search
        start_time = time.time()

        datasets = self.get_datasets(user)
        full_datasets = [DatasetsAIGet.model_validate(dataset) for dataset in datasets]
        embed_datasets = [DatasetEmbed.model_validate(dataset) for dataset in datasets]
        stop_time = time.time()
        logger.info(
            f"Fetched and prepared {len(datasets)} datasets in {stop_time - start_time} seconds for AI search."
        )
        start_time = time.time()
        search_agent = SearchAgent()
        response = search_agent.converse_stream(f"""
You are a strict dataset relevance filter.

Task:
Select the most relevant datasets for the user query below.

User query:
"{query}"

Candidate datasets (JSON, authoritative, do not invent new ones):
{json.dumps([d.model_dump_json() for d in embed_datasets], indent=2)}

Rules:
- Only select datasets that are HIGHLY relevant to the query.
- If a dataset is not clearly relevant, DO NOT include it.
- NEVER hallucinate datasets or IDs.
- NEVER modify dataset IDs.
- Base your decision only on the provided dataset content.

For each selected dataset, assign:
- rank: a float between 0 and 1 indicating relevance confidence
- reason:
  - If relevance is HIGH → provide a concrete explanation
  - Otherwise → do NOT include the dataset at all

Output constraints:
- Return at most {limit} datasets
- You may return fewer or an empty list
- Output MUST be valid JSON
- Output MUST be a descending order list by rank
- Return ONE dataset per line as JSON.
- Do NOT wrap results in an array.
- Each line must be valid JSON.

Return JSON only. No commentary. No markdown.
IMPORTANT:
- Output ONE dataset per line
- Each line MUST be valid JSON
- DO NOT wrap results in an array
- DO NOT use markdown
- DO NOT add explanations
- Emit nothing except JSON lines
- DO NOT add any extra text

e.g.
{{"id": "123e4567-e89b-12d3-a456-426614174000", "rank": 0.95, "reason": "This dataset is highly relevant because..."}}
""")
        buffer = ""

        for event in response:
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]

                if "text" in delta["delta"]:
                    text = delta["delta"]["text"]
                    buffer += text

                    # Process complete lines
                    # Process anything between { and }
                    while "}" in buffer:
                        chunk, buffer = buffer.split("}", 1)
                        chunk += "}"

                        chunk = chunk.lstrip("```json\n")
                        try:
                            dataset = json.loads(chunk)
                        except json.JSONDecodeError:
                            buffer = chunk + buffer
                            break

                        # try:
                        #     dataset = json.loads(line)
                        # except json.JSONDecodeError:
                        #     continue  # wait for more tokens
                        matched = [
                            d for d in full_datasets if d.id == UUID(dataset["id"])
                        ]

                        if len(matched) != 1:
                            logger.warning(f"Dataset {dataset['id']} not found")
                            continue

                        base = matched[0].model_dump()

                        result = DatasetsAISearch.model_validate(
                            {
                                **base,
                                "rank": dataset["rank"],
                                "reason": dataset["reason"],
                            }
                        )

                        # 🔥 stream immediately
                        yield (
                            json.dumps(
                                {
                                    "type": "dataset",
                                    "payload": result.model_dump_json(),
                                }
                            )
                            + "\n"
                        )

            elif "messageStop" in event:
                break

    def search_datasets(
        self, query: str, limit: int, user: UserModel
    ) -> Sequence[DatasetsSearch]:
        load_options = get_dataset_load_options()
        stmt = (
            select(
                DatasetModel,
                func.ts_rank_cd(
                    DatasetModel.search_vector,
                    func.websearch_to_tsquery("english", query),
                    32,  # 32 normalizes all results between 0-1
                ).label("rank"),
            )
            .options(*load_options)
            .where(
                DatasetModel.search_vector.op("@@")(
                    func.websearch_to_tsquery("english", query)
                )
            )
            .order_by(desc("rank"))
        )
        results = self.db.execute(stmt).unique().all()
        filtered_datasets: list[DatasetsSearch] = []
        for row in results:
            if len(filtered_datasets) >= limit:
                return filtered_datasets
            dataset = row[0]
            rank = row[1]
            if self.is_visible_to_user(dataset, user):
                dataset.rank = rank
                filtered_datasets.append(dataset)
        return filtered_datasets

    def recalculate_search_vector_for(self, dataset_id: UUID) -> int:
        if settings.SEARCH_INDEXING_DISABLED:
            logger.debug("Search indexing is disabled, skipping recalculation")
            return 0
        sql = recalculate_search_vector_dataset_statement(dataset_id)
        result = self.db.execute(sql, {"dataset_id": dataset_id})
        return result.rowcount

    def recalculate_search_vector_datasets(self) -> int:
        if settings.SEARCH_INDEXING_DISABLED:
            logger.debug("Search indexing is disabled, skipping recalculation")
            return 0
        sql = recalculate_search_vector_datasets_statement()
        result = self.db.execute(sql)
        self.db.commit()
        return result.rowcount

    def get_datasets(
        self,
        user: UserModel,
    ) -> Sequence[DatasetsGet]:
        load_options = get_dataset_load_options()
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        query = (
            select(DatasetModel).options(*load_options).order_by(asc(DatasetModel.name))
        )
        datasets = [
            dataset
            for dataset in self.db.scalars(query).unique().all()
            if self.is_visible_to_user(dataset, user)
        ]

        for dataset in datasets:
            if not dataset.lifecycle:
                dataset.lifecycle = default_lifecycle
        return datasets

    def get_datasets_from_embeddings_search(
        self,
        user: UserModel,
        search_results: Sequence[DatasetEmbeddingResult],
    ) -> Sequence[DatasetsGet]:
        load_options = get_dataset_load_options()
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        id_col = column("id", Integer)
        distance_col = column("distance", Float)

        search_data = [
            (
                r.id,
                r.distance,
            )
            for r in search_results
        ]
        search_cte = (
            values(id_col, distance_col, name="search_vals")
            .data(search_data)
            .cte("search_results_cte")
        )
        query = (
            select(DatasetModel)
            .options(*load_options)
            .join(search_cte, DatasetModel.id == search_cte.c.id)
            .order_by(asc(search_cte.c.distance))
        )
        datasets = [
            dataset
            for dataset in self.db.scalars(query).unique().all()
            if self.is_visible_to_user(dataset, user)
        ]

        for dataset in datasets:
            if not dataset.lifecycle:
                dataset.lifecycle = default_lifecycle
        return datasets

    def get_datasets_for_embedding(self) -> Sequence[DatasetEmbed]:
        return [
            DatasetEmbed.model_validate(ds)
            for ds in (
                self.db.scalars(
                    select(DatasetModel)
                    .options(
                        selectinload(DatasetModel.data_product).raiseload("*"),
                        selectinload(DatasetModel.data_output_links)
                        .selectinload(DataOutputDatasetAssociationModel.data_output)
                        .raiseload("*"),
                    )
                    .order_by(asc(DatasetModel.name))
                )
                .unique()
                .all()
            )
        ]

    def get_user_datasets(self, user_id: UUID) -> Sequence[DatasetsGet]:
        return (
            self.db.scalars(
                select(DatasetModel)
                .options(
                    selectinload(DatasetModel.data_product_links).raiseload("*"),
                    selectinload(DatasetModel.data_output_links)
                    .selectinload(DataOutputDatasetAssociationModel.data_output)
                    .options(
                        joinedload(DataOutput.configuration),
                        joinedload(DataOutput.owner),
                        raiseload("*"),
                    ),
                )
                .filter(DatasetModel.assignments.any(user_id=user_id))
                .order_by(asc(DatasetModel.name))
            )
            .unique()
            .all()
        )

    def _fetch_tags(self, tag_ids: Iterable[UUID] = ()) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, self.db)
            tags.append(tag)

        return tags

    def create_dataset(self, dataset: DatasetCreate) -> DatasetModel:
        if (
            validity := self.namespace_validator.validate_namespace(
                dataset.namespace, self.db
            ).validity
        ) != NamespaceValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        dataset_schema = dataset.parse_pydantic_schema()
        tags = self._fetch_tags(dataset_schema.pop("tag_ids", []))
        _ = dataset_schema.pop("owners", [])
        model = DatasetModel(**dataset_schema, tags=tags)

        self.db.add(model)
        self.db.flush()
        self.recalculate_search_vector_for(model.id)
        self.db.commit()
        return model

    def remove_dataset(self, id: UUID) -> DatasetModel:
        dataset = self.db.get(DatasetModel, id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {id} not found"
            )

        result = copy.deepcopy(dataset)
        self.db.delete(dataset)
        self.db.commit()
        return result

    def update_dataset(self, id: UUID, dataset: DatasetUpdate) -> dict[str, UUID]:
        current_dataset = ensure_dataset_exists(id, self.db)
        updated_dataset = dataset.model_dump(exclude_unset=True)

        if (
            current_dataset.namespace != dataset.namespace
            and (
                validity := self.namespace_validator.validate_namespace(
                    dataset.namespace, self.db
                ).validity
            )
            != NamespaceValidityType.VALID
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        for k, v in updated_dataset.items():
            if k == "tag_ids":
                new_tags = self._fetch_tags(v)
                current_dataset.tags = new_tags
            else:
                setattr(current_dataset, k, v) if v else None
        self.db.flush()
        self.recalculate_search_vector_for(id)
        self.db.commit()
        return {"id": current_dataset.id}

    def update_dataset_about(
        self,
        id: UUID,
        dataset: DatasetAboutUpdate,
    ) -> None:
        current_dataset = ensure_dataset_exists(id, self.db)
        current_dataset.about = dataset.about
        self.db.commit()

    def update_dataset_status(
        self,
        id: UUID,
        dataset: DatasetStatusUpdate,
    ) -> None:
        current_dataset = ensure_dataset_exists(id, self.db)
        current_dataset.status = dataset.status
        self.db.commit()

    def update_dataset_usage(
        self,
        id: UUID,
        usage: DatasetUsageUpdate,
    ) -> DatasetModel:
        current_dataset = ensure_dataset_exists(id, self.db)
        current_dataset.usage = usage.usage
        self.db.commit()
        return current_dataset

    def get_graph_data(self, id: UUID, level: int) -> Graph:
        dataset = self.db.get(
            DatasetModel,
            id,
            options=[
                selectinload(DatasetModel.data_product_links),
                selectinload(DatasetModel.data_output_links),
            ],
        )
        nodes = [
            Node(
                id=id,
                isMain=True,
                data=NodeData(id=id, name=dataset.name),
                type=NodeType.datasetNode,
            )
        ]
        edges = []
        for downstream_products in dataset.data_product_links:
            nodes.append(
                Node(
                    id=downstream_products.data_product_id,
                    data=NodeData(
                        id=downstream_products.data_product_id,
                        name=downstream_products.data_product.name,
                        icon_key=downstream_products.data_product.type.icon_key,
                    ),
                    type=NodeType.dataProductNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{downstream_products.id}-{dataset.id}",
                    target=downstream_products.data_product_id,
                    source=dataset.id,
                    animated=downstream_products.status == DecisionStatus.APPROVED,
                )
            )

        for data_output_link in dataset.data_output_links:
            data_output = data_output_link.data_output
            nodes.append(
                Node(
                    id=data_output.id,
                    data=NodeData(
                        id=data_output.id,
                        icon_key=data_output.configuration.configuration_type,
                        name=data_output.name,
                        link_to_id=data_output.owner_id,
                    ),
                    type=NodeType.dataOutputNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{data_output.id}-{dataset.id}",
                    source=data_output.id,
                    target=dataset.id,
                    animated=data_output_link.status == DecisionStatus.APPROVED,
                )
            )
            if level >= 2:
                nodes.append(
                    Node(
                        id=f"{data_output.owner.id}_2",
                        data=NodeData(
                            id=f"{data_output.owner.id}",
                            name=data_output.owner.name,
                            icon_key=data_output.owner.type.icon_key,
                        ),
                        type=NodeType.dataProductNode,
                    )
                )
                edges.append(
                    Edge(
                        id=f"{data_output.owner.id}-{data_output.id}-2",
                        target=data_output.id,
                        source=f"{data_output.owner.id}_2",
                        animated=True,
                    )
                )

        # if no data outputs are linked yet, still show the owner data product
        if level >= 2 and not dataset.data_output_links:
            nodes.append(
                Node(
                    id=f"{dataset.data_product.id}_2",
                    data=NodeData(
                        id=f"{dataset.data_product.id}",
                        name=dataset.data_product.name,
                        icon_key=dataset.data_product.type.icon_key,
                    ),
                    type=NodeType.dataProductNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{dataset.data_product.id}-{dataset.id}-2",
                    target=dataset.id,
                    source=f"{dataset.data_product.id}_2",
                    animated=True,
                )
            )

        return Graph(nodes=set(nodes), edges=set(edges))

    def validate_dataset_namespace(self, namespace: str) -> NamespaceValidation:
        return self.namespace_validator.validate_namespace(namespace, self.db)

    @classmethod
    def dataset_namespace_suggestion(cls, name: str) -> NamespaceSuggestion:
        return NamespaceValidator.namespace_suggestion(name)

    @classmethod
    def dataset_namespace_length_limits(cls) -> NamespaceLengthLimits:
        return NamespaceValidator.namespace_length_limits()

    def is_visible_to_user(self, dataset: DatasetModel, user: User) -> bool:
        if (
            dataset.access_type != OutputPortAccessType.PRIVATE
            or Authorization().has_admin_role(user_id=str(user.id))
            or DatasetRoleAssignmentService(self.db).has_assignment(
                dataset_id=dataset.id, user=user
            )
        ):
            return True

        consuming_data_products = {
            link.data_product
            for link in dataset.data_product_links
            if link.status == DecisionStatus.APPROVED
        }

        user_data_products = {
            assignment.data_product
            for assignment in user.data_product_roles
            if assignment.decision == DecisionStatus.APPROVED
        }

        return bool(consuming_data_products & user_data_products)
