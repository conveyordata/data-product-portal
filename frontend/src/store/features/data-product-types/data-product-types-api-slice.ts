import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import {
    DataProductTypeContract,
    DataProductTypeCreateRequest,
    DataProductTypeCreateResponse,
} from '@/types/data-product-type';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';

export const dataProductTypeTags: string[] = [TagTypes.DataProductType];
export const dataProductTypesApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductTypeTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getAllDataProductTypes: builder.query<DataProductTypeContract[], void>({
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
                        : [{ type: TagTypes.DataProductType, id: STATIC_TAG_ID.LIST }],
            }),
            createDataProductType: builder.mutation<DataProductTypeCreateResponse, DataProductTypeCreateRequest>({
                query: (request) => ({
                    url: ApiUrl.DataProductType,
                    method: 'POST',
                    data: request,
                }),
                invalidatesTags: [{ type: TagTypes.DataProductType, id: STATIC_TAG_ID.LIST }],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useCreateDataProductTypeMutation, useGetAllDataProductTypesQuery } = dataProductTypesApiSlice;
