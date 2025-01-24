import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { DataProductDatasetContract, DataProductDatasetLinkRequest } from '@/types/data-product-dataset';

export const dataProductsDatasetsTags: string[] = [
    TagTypes.DataProduct,
    TagTypes.Dataset,
    TagTypes.UserDataProducts,
    TagTypes.UserDatasets,
];
export const dataProductsDatasetsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductsDatasetsTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            approveDataProductLink: builder.mutation<void, DataProductDatasetLinkRequest>({
                query: ({ id }) => ({
                    url: buildUrl(ApiUrl.DataProductDatasetLinkApprove, { datasetLinkId: id }),
                    method: 'POST',
                    data: {
                        id,
                    },
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.DataProduct as const, id: arg.data_product_id },
                    { type: TagTypes.Dataset as const, id: arg.dataset_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            rejectDataProductLink: builder.mutation<void, DataProductDatasetLinkRequest>({
                query: ({ id }) => ({
                    url: buildUrl(ApiUrl.DataProductDatasetLinkReject, { datasetLinkId: id }),
                    method: 'POST',
                    data: {
                        id,
                    },
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.DataProduct as const, id: arg.data_product_id },
                    { type: TagTypes.Dataset as const, id: arg.dataset_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            removeDataProductDatasetLink: builder.mutation<
                void,
                {
                    datasetId: string;
                    dataProductId: string;
                    datasetLinkId: string;
                }
            >({
                query: ({ datasetLinkId }) => ({
                    url: buildUrl(ApiUrl.DataProductDatasetLinkRemove, { datasetLinkId }),
                    method: 'POST',
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.DataProduct as const, id: arg.dataProductId },
                    { type: TagTypes.Dataset as const, id: arg.datasetId },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            getDataProductDatasetPendingActions: builder.query<DataProductDatasetContract[], void>({
                query: () => ({
                    url: buildUrl(ApiUrl.DataProductDatasetPendingActions, {}),
                    method: 'GET',
                }),
                providesTags: (_, __) => [
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useApproveDataProductLinkMutation,
    useRejectDataProductLinkMutation,
    useRemoveDataProductDatasetLinkMutation,
    useGetDataProductDatasetPendingActionsQuery,
} = dataProductsDatasetsApiSlice;
