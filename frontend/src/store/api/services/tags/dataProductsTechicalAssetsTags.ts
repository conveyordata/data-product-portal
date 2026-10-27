import type { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

type EndpointDefinitions = Parameters<typeof api.enhanceEndpoints>[0]['endpoints'];

const invalidateTagsTechnicalAsset = (
    _: unknown,
    __: unknown,
    { dataProductId, id }: { dataProductId: string; id: string },
) => invalidateTechnicalAsset(dataProductId, id);

const invalidateTechnicalAsset = (dataProductId: string, technicalAssetId: string) => [
    {
        type: TagTypes.TechnicalAsset,
        id: technicalAssetId,
    },
    {
        type: TagTypes.TechnicalAsset,
        id: STATIC_TAG_ID.LIST,
    },
    {
        type: TagTypes.DataProductTechnicalAssets,
        id: dataProductId,
    },
    {
        type: TagTypes.History,
        id: technicalAssetId,
    },
];

const invalidateTechnicalAssetOutputPort = (dataProductId: string, outputPortId: string) => [
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
];

export const dataProductTechnicalAssetsTags = {
    getDataProductTechnicalAssets: {
        providesTags: (_, __, id) => [
            {
                type: TagTypes.DataProductTechnicalAssets,
                id: id,
            },
        ],
    },
    approveOutputPortTechnicalAssetLink: {
        invalidatesTags: (
            _,
            __,
            {
                dataProductId,
                outputPortId,
                approveLinkBetweenTechnicalAssetAndOutputPortRequest: { technical_asset_id },
            },
        ) => [
            ...invalidateTechnicalAssetOutputPort(dataProductId, outputPortId),
            ...invalidateTechnicalAsset(dataProductId, technical_asset_id),
            { type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.Graph },
        ],
    },
    denyOutputPortTechnicalAssetLink: {
        invalidatesTags: (
            _,
            __,
            { dataProductId, outputPortId, denyLinkBetweenTechnicalAssetAndOutputPortRequest: { technical_asset_id } },
        ) => [
            ...invalidateTechnicalAssetOutputPort(dataProductId, outputPortId),
            ...invalidateTechnicalAsset(dataProductId, technical_asset_id),
            { type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.Graph },
        ],
    },
    linkOutputPortToTechnicalAsset: {
        extraOptions: {
            suppressErrorToast: true,
        },
        invalidatesTags: (
            _,
            __,
            { dataProductId, outputPortId, linkTechnicalAssetToOutputPortRequest: { technical_asset_id } },
        ) => [
            ...invalidateTechnicalAssetOutputPort(dataProductId, outputPortId),
            ...invalidateTechnicalAsset(dataProductId, technical_asset_id),
            { type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.Graph },
        ],
    },
    unlinkOutputPortFromTechnicalAsset: {
        invalidatesTags: (
            _,
            __,
            { dataProductId, outputPortId, unLinkTechnicalAssetToOutputPortRequest: { technical_asset_id } },
        ) => [
            ...invalidateTechnicalAssetOutputPort(dataProductId, outputPortId),
            ...invalidateTechnicalAsset(dataProductId, technical_asset_id),
            { type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST },
            { type: TagTypes.Graph },
        ],
    },
    createTechnicalAsset: {
        invalidatesTags: (_, __, { dataProductId }) => [
            {
                type: TagTypes.DataProductTechnicalAssets,
                id: dataProductId,
            },
            { type: TagTypes.Graph },
        ],
    },
    getTechnicalAsset: {
        providesTags: (_, __, { id }) => [
            {
                type: TagTypes.TechnicalAsset,
                id,
            },
        ],
    },
    removeTechnicalAsset: {
        invalidatesTags: (_, __, arg) => [
            ...invalidateTagsTechnicalAsset(_, __, arg),
            { type: TagTypes.Graph, id: STATIC_TAG_ID.LIST },
        ],
    },
    updateTechnicalAsset: {
        invalidatesTags: (_, __, arg) => [...invalidateTagsTechnicalAsset(_, __, arg), { type: TagTypes.Graph }],
    },
    getTechnicalAssetEventHistory: {
        providesTags: (_, __, { id }) => [
            {
                type: TagTypes.History,
                id: id,
            },
        ],
    },
    updateTechnicalAssetStatus: {
        invalidatesTags: invalidateTagsTechnicalAsset,
    },
    getTechnicalAssetGraphData: {
        providesTags: (_, __, { id }) => [{ type: TagTypes.Graph, id }],
    },
} satisfies EndpointDefinitions;
