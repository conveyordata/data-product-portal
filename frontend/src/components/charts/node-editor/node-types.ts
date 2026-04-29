import type { EdgeTypes, NodeTypes } from '@xyflow/react';

import { DefaultEdge } from '@/components/charts/custom-edges/default-edge';
import { StraightEdge } from '@/components/charts/custom-edges/straight-edge';
import { DataProductNode } from '@/components/charts/custom-nodes/data-product-node/data-product-node.tsx';
import { DomainNode } from '@/components/charts/custom-nodes/domain-node/domain-node.tsx';
import { ExplorationNode } from '@/components/charts/custom-nodes/exploration-node/exploration-node.tsx';
import { OutputPortNode } from '@/components/charts/custom-nodes/output-port-node/output-port-node.tsx';
import { NodeType } from '@/store/api/services/generated/graphApi.ts';
import { TechnicalAssetNode } from '../custom-nodes/technical-asset-node/technical-asset-node';

export enum CustomEdgeTypes {
    DefaultEdge = 'defaultEdge',
    StraightEdge = 'straightEdge',
}

export const nodeTypes: NodeTypes = {
    [NodeType.DataProductNode]: DataProductNode,
    [NodeType.OutputPortNode]: OutputPortNode,
    [NodeType.TechnicalAssetNode]: TechnicalAssetNode,
    [NodeType.DomainNode]: DomainNode,
    [NodeType.ExplorationNode]: ExplorationNode,
};

export const edgeTypes: EdgeTypes = {
    [CustomEdgeTypes.DefaultEdge]: DefaultEdge,
    [CustomEdgeTypes.StraightEdge]: StraightEdge,
};
