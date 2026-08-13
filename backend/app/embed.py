import typer

from app.core.embed.model import warm_text_embedding_model

app = typer.Typer(help="Embeddings toolkit for the Data product portal.")


@app.command(short_help="Preload embedding model for caching")
def load_embeddings_model():
    warm_text_embedding_model()


if __name__ == "__main__":
    app()
