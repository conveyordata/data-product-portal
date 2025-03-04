import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { PlatformServiceConfigCreateRequest, PlatformServiceConfigGetResponse } from '@/types/platform-service-config';

type PlatformServiceConfigRequest = {
    platformId: string;
    serviceId: string;
};

export const platformServiceConfigTags: string[] = [TagTypes.PlatformServiceConfig];
export const platformServiceConfigsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: platformServiceConfigTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getAllPlatformsConfigs: builder.query<PlatformServiceConfigGetResponse[], void>({
                query: () => ({
                    url: ApiUrl.PlatformsConfigs,
                    method: 'GET',
                }),
                providesTags: (result = []) =>
                    result
                        ? [
                              { type: TagTypes.PlatformServiceConfig as const, id: STATIC_TAG_ID.LIST },
                              ...result.map(({ id }) => ({ type: TagTypes.PlatformServiceConfig as const, id })),
                          ]
                        : [{ type: TagTypes.PlatformServiceConfig as const, id: STATIC_TAG_ID.LIST }],
            }),
            getPlatformServiceConfig: builder.query<PlatformServiceConfigGetResponse, PlatformServiceConfigRequest>({
                query: ({ platformId, serviceId }) => ({
                    url: buildUrl(ApiUrl.PlatformServiceConfig, { platformId, serviceId }),
                    method: 'GET',
                }),
                providesTags: (result) =>
                    result ? [{ type: TagTypes.PlatformServiceConfig as const, id: result.id }] : [],
            }),
            getPlatformServiceConfigById: builder.query<PlatformServiceConfigGetResponse, string>({
                query: (configId) => ({
                    url: buildUrl(ApiUrl.PlatformServiceConfigById, { configId }),
                    method: 'GET',
                }),
                providesTags: (result) =>
                    result ? [{ type: TagTypes.PlatformServiceConfig as const, id: result.id }] : [],
            }),
            createPlatformServiceConfig: builder.mutation<void, PlatformServiceConfigCreateRequest>({
                query: ({ platformId, serviceId, config }) => ({
                    url: buildUrl(ApiUrl.PlatformServiceConfig, { platformId, serviceId }),
                    method: 'POST',
                    data: config,
                }),
                invalidatesTags: [{ type: TagTypes.PlatformServiceConfig as const, id: STATIC_TAG_ID.LIST }],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useCreatePlatformServiceConfigMutation,
    useGetAllPlatformsConfigsQuery,
    useGetPlatformServiceConfigByIdQuery,
    useGetPlatformServiceConfigQuery,
} = platformServiceConfigsApiSlice;
