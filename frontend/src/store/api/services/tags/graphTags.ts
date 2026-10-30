import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { type Graph, NodeType } from '@/store/api/services/generated/graphApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

const nodeTagTypes = {
    [NodeType.DataProductNode]: TagTypes.DataProduct,
    [NodeType.ExplorationNode]: TagTypes.Exploration,
    [NodeType.OutputPortNode]: TagTypes.OutputPort,
    [NodeType.TechnicalAssetNode]: TagTypes.TechnicalAsset,
} as const;

const nodeTags = (graph?: Graph) =>
    (graph?.nodes ?? []).map((node) => ({ type: nodeTagTypes[node.type], id: node.data.id }));

export const graphTags = {
    getGraphData: {
        providesTags: (graph) => [
            ...nodeTags(graph),
            { type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.OutputPort, id: STATIC_TAG_ID.LIST },
        ],
    },
    getDataProductGraphData: {
        providesTags: (graph, _, { id }) => [
            ...nodeTags(graph),
            { type: TagTypes.DataProduct, id },
            { type: TagTypes.DataProductInputPorts, id },
            { type: TagTypes.DataProductOutputPorts, id },
            { type: TagTypes.DataProductTechnicalAssets, id },
        ],
    },
    getOutputPortGraphData: {
        providesTags: (graph, _, { id }) => [
            ...nodeTags(graph),
            { type: TagTypes.OutputPort, id },
            { type: TagTypes.OutputPortInputPorts, id },
        ],
    },
    getTechnicalAssetGraphData: {
        providesTags: (graph, _, { id }) => [...nodeTags(graph), { type: TagTypes.TechnicalAsset, id }],
    },
} satisfies EndpointDefinitions;
