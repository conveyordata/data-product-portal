import Dagre from '@dagrejs/dagre';
import type { Edge, FitViewOptions, Node } from '@xyflow/react';
import { Position } from '@xyflow/react';

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

    for (const node of nodes) {
        graph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    }
    for (const edge of edges) {
        graph.setEdge(edge.source, edge.target);
    }

    Dagre.layout(graph);

    for (const node of nodes) {
        if (graph.node(node.id)) {
            const position = graph.node(node.id);
            node.targetPosition = isHorizontal ? Position.Left : Position.Top;
            node.sourcePosition = isHorizontal ? Position.Right : Position.Bottom;

            node.position = {
                x: position.x - nodeWidth / 2,
                y: position.y - nodeHeight / 2,
            };
        }
    }

    return { nodes, edges };
};

export const defaultFitViewOptions: FitViewOptions = {
    padding: 0.1,
    maxZoom: 1.25,
};
