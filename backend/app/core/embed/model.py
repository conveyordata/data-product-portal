from functools import cache

from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
RERANKER_MODEL = "jinaai/jina-reranker-v1-turbo-en"


@cache
def get_text_embedding_model() -> TextEmbedding:
    return TextEmbedding(EMBEDDING_MODEL)


@cache
def get_text_reranker_model() -> TextCrossEncoder:
    return TextCrossEncoder(model_name=RERANKER_MODEL)


def warm_text_embedding_model() -> None:
    next(iter(get_text_embedding_model().embed(["warmup"])), None)


def warm_text_reranker_model() -> None:
    next(iter(get_text_reranker_model().rerank("warmup", ["warmup"])), None)
