import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const explorationTags = {
    //Explorations api
    getExplorations: {
        providesTags: [{ type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST }],
    },
    getExploration: {
        providesTags: (response) => (response?.id ? [{ type: TagTypes.Exploration, id: response?.id }] : []),
    },
    createExploration: {
        invalidatesTags: [{ type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST }, { type: TagTypes.MyRequests }],
    },
    removeExploration: {
        invalidatesTags: (_, __, id) => [
            { type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.Exploration, id },
        ],
    },
    requestInputPortsForExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: arg.id },
            ...arg.requestInputPortsForExplorationRequest.output_ports.map((id) => ({
                type: TagTypes.OutputPort,
                id,
            })),
            ...arg.requestInputPortsForExplorationRequest.output_ports.map((id) => ({ type: TagTypes.History, id })),
            { type: TagTypes.ExplorationInputPorts, id: arg.id },
            { type: TagTypes.MyRequests },
        ],
    },
    getExplorationInputPorts: {
        providesTags: (_, __, id) => [{ type: TagTypes.ExplorationInputPorts, id }],
    },
} satisfies EndpointDefinitions;
