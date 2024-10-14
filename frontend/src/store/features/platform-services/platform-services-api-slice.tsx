import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { IdName } from '@/types/shared';

export const platformServiceTags: string[] = [TagTypes.PlatformService];
export const platformServicesApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: platformServiceTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getAllPlatformServices: builder.query<IdName[], string>({
                query: (platformId) => ({
                    url: buildUrl(ApiUrl.PlatformServices, { platformId }),
                    method: 'GET',
                }),
                providesTags: (result = []) =>
                    result
                        ? [
                              { type: TagTypes.PlatformService as const, id: STATIC_TAG_ID.LIST },
                              ...result.map(({ id }) => ({ type: TagTypes.PlatformService as const, id })),
                          ]
                        : [{ type: TagTypes.PlatformService, id: STATIC_TAG_ID.LIST }],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetAllPlatformServicesQuery } = platformServicesApiSlice;
