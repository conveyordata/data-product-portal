import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import {
    DataProductTypeCreateRequest,
    DataProductTypeCreateResponse,
} from '@/types/data-product-type';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { DataProductLifeCycle } from '@/types/data-product/data-product-contract';

export const dataProductLifecycleTags: string[] = [TagTypes.DataProductLifecycle];
export const dataProductLifecyclesApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductLifecycleTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getAllDataProductLifecycles: builder.query<DataProductLifeCycle[], void>({
                query: () => ({
                    url: ApiUrl.DataProductLifecycle,
                    method: 'GET',
                }),
                providesTags: (result = []) =>
                    result
                        ? [
                              { type: TagTypes.DataProductLifecycle as const, id: STATIC_TAG_ID.LIST },
                              ...result.map(({ id }) => ({ type: TagTypes.DataProductLifecycle as const, id })),
                          ]
                        : [{ type: TagTypes.DataProductLifecycle, id: STATIC_TAG_ID.LIST }],
            }),
            // TODO Fix proper typing
            createDataProductLifecycle: builder.mutation<DataProductTypeCreateResponse, DataProductTypeCreateRequest>({
                query: (request) => ({
                    url: ApiUrl.DataProductLifecycle,
                    method: 'POST',
                    data: request,
                }),
                invalidatesTags: [{ type: TagTypes.DataProductLifecycle, id: STATIC_TAG_ID.LIST }],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useCreateDataProductLifecycleMutation, useGetAllDataProductLifecyclesQuery } = dataProductLifecyclesApiSlice;
