import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
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
    DataProductGetSignInUrlRequest,
    DataProductGetSignInUrlResponse,
    DataProductsGetContract,
    DataProductUpdateRequest,
    DataProductUpdateResponse,
} from '@/types/data-product';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { datasetsApiSlice } from '@/store/features/datasets/datasets-api-slice.ts';

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
        getDataProductById: builder.query<DataProductContract, string>({
            query: (id) => ({
                url: buildUrl(ApiUrl.DataProductGet, { dataProductId: id }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [{ type: TagTypes.DataProduct as const, id }],
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
        getDataProductConveyorNotebookUrl: builder.mutation<
            DataProductGetConveyorUrlResponse,
            DataProductGetConveyorUrlRequest
        >({
            query: ({ id }) => ({
                url: buildUrl(ApiUrl.DataProductConveyorNotebookUrl, { dataProductId: id }),
                method: 'GET',
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
            onQueryStarted: async ({ dataProductId, datasetId }, { dispatch, queryFulfilled }) => {
                const patchDataProductResult = dispatch(
                    dataProductsApiSlice.util.updateQueryData(
                        'getDataProductById',
                        dataProductId as string,
                        (draft) => {
                            draft.dataset_links = draft.dataset_links.filter((d) => d.dataset_id !== datasetId);
                        },
                    ),
                );
                const patchDatasetResult = dispatch(
                    datasetsApiSlice.util.updateQueryData('getDatasetById', datasetId as string, (draft) => {
                        draft.data_product_links = draft.data_product_links.filter(
                            (p) => p.data_product.id !== dataProductId,
                        );
                    }),
                );

                queryFulfilled.catch(patchDataProductResult.undo);
                queryFulfilled.catch(patchDatasetResult.undo);
            },
            invalidatesTags: () => [
                { type: TagTypes.DataProduct as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.Dataset as const, id: STATIC_TAG_ID.LIST },
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
    useGetDataProductConveyorNotebookUrlMutation,
    useGetUserDataProductsQuery,
} = dataProductsApiSlice;
