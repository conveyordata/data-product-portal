import typer
from fastembed import TextEmbedding

from app.core.embed.model import EMBEDDING_MODEL

app = typer.Typer(help="Embeddings toolkit for the Data product portal.")


@app.command(short_help="Preload embedding model for caching")
def load_embeddings_model():
    TextEmbedding(EMBEDDING_MODEL).embed(["TEST"])


if __name__ == "__main__":
    app()
