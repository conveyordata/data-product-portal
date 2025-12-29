from uuid import UUID

from sqlalchemy import TextClause, text

from app.core.logging import logger


def recalculate_search_vector_statement(dataset_id: UUID | None = None) -> TextClause:
    logger.debug(
        "Recalculating search vector for"
        f"{str(dataset_id) if dataset_id else 'all datasets'}"
    )

    if dataset_id:
        return text(
            """
WITH data_outputs_vectors AS (
    SELECT dod.dataset_id,
        (
            setweight(to_tsvector('english',
                string_agg(coalesce(data_outputs.name, ''), ' ')),
                      'A') ||
            setweight(to_tsvector('english',
                string_agg(coalesce(data_outputs.description, ''), ' ')),
                      'B')
        ) AS search_vector
    FROM data_outputs
             JOIN data_outputs_datasets dod on dod.data_output_id = data_outputs.id
WHERE dod.dataset_id = :dataset_id
    GROUP BY dod.dataset_id),
dataset_search_vectors AS (
    SELECT datasets.id,
        (
            setweight(
                    to_tsvector('english', coalesce(datasets.name, '')),
                    'A') ||
            setweight(
                    to_tsvector('english', coalesce(datasets.description, '')),
                    'B') ||
            coalesce(dov.search_vector, to_tsvector('english', ''))
        ) AS new_search_vector
    FROM datasets
    LEFT JOIN data_outputs_vectors dov ON dov.dataset_id = datasets.id
    WHERE datasets.id = :dataset_id)
UPDATE datasets ds
SET search_vector = csv.new_search_vector FROM dataset_search_vectors csv
WHERE ds.id = csv.id;
"""
        ).bindparams(dataset_id=dataset_id)
    else:
        return text(
            """
WITH data_outputs_vectors AS (
    SELECT dod.dataset_id,
        (
            setweight(to_tsvector('english',
                string_agg(coalesce(data_outputs.name, ''), ' ')),
                      'A') ||
            setweight(to_tsvector('english',
                string_agg(coalesce(data_outputs.description, ''), ' ')),
                      'B')
        ) AS search_vector
    FROM data_outputs
             JOIN data_outputs_datasets dod on dod.data_output_id = data_outputs.id
    GROUP BY dod.dataset_id),
dataset_search_vectors AS (
    SELECT datasets.id,
        (
            setweight(
                    to_tsvector('english', coalesce(datasets.name, '')),
                    'A') ||
            setweight(
                    to_tsvector('english', coalesce(datasets.description, '')),
                    'B') ||
            coalesce(dov.search_vector, to_tsvector('english', ''))
        ) AS new_search_vector
    FROM datasets
    LEFT JOIN data_outputs_vectors dov ON dov.dataset_id = datasets.id)
UPDATE datasets ds
SET search_vector = csv.new_search_vector FROM dataset_search_vectors csv
WHERE ds.id = csv.id;
"""
        )


def recalculate_search_vector_dataset_statement(dataset_id: UUID) -> TextClause:
    return recalculate_search_vector_statement(dataset_id)


def recalculate_search_vector_datasets_statement() -> TextClause:
    return recalculate_search_vector_statement()
