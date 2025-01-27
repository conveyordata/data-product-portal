import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { TagTypes } from '@/store/features/api/tag-types.ts';
import { VersionResponse } from '@/types/version';

export const versionTags: string[] = [TagTypes.Version];
export const versionApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: versionTags }).injectEndpoints({
    endpoints: (builder) => ({
        getVersion: builder.query<VersionResponse, void>({
            query: () => ({
                url: ApiUrl.Version,
                method: 'GET',
            }),
            providesTags: (version) => (version ? [{ type: TagTypes.Version as const, id: version.version }] : []),
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetVersionQuery } = versionApiSlice;
