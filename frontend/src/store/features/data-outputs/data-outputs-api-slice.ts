import { ApiUrl, buildUrl } from '@/api/api-urls';
import {
    DataOutputContract,
    DataOutputCreate,
    DataOutputCreateResponse,
    DataOutputDatasetAccessRequest,
    DataOutputDatasetAccessResponse,
    DataOutputDatasetRemoveRequest,
    DataOutputDatasetRemoveResponse,
} from '@/types/data-output';
import { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract';
import { DataOutputUpdateRequest, DataOutputUpdateResponse } from '@/types/data-output/data-output-update.contract';
import { EventContract } from '@/types/events/event.contract';
import { GraphContract } from '@/types/graph/graph-contract';

import { baseApiSlice } from '../api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '../api/tag-types';
import { datasetsApiSlice } from '../datasets/datasets-api-slice';

export const dataOutputTags: string[] = [
    TagTypes.DataOutput,
    TagTypes.UserDataProducts,
    TagTypes.DataProduct,
    TagTypes.UserDatasets,
    TagTypes.UserDataOutputs,
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
        createDataOutput: builder.mutation<DataOutputCreateResponse, DataOutputCreate>({
            query: (dataOutput) => ({
                url: ApiUrl.DataOutputs,
                method: 'POST',
                data: dataOutput,
            }),
            invalidatesTags: (_, _error, arg) => [
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const, id: arg.owner_id },
                { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
            ],
            // invalidatesTags: (_, _error, arg) => [
            //
            //     { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
            //     { type: TagTypes.DataOutput as const, id: arg.dataOutputId },
            //     { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            // ],
        }),
        getDataOutputHistory: builder.query<EventContract[], string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataOutputHistory, { dataOutputId: id }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [
                { type: TagTypes.DataOutput as const, id: id },
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
            ],
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
            ],
        }),
        removeDataOutput: builder.mutation<void, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataOutputGet, { dataOutputId: id }),
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST }],
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
            invalidatesTags: () => [
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
            ],
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
    useGetDataOutputHistoryQuery,
} = dataOutputsApiSlice;
