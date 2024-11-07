import { Edge, FitViewOptions, Node, Position } from 'reactflow';
import Dagre from '@dagrejs/dagre';

export function getDagreDirection(direction: Position) {
    switch (direction) {
        case Position.Left:
            return 'LR';
        case Position.Top:
            return 'TB';
        case Position.Right:
            return 'RL';
        case Position.Bottom:
            return 'BT';
        default:
            return 'LR';
    }
}

export const generateDagreLayout = (
    nodes: Node[],
    edges: Edge[],
    direction: Position,
    nodeWidth: number,
    nodeHeight: number,
) => {
    const graph = new Dagre.graphlib.Graph();
    const isHorizontal = direction === Position.Left || direction === Position.Right;
    graph.setDefaultEdgeLabel(() => ({}));
    graph.setGraph({ rankdir: getDagreDirection(direction) });

    nodes.forEach((node) => {
        graph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });
    edges.forEach((edge) => graph.setEdge(edge.source, edge.target));

    Dagre.layout(graph);

    nodes.forEach((node) => {
        if (graph.node(node.id)) {
            const position = graph.node(node.id);
            node.targetPosition = isHorizontal ? Position.Left : Position.Top;
            node.sourcePosition = isHorizontal ? Position.Right : Position.Bottom;

            node.position = {
                x: position.x - nodeWidth / 2,
                y: position.y - nodeHeight / 2,
            };
        }
    });

    return { nodes, edges };
};

export const defaultFitViewOptions: FitViewOptions = {
    padding: 0.1,
    maxZoom: 1.25,
};
