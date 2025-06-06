import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { DataOutputsGetContract } from '@/types/data-output';
import {
    DataProductContract,
    DataProductCreate,
    DataProductCreateResponse,
    DataProductDatasetAccessRequest,
    DataProductDatasetAccessResponse,
    DataProductDatasetRemoveRequest,
    DataProductDatasetRemoveResponse,
    DataProductGetConveyorUrlRequest,
    DataProductGetConveyorUrlResponse,
    DataProductGetDatabricksWorkspaceUrlRequest,
    DataProductGetDatabricksWorkspaceUrlResponse,
    DataProductGetSignInUrlRequest,
    DataProductGetSignInUrlResponse,
    DataProductGetSnowflakeUrlRequest,
    DataProductGetSnowflakeUrlResponse,
    DataProductUpdateRequest,
    DataProductUpdateResponse,
    DataProductsGetContract,
} from '@/types/data-product';
import { GraphContract } from '@/types/graph/graph-contract';
import {
    NamespaceLengthLimitsResponse,
    NamespaceSuggestionResponse,
    NamespaceValidationResponse,
} from '@/types/namespace/namespace';

export const dataProductTags: string[] = [
    TagTypes.DataProduct,
    TagTypes.UserDataProducts,
    TagTypes.Dataset,
    TagTypes.UserDatasets,
];

export const dataProductsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: dataProductTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllDataProducts: builder.query<DataProductsGetContract, void>({
            query: () => ({
                url: ApiUrl.DataProducts,
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.DataProduct as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ id }) => ({ type: TagTypes.DataProduct as const, id })),
                      ]
                    : [{ type: TagTypes.DataProduct as const, id: STATIC_TAG_ID.LIST }],
        }),
        getUserDataProducts: builder.query<DataProductsGetContract, string>({
            query: (userId) => ({
                url: buildUrl(ApiUrl.UserDataProducts, { userId }),
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST }],
        }),
        getDataProductDataOutputs: builder.query<DataOutputsGetContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataProductsDataOutput, { dataProductId: id }),
                method: 'GET',
            }),
        }),
        getDataProductById: builder.query<DataProductContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataProductGet, { dataProductId: id }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [
                { type: TagTypes.DataProduct as const, id },
                { type: TagTypes.DataOutput as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        getDataProductGraphData: builder.query<GraphContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataProductGraph, { dataProductId: id }),
                method: 'GET',
            }),
        }),
        createDataProduct: builder.mutation<DataProductCreateResponse, DataProductCreate>({
            query: (dataProduct) => ({
                url: ApiUrl.DataProducts,
                method: 'POST',
                data: dataProduct,
            }),
            invalidatesTags: [
                { type: TagTypes.DataProduct as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        updateDataProduct: builder.mutation<
            DataProductUpdateResponse,
            {
                dataProduct: DataProductUpdateRequest;
                data_product_id: string;
            }
        >({
            query: ({ dataProduct, data_product_id }) => ({
                url: buildUrl(ApiUrl.DataProductGet, { dataProductId: data_product_id }),
                method: 'PUT',
                data: dataProduct,
            }),
            invalidatesTags: (_, __, { data_product_id }) => [
                { type: TagTypes.DataProduct as const, id: data_product_id },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.Dataset as const },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        removeDataProduct: builder.mutation<void, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataProductGet, { dataProductId: id }),
                method: 'DELETE',
            }),
            invalidatesTags: [
                { type: TagTypes.DataProduct as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        getDataProductSignInUrl: builder.mutation<DataProductGetSignInUrlResponse, DataProductGetSignInUrlRequest>({
            query: ({ id, environment }) => ({
                url: buildUrl(ApiUrl.DataProductSignInUrl, { dataProductId: id }),
                method: 'GET',
                params: { environment },
            }),
        }),
        getDataProductConveyorIDEUrl: builder.mutation<
            DataProductGetConveyorUrlResponse,
            DataProductGetConveyorUrlRequest
        >({
            query: ({ id }) => ({
                url: buildUrl(ApiUrl.DataProductConveyorIdeUrl, { dataProductId: id }),
                method: 'GET',
            }),
        }),
        getDataProductDatabricksWorkspaceUrl: builder.mutation<
            DataProductGetDatabricksWorkspaceUrlResponse,
            DataProductGetDatabricksWorkspaceUrlRequest
        >({
            query: ({ id, environment }) => ({
                url: buildUrl(ApiUrl.DataProductDatabricksWorkspaceUrl, { dataProductId: id }),
                method: 'GET',
                params: { environment },
            }),
        }),
        getDataProductSnowflakeUrl: builder.mutation<
            DataProductGetSnowflakeUrlResponse,
            DataProductGetSnowflakeUrlRequest
        >({
            query: ({ id, environment }) => ({
                url: buildUrl(ApiUrl.DataProductSnowflakeUrl, { dataProductId: id }),
                method: 'GET',
                params: { environment },
            }),
        }),
        requestDatasetAccessForDataProduct: builder.mutation<
            DataProductDatasetAccessResponse,
            DataProductDatasetAccessRequest
        >({
            query: ({ dataProductId, datasetId }) => ({
                url: buildUrl(ApiUrl.DataProductDataset, { dataProductId, datasetId }),
                method: 'POST',
            }),
            invalidatesTags: (_, _error, arg) => [
                { type: TagTypes.DataProduct as const, id: arg.dataProductId },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.Dataset as const, id: arg.datasetId },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        removeDatasetFromDataProduct: builder.mutation<
            DataProductDatasetRemoveResponse,
            DataProductDatasetRemoveRequest
        >({
            query: ({ dataProductId, datasetId }) => ({
                url: buildUrl(ApiUrl.DataProductDataset, { dataProductId, datasetId }),
                method: 'DELETE',
            }),
            invalidatesTags: (_, _error, arg) => [
                { type: TagTypes.DataProduct as const, id: arg.dataProductId },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.Dataset as const, id: arg.datasetId },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        updateDataProductAbout: builder.mutation<
            void,
            {
                dataProductId: string;
                about: string;
            }
        >({
            query: ({ dataProductId, about }) => ({
                url: buildUrl(ApiUrl.DataProductAbout, { dataProductId }),
                method: 'PUT',
                data: { about },
            }),
            onQueryStarted: async ({ dataProductId, about }, { dispatch, queryFulfilled }) => {
                const patchResult = dispatch(
                    dataProductsApiSlice.util.updateQueryData(
                        'getDataProductById',
                        dataProductId as string,
                        (draft) => {
                            draft.about = about;
                        },
                    ),
                );

                queryFulfilled.catch(patchResult.undo);
            },
            invalidatesTags: (_, __, { dataProductId }) => [{ type: TagTypes.DataProduct as const, id: dataProductId }],
        }),
        validateDataProductNamespace: builder.query<NamespaceValidationResponse, string>({
            query: (namespace) => ({
                url: ApiUrl.DataProductNamespaceValidation,
                method: 'GET',
                params: { namespace },
            }),
        }),
        getDataProductNamespaceSuggestion: builder.query<NamespaceSuggestionResponse, string>({
            query: (name) => ({
                url: ApiUrl.DataProductNamespaceSuggestion,
                method: 'GET',
                params: { name },
            }),
        }),
        getDataProductNamespaceLengthLimits: builder.query<NamespaceLengthLimitsResponse, void>({
            query: () => ({
                url: ApiUrl.DataProductNamespaceLimits,
                method: 'GET',
            }),
        }),
        validateDataOutputNamespace: builder.query<
            NamespaceValidationResponse,
            { dataProductId: string; namespace: string }
        >({
            query: ({ dataProductId, namespace }) => ({
                url: buildUrl(ApiUrl.DataProductDataOutputNamespaceValidation, { dataProductId }),
                method: 'GET',
                params: { namespace },
            }),
        }),
    }),
    overrideExisting: false,
});

export const {
    useCreateDataProductMutation,
    useUpdateDataProductMutation,
    useGetDataProductByIdQuery,
    useGetAllDataProductsQuery,
    useGetDataProductSignInUrlMutation,
    useGetDataProductConveyorIDEUrlMutation,
    useRemoveDataProductMutation,
    useRemoveDatasetFromDataProductMutation,
    useRequestDatasetAccessForDataProductMutation,
    useUpdateDataProductAboutMutation,
    useGetUserDataProductsQuery,
    useGetDataProductDataOutputsQuery,
    useGetDataProductGraphDataQuery,
    useGetDataProductDatabricksWorkspaceUrlMutation,
    useGetDataProductSnowflakeUrlMutation,
    useLazyGetDataProductNamespaceSuggestionQuery,
    useLazyValidateDataProductNamespaceQuery,
    useGetDataProductNamespaceLengthLimitsQuery,
    useLazyValidateDataOutputNamespaceQuery,
} = dataProductsApiSlice;
