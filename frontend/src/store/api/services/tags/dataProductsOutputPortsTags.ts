import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

const invalidateOutputPort = (
    _: unknown,
    __: unknown,
    { dataProductId, id }: { dataProductId: string; id: string },
) => [
    {
        type: TagTypes.OutputPort as const,
        id: id,
    },
    {
        type: TagTypes.OutputPort as const,
        id: STATIC_TAG_ID.LIST,
    },
    {
        type: TagTypes.DataProductOutputPorts as const,
        id: dataProductId,
    },
    {
        type: TagTypes.History as const,
        id: id,
    },
];

export const dataProductOutputPortTags = {
    getDataProductOutputPorts: {
        providesTags: (_, __, id) => [
            {
                type: TagTypes.DataProductOutputPorts,
                id: id,
            },
        ],
    },
    getOutputPortQueryStats: {},
    deleteOutputPortQueryStat: {},
    updateOutputPortQueryStats: {},
    getOutputPortCuratedQueries: {},
    getLatestDataQualitySummaryForOutputPort: {},
    addOutputPortDataQualityRun: {},
    overwriteOutputPortDataQualitySummary: {},
    createOutputPort: {
        invalidatesTags: (_, __, { dataProductId }) => [
            {
                type: TagTypes.DataProductOutputPorts,
                id: dataProductId,
            },
        ],
    },
    getOutputPort: {
        providesTags: (_, __, { id }) => [
            {
                type: TagTypes.OutputPort,
                id: id,
            },
        ],
    },
    removeOutputPort: {
        invalidatesTags: invalidateOutputPort,
    },
    updateOutputPort: {
        invalidatesTags: invalidateOutputPort,
    },
    getOutputPortsEventHistory: {
        providesTags: (_, __, { id }) => [
            {
                type: TagTypes.History,
                id: id,
            },
        ],
    },
    updateOutputPortAbout: {
        invalidatesTags: invalidateOutputPort,
    },
    updateOutputPortStatus: {
        invalidatesTags: invalidateOutputPort,
    },
    setValueForOutputPort: {
        invalidatesTags: invalidateOutputPort,
    },
} satisfies EndpointDefinitions;
