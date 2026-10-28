from functools import cache

from fastembed import TextEmbedding

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


@cache
def get_text_embedding_model() -> TextEmbedding:
    return TextEmbedding(EMBEDDING_MODEL)


def warm_text_embedding_model() -> None:
    next(iter(get_text_embedding_model().embed(["warmup"])), None)
