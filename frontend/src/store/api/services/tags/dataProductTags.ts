import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';
import { requestListTags } from '@/store/api/services/tags/requestTags.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const dataProductTags = {
    getDataProducts: {
        providesTags: [{ type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST }],
    },
    getDataProduct: {
        providesTags: (response) => (response?.id ? [{ type: TagTypes.DataProduct, id: response?.id }] : []),
    },
    createDataProduct: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST },
            ...(arg.input_ports?.output_ports?.map((op) => ({
                type: TagTypes.OutputPort,
                id: op.output_port_id,
            })) ?? []),
            ...(arg.input_ports?.output_ports?.map((op) => ({ type: TagTypes.History, id: op.output_port_id })) ?? []),
            ...requestListTags,
        ],
    },
    removeDataProduct: {
        invalidatesTags: [{ type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST }],
    },
    updateDataProduct: {
        invalidatesTags: (resp) =>
            resp?.id
                ? [
                      { type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST },
                      { type: TagTypes.DataProduct, id: resp?.id },
                      { type: TagTypes.DataProductRolledUpTags, id: resp?.id },
                  ]
                : [{ type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST }],
    },
    updateDataProductAbout: {
        invalidatesTags: (resp) =>
            resp?.id
                ? [
                      { type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST },
                      { type: TagTypes.DataProduct, id: resp?.id },
                  ]
                : [{ type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST }],
    },
    updateDataProductStatus: {
        invalidatesTags: (resp) =>
            resp?.id
                ? [
                      { type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST },
                      { type: TagTypes.DataProduct, id: resp?.id },
                  ]
                : [{ type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST }],
    },
    updateDataProductUsage: {
        invalidatesTags: (resp) =>
            resp?.id
                ? [
                      { type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST },
                      { type: TagTypes.DataProduct, id: resp?.id },
                  ]
                : [{ type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST }],
    },
    getDataProductEventHistory: {
        providesTags: (_, __, id) => [{ type: TagTypes.History, id: id }],
    },
    requestInputPortsForDataProduct: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: arg.id },
            ...arg.requestInputPortsForDataProductRequest.output_ports.map((op) => ({
                type: TagTypes.OutputPort,
                id: op.output_port_id,
            })),
            ...arg.requestInputPortsForDataProductRequest.output_ports.map((op) => ({
                type: TagTypes.History,
                id: op.output_port_id,
            })),
            ...arg.requestInputPortsForDataProductRequest.output_ports.map((op) => ({
                type: TagTypes.OutputPortInputPorts,
                id: op.output_port_id,
            })),
            { type: TagTypes.History, id: arg.id },
            { type: TagTypes.DataProductInputPorts, id: arg.id },
            ...requestListTags,
        ],
    },
    revokeInputPortForDataProduct: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: arg.id },
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.id },
            { type: TagTypes.DataProductInputPorts, id: arg.id },
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
            ...requestListTags,
        ],
    },
    cancelInputPortForDataProduct: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: arg.id },
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.id },
            { type: TagTypes.DataProductInputPorts, id: arg.id },
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
            ...requestListTags,
        ],
    },
    renewInputPortForDataProduct: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: arg.id },
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.id },
            { type: TagTypes.DataProductInputPorts, id: arg.id },
            { type: TagTypes.OutputPortInputPorts, id: arg.outputPortId },
            ...requestListTags,
        ],
    },
    getDataProductInputPorts: {
        providesTags: (_, __, id) => [{ type: TagTypes.DataProductInputPorts, id }],
    },
    getDataProductRolledUpTags: {
        providesTags: (_, __, id) => [{ type: TagTypes.DataProductRolledUpTags, id }],
    },
    getDataProductSettings: {
        providesTags: (_, __, id) => [{ type: TagTypes.DataProductSettings, id }],
    },
    setValueForDataProduct: {
        invalidatesTags: (_, __, arg) => [{ type: TagTypes.DataProductSettings, id: arg.id }],
    },
} satisfies EndpointDefinitions;
