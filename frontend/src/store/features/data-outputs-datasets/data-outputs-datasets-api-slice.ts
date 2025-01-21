import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { DataOutputDatasetContract, DataOutputDatasetLinkRequest } from '@/types/data-output-dataset';

export const dataOutputsDatasetsTags: string[] = [
    TagTypes.DataOutput,
    TagTypes.Dataset,
    TagTypes.UserDataProducts,
    TagTypes.UserDatasets,
    TagTypes.DataProduct,
    TagTypes.UserDataOutputs,
];
export const dataOutputsDatasetsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataOutputsDatasetsTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            approveDataOutputLink: builder.mutation<void, DataOutputDatasetLinkRequest>({
                query: ({ id }) => ({
                    url: buildUrl(ApiUrl.DataOutputDatasetLinkApprove, { datasetLinkId: id }),
                    method: 'POST',
                    data: {
                        id,
                    },
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataOutput as const, id: arg.data_output_id },
                    { type: TagTypes.Dataset as const, id: arg.dataset_id },
                    { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            rejectDataOutputLink: builder.mutation<void, DataOutputDatasetLinkRequest>({
                query: ({ id }) => ({
                    url: buildUrl(ApiUrl.DataOutputDatasetLinkReject, { datasetLinkId: id }),
                    method: 'POST',
                    data: {
                        id,
                    },
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                    //{ type: TagTypes.DataProduct as const, id: STATIC_TAG_ID.LIST} ,
                    //{ type: TagTypes.DataOutput as const, id: arg.data_output_id },
                    { type: TagTypes.Dataset as const, id: arg.dataset_id },
                    { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
                    //{ type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                    //{ type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                    //{ type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            removeDataOutputDatasetLink: builder.mutation<
                void,
                {
                    datasetId: string;
                    dataOutputId: string;
                    datasetLinkId: string;
                }
            >({
                query: ({ datasetLinkId }) => ({
                    url: buildUrl(ApiUrl.DataOutputDatasetLinkRemove, { datasetLinkId }),
                    method: 'POST',
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataOutput as const, id: arg.dataOutputId },
                    { type: TagTypes.DataProduct as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.Dataset as const, id: arg.datasetId },
                    { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            getDataOutputDatasetPendingActions: builder.query<DataOutputDatasetContract[], void>({
                query: () => ({
                    url: buildUrl(ApiUrl.DataOutputDatasetPendingActions, { }),
                    method: 'GET',
                }),
                providesTags: (_, __) => [
                    { type: TagTypes.UserDataOutputs as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useApproveDataOutputLinkMutation,
    useRejectDataOutputLinkMutation,
    useRemoveDataOutputDatasetLinkMutation,
    useGetDataOutputDatasetPendingActionsQuery,
} = dataOutputsDatasetsApiSlice;
