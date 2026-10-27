import type { ResultDescription } from '@reduxjs/toolkit/query';
import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

const everyGraph = { type: TagTypes.Graph };
const globalGraph = { type: TagTypes.Graph, id: STATIC_TAG_ID.LIST };

const alsoInvalidate =
    (tag: typeof everyGraph | typeof globalGraph) =>
    <Result, Arg, Error, Meta>(definition: {
        invalidatesTags?: ResultDescription<string, Result, Arg, Error, Meta>;
    }) => {
        const { invalidatesTags } = definition;
        definition.invalidatesTags = (result, error, arg, meta) => [
            ...(typeof invalidatesTags === 'function'
                ? invalidatesTags(result, error, arg, meta)
                : (invalidatesTags ?? [])),
            tag,
        ];
    };

const refreshesEveryGraph = alsoInvalidate(everyGraph);
const refreshesGlobalGraph = alsoInvalidate(globalGraph);

export const graphTags = {
    getGraphData: { providesTags: [globalGraph] },
    getDataProductGraphData: { providesTags: (_, __, { id }) => [{ type: TagTypes.Graph, id }] },
    getOutputPortGraphData: { providesTags: (_, __, { id }) => [{ type: TagTypes.Graph, id }] },
    getTechnicalAssetGraphData: { providesTags: (_, __, { id }) => [{ type: TagTypes.Graph, id }] },

    createDataProduct: refreshesEveryGraph,
    updateDataProduct: refreshesEveryGraph,
    requestInputPortsForDataProduct: refreshesEveryGraph,
    cancelInputPortForDataProduct: refreshesEveryGraph,
    revokeInputPortForDataProduct: refreshesEveryGraph,
    renewInputPortForDataProduct: refreshesEveryGraph,
    createExploration: refreshesEveryGraph,
    requestInputPortsForExploration: refreshesEveryGraph,
    cancelInputPortForExploration: refreshesEveryGraph,
    revokeInputPortForExploration: refreshesEveryGraph,
    renewInputPortForExploration: refreshesEveryGraph,
    createOutputPort: refreshesEveryGraph,
    updateOutputPort: refreshesEveryGraph,
    grantOutputPortAccess: refreshesEveryGraph,
    approveOutputPortAsInputPort: refreshesEveryGraph,
    denyOutputPortAsInputPort: refreshesEveryGraph,
    renewOutputPortAsInputPort: refreshesEveryGraph,
    revokeOutputPortAsInputPort: refreshesEveryGraph,
    createTechnicalAsset: refreshesEveryGraph,
    updateTechnicalAsset: refreshesEveryGraph,
    linkOutputPortToTechnicalAsset: refreshesEveryGraph,
    unlinkOutputPortFromTechnicalAsset: refreshesEveryGraph,
    approveOutputPortTechnicalAssetLink: refreshesEveryGraph,
    denyOutputPortTechnicalAssetLink: refreshesEveryGraph,

    removeDataProduct: refreshesGlobalGraph,
    removeExploration: refreshesGlobalGraph,
    removeOutputPort: refreshesGlobalGraph,
    removeTechnicalAsset: refreshesGlobalGraph,
} satisfies EndpointDefinitions;
