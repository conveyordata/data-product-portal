import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';
import { requestListTags } from '@/store/api/services/tags/requestTags.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const explorationTags = {
    getExplorations: {
        providesTags: [{ type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST }],
    },
    getExploration: {
        providesTags: (response) => (response?.id ? [{ type: TagTypes.Exploration, id: response?.id }] : []),
    },
    createExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST },
            ...(arg.input_ports?.output_ports?.map((op) => ({
                type: TagTypes.OutputPort,
                id: op.output_port_id,
            })) ?? []),
            ...(arg.input_ports?.output_ports?.map((op) => ({ type: TagTypes.History, id: op.output_port_id })) ?? []),
            ...requestListTags,
        ],
    },
    removeExploration: {
        invalidatesTags: [{ type: TagTypes.Exploration, id: STATIC_TAG_ID.LIST }],
    },
    requestInputPortsForExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.Exploration, id: arg.id },
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
            ...requestListTags,
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
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
            ...requestListTags,
        ],
    },
    revokeInputPortForExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.ExplorationInputPorts, id: arg.id },
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
            ...requestListTags,
        ],
    },
    cancelInputPortForExploration: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.ExplorationInputPorts, id: arg.id },
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
            ...requestListTags,
        ],
    },
} satisfies EndpointDefinitions;
