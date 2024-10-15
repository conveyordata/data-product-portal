import { EdgeTypes, NodeTypes } from 'reactflow';
import { DataProductNode } from '@/components/charts/custom-nodes/data-product-node/data-product-node.tsx';
import { DatasetNode } from '@/components/charts/custom-nodes/dataset-node/dataset-node.tsx';
import { DefaultEdge } from '@/components/charts/custom-edges/default-edge/default-edge.tsx';
import { DataOutputNode } from '../custom-nodes/dataoutput-node/dataoutput-node';

export enum CustomNodeTypes {
    DataProductNode = 'dataProductNode',
    DatasetNode = 'datasetNode',
    DataOutputNode = 'dataOutputNode',
}

export enum CustomEdgeTypes {
    DefaultEdge = 'defaultEdge',
}

export const nodeTypes: NodeTypes = {
    [CustomNodeTypes.DataProductNode]: DataProductNode,
    [CustomNodeTypes.DatasetNode]: DatasetNode,
    [CustomNodeTypes.DataOutputNode]: DataOutputNode,
};

export const edgeTypes: EdgeTypes = {
    [CustomEdgeTypes.DefaultEdge]: DefaultEdge,
};
