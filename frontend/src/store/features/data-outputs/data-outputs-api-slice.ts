import { ApiUrl, buildUrl } from '@/api/api-urls';
import type {
    DataOutputContract,
    DataOutputCreate,
    DataOutputCreateResponse,
    DataOutputDatasetAccessRequest,
    DataOutputDatasetAccessResponse,
    DataOutputDatasetRemoveRequest,
    DataOutputDatasetRemoveResponse,
    DataOutputResultStringRequest,
    OutputConfig,
} from '@/types/data-output';
import type { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract';
import type {
    DataOutputUpdateRequest,
    DataOutputUpdateResponse,
} from '@/types/data-output/data-output-update.contract';
import type { DataPlatform } from '@/types/data-platform';
import type { EventContract } from '@/types/events/event.contract';
import type { GraphContract } from '@/types/graph/graph-contract';
import type { NamespaceLengthLimitsResponse, NamespaceSuggestionResponse } from '@/types/namespace/namespace';
import { baseApiSlice } from '../api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '../api/tag-types';
import { datasetsApiSlice } from '../datasets/datasets-api-slice';

export const dataOutputTags: string[] = [
    TagTypes.DataOutput,
    TagTypes.UserDataProducts,
    TagTypes.DataProduct,
    TagTypes.UserDatasets,
    TagTypes.UserDataOutputs,
    TagTypes.History,
];

export const dataOutputsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: dataOutputTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllDataOutputs: builder.query<DataOutputsGetContract, void>({
            query: () => ({
                url: ApiUrl.DataOutputs,
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST }],
        }),
        getDataOutputConfig: builder.query<string, DataPlatform>({
            query: (type) => ({
                url: ApiUrl.DataOutputConfig,
                params: { type },
                method: 'GET',
            }),
        }),
        getDataOutputById: builder.query<DataOutputContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataOutputGet, { dataOutputId: id }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [
                { type: TagTypes.DataProduct as const, id },
                { type: TagTypes.DataOutput as const, id },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        createDataOutput: builder.mutation<DataOutputCreateResponse, { id: string; dataOutput: DataOutputCreate }>({
            query: ({ id, dataOutput }) => ({
                url: buildUrl(ApiUrl.DataProductOutputCreate, { dataProductId: id }),
                method: 'POST',
                data: dataOutput,
            }),
            invalidatesTags: (_, _error, arg) => [
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const, id: arg.id },
                { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.History as const, id: arg.id },
            ],
        }),
        getDataOutputHistory: builder.query<EventContract[], string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataOutputHistory, { dataOutputId: id }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [{ type: TagTypes.History as const, id: id }],
        }),
        getDataOutputGraphData: builder.query<GraphContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataOutputGraph, { dataOutputId: id }),
                method: 'GET',
            }),
        }),
        updateDataOutput: builder.mutation<
            DataOutputUpdateResponse,
            {
                dataOutput: DataOutputUpdateRequest;
                dataOutputId: string;
            }
        >({
            query: ({ dataOutput, dataOutputId }) => ({
                url: buildUrl(ApiUrl.DataOutputGet, { dataOutputId: dataOutputId }),
                method: 'PUT',
                data: dataOutput,
            }),
            invalidatesTags: (_, __, { dataOutputId }) => [
                { type: TagTypes.DataOutput as const, id: dataOutputId },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.Dataset as const },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.History as const, id: dataOutputId },
            ],
        }),
        requestDatasetAccessForDataOutput: builder.mutation<
            DataOutputDatasetAccessResponse,
            DataOutputDatasetAccessRequest
        >({
            query: ({ dataOutputId, datasetId }) => ({
                url: buildUrl(ApiUrl.DataOutputsDataset, { dataOutputId, datasetId }),
                method: 'POST',
            }),
            invalidatesTags: (_, _error, arg) => [
                //{ type: TagTypes.DataOutput as const, id: arg.dataOutputId },
                // This should refresh the owner of data output only. Instead, super inefficient, it refreshes all of the data products?
                // Or maybe it's fine? It seems fine lol
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                //{ type: TagTypes.DataProduct as const, id: dataOutputsApiSlice.util.getDataOutputById(arg.data)},
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.Dataset as const, id: arg.datasetId },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.History as const, id: arg.dataOutputId },
                { type: TagTypes.History as const, id: arg.datasetId },
            ],
        }),
        removeDataOutput: builder.mutation<void, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataOutputGet, { dataOutputId: id }),
                method: 'DELETE',
            }),
            invalidatesTags: (_, _error, arg) => [
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataOutput as const, id: arg },
                { type: TagTypes.History as const, id: arg },
            ],
        }),
        removeDatasetFromDataOutput: builder.mutation<DataOutputDatasetRemoveResponse, DataOutputDatasetRemoveRequest>({
            query: ({ dataOutputId, datasetId }) => ({
                url: buildUrl(ApiUrl.DataOutputsDataset, { dataOutputId, datasetId }),
                method: 'DELETE',
            }),
            onQueryStarted: async ({ dataOutputId, datasetId }, { dispatch, queryFulfilled }) => {
                const patchDataProductResult = dispatch(
                    dataOutputsApiSlice.util.updateQueryData('getDataOutputById', dataOutputId as string, (draft) => {
                        draft.dataset_links = draft.dataset_links.filter((d) => d.dataset_id !== datasetId);
                    }),
                );
                const patchDatasetResult = dispatch(
                    datasetsApiSlice.util.updateQueryData('getDatasetById', datasetId as string, (draft) => {
                        draft.data_product_links = draft.data_product_links.filter(
                            (p) => p.data_product.id !== dataOutputId,
                        );
                    }),
                );

                queryFulfilled.catch(patchDataProductResult.undo);
                queryFulfilled.catch(patchDatasetResult.undo);
            },
            invalidatesTags: (_, _error, arg) => [
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.History as const, id: arg.dataOutputId },
                { type: TagTypes.History as const, id: arg.datasetId },
            ],
        }),
        getDataOutputNamespaceSuggestion: builder.query<NamespaceSuggestionResponse, string>({
            query: (name) => ({
                url: ApiUrl.DataOutputNamespaceSuggestion,
                method: 'GET',
                params: { name },
            }),
        }),
        getDataOutputNamespaceLengthLimits: builder.query<NamespaceLengthLimitsResponse, void>({
            query: () => ({
                url: ApiUrl.DataOutputNamespaceLimits,
                method: 'GET',
            }),
        }),
        getDataOutputResultString: builder.query<string, DataOutputResultStringRequest>({
            query: (data) => ({
                url: ApiUrl.DataOutputResultString,
                method: 'POST',
                data,
            }),
        }),
    }),

    overrideExisting: false,
});

export const {
    useGetAllDataOutputsQuery,
    useGetDataOutputByIdQuery,
    useCreateDataOutputMutation,
    useRemoveDatasetFromDataOutputMutation,
    useUpdateDataOutputMutation,
    useRemoveDataOutputMutation,
    useRequestDatasetAccessForDataOutputMutation,
    useGetDataOutputGraphDataQuery,
    useGetDataOutputConfigQuery,
    useGetDataOutputHistoryQuery,
    useGetDataOutputNamespaceLengthLimitsQuery,
    useLazyGetDataOutputNamespaceSuggestionQuery,
    useLazyGetDataOutputResultStringQuery,
} = dataOutputsApiSlice;
