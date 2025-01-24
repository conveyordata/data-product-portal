import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import {
    DataProductLifecycleCreateRequest,
    DataProductLifecycleCreateResponse,
    DataProductLifeCycleContract,
} from '@/types/data-product-lifecycle';

export const dataProductLifecycleTags: string[] = [TagTypes.DataProductLifecycle];
export const dataProductLifecyclesApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductLifecycleTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getAllDataProductLifecycles: builder.query<DataProductLifeCycleContract[], void>({
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
            createDataProductLifecycle: builder.mutation<
                DataProductLifecycleCreateResponse,
                DataProductLifecycleCreateRequest
            >({
                query: (request) => ({
                    url: ApiUrl.DataProductLifecycle,
                    method: 'POST',
                    data: request,
                }),
                invalidatesTags: [{ type: TagTypes.DataProductLifecycle, id: STATIC_TAG_ID.LIST }],
            }),
            removeDataProductLifecycle: builder.mutation<void, string>({
                query: (id) => ({
                    url: ApiUrl.DataProductLifecycle,
                    method: 'DELETE',
                    params: { lifecycle_id: id },
                }),
                invalidatesTags: [{ type: TagTypes.DataProductLifecycle as const, id: STATIC_TAG_ID.LIST }],
            }),
            updateDataProductLifecycle: builder.mutation<
                DataProductLifecycleCreateResponse,
                DataProductLifeCycleContract
            >({
                query: (request) => ({
                    url: ApiUrl.DataProductLifecycle,
                    method: 'PUT',
                    data: request,
                }),
                invalidatesTags: [{ type: TagTypes.DataProductLifecycle as const, id: STATIC_TAG_ID.LIST }],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useCreateDataProductLifecycleMutation,
    useGetAllDataProductLifecyclesQuery,
    useRemoveDataProductLifecycleMutation,
    useUpdateDataProductLifecycleMutation,
} = dataProductLifecyclesApiSlice;
