import type { EdgeTypes, NodeTypes } from '@xyflow/react';

import { DefaultEdge } from '@/components/charts/custom-edges/default-edge';
import { DataProductNode } from '@/components/charts/custom-nodes/data-product-node/data-product-node.tsx';
import { DatasetNode } from '@/components/charts/custom-nodes/dataset-node/dataset-node.tsx';
import { DomainNode } from '@/components/charts/custom-nodes/domain-node/domain-node.tsx';

import { DataOutputNode } from '@/components/charts/custom-nodes/dataoutput-node/dataoutput-node';
import { StraightEdge } from '@/components/charts/custom-edges/straight-edge';

export enum CustomNodeTypes {
    DataProductNode = 'dataProductNode',
    DatasetNode = 'datasetNode',
    DataOutputNode = 'dataOutputNode',
    DomainNode = 'domainNode',
}

export enum CustomEdgeTypes {
    DefaultEdge = 'defaultEdge',
    StraightEdge = 'straightEdge',
}

export const nodeTypes: NodeTypes = {
    [CustomNodeTypes.DataProductNode]: DataProductNode,
    [CustomNodeTypes.DatasetNode]: DatasetNode,
    [CustomNodeTypes.DataOutputNode]: DataOutputNode,
    [CustomNodeTypes.DomainNode]: DomainNode,
};

export const edgeTypes: EdgeTypes = {
    [CustomEdgeTypes.DefaultEdge]: DefaultEdge,
    [CustomEdgeTypes.StraightEdge]: StraightEdge,
};
