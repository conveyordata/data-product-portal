import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

const invalidateOutputPortAsInputPort = (
    dataProductId: string,
    outputPortId: string,
    consumingDataProductId: string,
) => [
    {
        type: TagTypes.OutputPort,
        id: outputPortId,
    },
    {
        type: TagTypes.OutputPort,
        id: STATIC_TAG_ID.LIST,
    },
    {
        type: TagTypes.DataProductOutputPorts,
        id: dataProductId,
    },
    {
        type: TagTypes.History,
        id: outputPortId,
    },
    {
        type: TagTypes.History,
        id: dataProductId,
    },
    {
        type: TagTypes.History,
        id: consumingDataProductId,
    },
    {
        type: TagTypes.OutputPortInputPorts,
        id: outputPortId,
    },
    {
        type: TagTypes.DataProductInputPorts,
        id: consumingDataProductId,
    },
    {
        type: TagTypes.PendingAction,
        id: STATIC_TAG_ID.LIST,
    },
    {
        type: TagTypes.OutputPortInputPorts,
        outputPortId,
    },
];

export const dataProductsOutputPortsInputPortsTags = {
    getInputPortsForOutputPort: {
        providesTags: (_, __, { outputPortId }) => [
            {
                type: TagTypes.OutputPortInputPorts,
                outputPortId,
            },
        ],
    },
    approveOutputPortAsInputPort: {
        invalidatesTags: (
            _,
            __,
            {
                dataProductId,
                outputPortId,
                approveOutputPortAsInputPortRequest: { consuming_data_product_id: consumingDataProductId },
            },
        ) => invalidateOutputPortAsInputPort(dataProductId, outputPortId, consumingDataProductId),
    },
    denyOutputPortAsInputPort: {
        invalidatesTags: (
            _,
            __,
            {
                dataProductId,
                outputPortId,
                denyOutputPortAsInputPortRequest: { consuming_data_product_id: consumingDataProductId },
            },
        ) => invalidateOutputPortAsInputPort(dataProductId, outputPortId, consumingDataProductId),
    },
    removeOutputPortAsInputPort: {
        invalidatesTags: (
            _,
            __,
            {
                dataProductId,
                outputPortId,
                removeOutputPortAsInputPortRequest: { consuming_data_product_id: consumingDataProductId },
            },
        ) => invalidateOutputPortAsInputPort(dataProductId, outputPortId, consumingDataProductId),
    },
} satisfies EndpointDefinitions;
