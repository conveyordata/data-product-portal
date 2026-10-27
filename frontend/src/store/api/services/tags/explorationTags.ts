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
        invalidatesTags: [
            { type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.MyRequests },
            { type: TagTypes.Graph },
        ],
    },
    removeExploration: {
        invalidatesTags: (_, __, id) => [
            { type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.Exploration, id },
            { type: TagTypes.Graph, id: STATIC_TAG_ID.LIST },
        ],
    },
    requestInputPortsForExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: arg.id },
            ...arg.requestInputPortsForExplorationRequest.output_ports.map((op) => ({
                type: TagTypes.OutputPort,
                id: op.output_port_id,
            })),
            ...arg.requestInputPortsForExplorationRequest.output_ports.map((op) => ({
                type: TagTypes.History,
                id: op.output_port_id,
            })),
            ...arg.requestInputPortsForExplorationRequest.output_ports.map((op) => ({
                type: TagTypes.OutputPortInputPorts,
                id: op.output_port_id,
            })),
            { type: TagTypes.ExplorationInputPorts, id: arg.id },
            { type: TagTypes.MyRequests },
            { type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.Graph },
        ],
    },
    getExplorationInputPorts: {
        providesTags: (_, __, id) => [{ type: TagTypes.ExplorationInputPorts, id }],
    },
    renewInputPortForExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.ExplorationInputPorts, id: arg.id },
            { type: TagTypes.MyRequests },
            { type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
        ],
    },
    revokeInputPortForExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.ExplorationInputPorts, id: arg.id },
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
            { type: TagTypes.Graph },
        ],
    },
    cancelInputPortForExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.ExplorationInputPorts, id: arg.id },
            { type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
            { type: TagTypes.Graph },
        ],
    },
} satisfies EndpointDefinitions;
