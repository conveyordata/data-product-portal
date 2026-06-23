import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

export const dataProductTags = {
    //Data products api
    getDataProducts: {
        providesTags: [{ type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST }],
    },
    getDataProduct: {
        providesTags: (response) => (response?.id ? [{ type: TagTypes.DataProduct, id: response?.id }] : []),
    },
    createDataProduct: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST },
            ...(arg.input_ports?.output_ports?.map((id) => ({
                type: TagTypes.OutputPort,
                id,
            })) ?? []),
            ...(arg.input_ports?.output_ports?.map((id) => ({ type: TagTypes.History, id })) ?? []),
            { type: TagTypes.MyRequests },
        ],
    },
    removeDataProduct: {
        invalidatesTags: (_, __, id) => [
            { type: TagTypes.DataProduct, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.DataProduct, id },
            { type: TagTypes.DataProductOutputPorts, id },
        ],
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
            ...arg.requestInputPortsForDataProductRequest.output_ports.map((id) => ({
                type: TagTypes.OutputPort,
                id,
            })),
            ...arg.requestInputPortsForDataProductRequest.output_ports.map((id) => ({ type: TagTypes.History, id })),
            { type: TagTypes.History, id: arg.id },
            { type: TagTypes.DataProductInputPorts, id: arg.id },
            { type: TagTypes.MyRequests },
        ],
    },
    unlinkInputPortFromDataProduct: {
        invalidatesTags: (_, __, arg) => [
            { type: TagTypes.DataProduct, id: arg.id },
            { type: TagTypes.OutputPort, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.outputPortId },
            { type: TagTypes.History, id: arg.id },
            { type: TagTypes.DataProductInputPorts, id: arg.id },
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
