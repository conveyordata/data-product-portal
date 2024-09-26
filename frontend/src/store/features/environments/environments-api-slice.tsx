import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { Environment, EnvironmentConfig } from '@/types/environment';

export const environmentTags: string[] = [TagTypes.Environment, TagTypes.EnvironmentConfigs];

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
                          ...result.map(({ id }) => ({ type: TagTypes.Environment as const, id })),
                      ]
                    : [{ type: TagTypes.Environment, id: STATIC_TAG_ID.LIST }],
        }),
        getAllEnvironmentConfigs: builder.query<EnvironmentConfig[], string>({
            query: (environmentId) => ({
                url: buildUrl(ApiUrl.EnvPlatformServiceConfigs, { environmentId }),
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.EnvironmentConfigs as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ id }) => ({ type: TagTypes.EnvironmentConfigs as const, id })),
                      ]
                    : [{ type: TagTypes.EnvironmentConfigs, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetAllEnvironmentsQuery, useGetAllEnvironmentConfigsQuery } = environmentsApiSlice;
