import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type { PlatformServiceConfigGetResponse } from '@/types/platform-service-config';

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
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetAllPlatformsConfigsQuery } = platformServiceConfigsApiSlice;
