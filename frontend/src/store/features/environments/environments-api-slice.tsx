import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { Environment } from '@/types/environment';

export const environmentTags: string[] = [TagTypes.Environment];
export const environmentsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: environmentTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllEnvironments: builder.query<Environment[], void>({
            query: () => ({
                url: ApiUrl.Environments,
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.Environment as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ name }) => ({ type: TagTypes.Environment as const, id: name })),
                      ]
                    : [{ type: TagTypes.Environment, id: STATIC_TAG_ID.LIST }],
        }),
        createEnvironment: builder.mutation<Environment, Environment>({
            query: (request) => ({
                url: ApiUrl.DataProductType,
                method: 'POST',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.Environment, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetAllEnvironmentsQuery, useCreateEnvironmentMutation } = environmentsApiSlice;
