from fastapi.routing import APIRoute

from app.main import app


def iter_app_routes():
    def walk(node):
        if isinstance(node, APIRoute):
            yield node
            return

        if type(node).__name__ == "_IncludedRouter":
            for candidate in node.effective_candidates():
                yield from walk(candidate)
            return

        if hasattr(node, "path") and hasattr(node, "dependencies"):
            yield node

    for route in app.routes:
        yield from walk(route)
