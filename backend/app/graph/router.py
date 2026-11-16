from fastapi import APIRouter

from app.database.deps import DbSession
from app.graph.graph import Graph
from app.graph.service import GraphService

router = APIRouter(tags=["Graph"])


@router.get("/v2/graph")
def get_graph_data(
    db: DbSession,
    output_port_nodes_enabled: bool = False,
    exploration_nodes_enabled: bool = False,
) -> Graph:
    return GraphService(db).get_graph_data(
        exploration_nodes_enabled=exploration_nodes_enabled,
        output_port_nodes_enabled=output_port_nodes_enabled,
    )
