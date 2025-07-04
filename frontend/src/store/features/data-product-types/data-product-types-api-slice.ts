import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type {
    DataProductTypeCreateRequest,
    DataProductTypeCreateResponse,
    DataProductTypeGetContract,
    DataProductTypesGetContract,
} from '@/types/data-product-type';

export const dataProductTypeTags: string[] = [
    TagTypes.DataProductType,
    TagTypes.DataProduct,
    TagTypes.UserDataProducts,
];
export const dataProductTypesApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductTypeTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getAllDataProductTypes: builder.query<DataProductTypesGetContract[], void>({
                query: () => ({
                    url: ApiUrl.DataProductType,
                    method: 'GET',
                }),
                providesTags: (result = []) =>
                    result
                        ? [
                              { type: TagTypes.DataProductType as const, id: STATIC_TAG_ID.LIST },
                              ...result.map(({ id }) => ({ type: TagTypes.DataProductType as const, id })),
                          ]
                        : [{ type: TagTypes.DataProductType as const, id: STATIC_TAG_ID.LIST }],
            }),
            getDataProductType: builder.query<DataProductTypeGetContract, string>({
                query: (dataProductTypeId) => ({
                    url: buildUrl(ApiUrl.DataProductTypeId, { dataProductTypeId }),
                    method: 'GET',
                }),
                providesTags: (_, __, id) => [{ type: TagTypes.DataProductType as const, id }],
            }),
            createDataProductType: builder.mutation<DataProductTypeCreateResponse, DataProductTypeCreateRequest>({
                query: (request) => ({
                    url: ApiUrl.DataProductType,
                    method: 'POST',
                    data: request,
                }),
                invalidatesTags: [{ type: TagTypes.DataProductType as const, id: STATIC_TAG_ID.LIST }],
            }),
            updateDataProductType: builder.mutation<
                DataProductTypeCreateResponse,
                { dataProductType: DataProductTypeCreateRequest; dataProductTypeId: string }
            >({
                query: ({ dataProductType, dataProductTypeId }) => ({
                    url: buildUrl(ApiUrl.DataProductTypeId, { dataProductTypeId }),
                    method: 'PUT',
                    data: dataProductType,
                }),
                invalidatesTags: [
                    { type: TagTypes.DataProductType as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct as const },
                    { type: TagTypes.UserDataProducts as const },
                ],
            }),
            removeDataProductType: builder.mutation<void, string>({
                query: (dataProductTypeId) => ({
                    url: buildUrl(ApiUrl.DataProductTypeId, { dataProductTypeId }),
                    method: 'DELETE',
                }),
                invalidatesTags: [{ type: TagTypes.DataProductType as const, id: STATIC_TAG_ID.LIST }],
            }),
            migrateDataProductType: builder.mutation<void, { fromId: string; toId: string }>({
                query: ({ fromId, toId }) => ({
                    url: buildUrl(ApiUrl.DataProductTypeMigrate, { fromId, toId }),
                    method: 'PUT',
                }),
                invalidatesTags: (_, __, { fromId, toId }) => [
                    { type: TagTypes.DataProductType as const, id: fromId },
                    { type: TagTypes.DataProductType as const, id: toId },
                    { type: TagTypes.DataProduct as const },
                    { type: TagTypes.UserDataProducts as const },
                ],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useCreateDataProductTypeMutation,
    useGetAllDataProductTypesQuery,
    useUpdateDataProductTypeMutation,
    useRemoveDataProductTypeMutation,
    useGetDataProductTypeQuery,
    useMigrateDataProductTypeMutation,
} = dataProductTypesApiSlice;
