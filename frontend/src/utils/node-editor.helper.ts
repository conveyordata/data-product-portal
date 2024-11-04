import { Edge, FitViewOptions, Node, Position } from 'reactflow';
import Dagre from '@dagrejs/dagre';
import { theme } from 'antd';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { CSSProperties } from 'react';
import { greenThemeConfig } from '@/theme/antd-theme.ts';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';

const { getDesignToken } = theme;

const token = getDesignToken(greenThemeConfig);

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

export const getDataProductDatasetLinkEdgeStyle = (status: DataProductDatasetLinkStatus): CSSProperties => {
    const edgeStyles: CSSProperties = {
        strokeDasharray: '5 5',
    };
    switch (status) {
        case DataProductDatasetLinkStatus.Approved:
            edgeStyles.stroke = token.colorPrimary;
            break;
        case DataProductDatasetLinkStatus.Denied:
        case DataProductDatasetLinkStatus.Pending:
        default:
            edgeStyles.stroke = token.colorPrimaryBorder;
            break;
    }

    return edgeStyles;
};

export const getDataOutputDatasetLinkEdgeStyle = (status: DataOutputDatasetLinkStatus): CSSProperties => {
    const edgeStyles: CSSProperties = {
        strokeDasharray: '5 5',
    };
    switch (status) {
        case DataOutputDatasetLinkStatus.Approved:
            edgeStyles.stroke = token.colorPrimary;
            break;
        case DataOutputDatasetLinkStatus.Denied:
        case DataOutputDatasetLinkStatus.Pending:
        default:
            edgeStyles.stroke = token.colorPrimaryBorder;
            break;
    }

    return edgeStyles;
};
