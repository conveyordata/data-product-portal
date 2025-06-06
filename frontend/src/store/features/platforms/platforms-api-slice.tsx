import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type { IdName } from '@/types/shared';

export const platformTags: string[] = [TagTypes.Platform];
export const platformsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: platformTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllPlatforms: builder.query<IdName[], void>({
            query: () => ({
                url: ApiUrl.Platforms,
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.Platform as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ id }) => ({ type: TagTypes.Platform as const, id })),
                      ]
                    : [{ type: TagTypes.Platform, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetAllPlatformsQuery } = platformsApiSlice;
