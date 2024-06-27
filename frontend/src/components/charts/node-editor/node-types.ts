import { EdgeTypes, NodeTypes } from 'reactflow';
import { DataProductNode } from '@/components/charts/custom-nodes/data-product-node/data-product-node.tsx';
import { DatasetNode } from '@/components/charts/custom-nodes/dataset-node/dataset-node.tsx';
import { DefaultEdge } from '@/components/charts/custom-edges/default-edge/default-edge.tsx';

export enum CustomNodeTypes {
    DataProductNode = 'dataProductNode',
    DatasetNode = 'datasetNode',
}

export enum CustomEdgeTypes {
    DefaultEdge = 'defaultEdge',
}

export const nodeTypes: NodeTypes = {
    [CustomNodeTypes.DataProductNode]: DataProductNode,
    [CustomNodeTypes.DatasetNode]: DatasetNode,
};

export const edgeTypes: EdgeTypes = {
    [CustomEdgeTypes.DefaultEdge]: DefaultEdge,
};
