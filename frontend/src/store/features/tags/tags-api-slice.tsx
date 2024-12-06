import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { TagContract } from '@/types/tag';

export const tagTags: string[] = [TagTypes.Tags];
export const tagsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: tagTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllTags: builder.query<TagContract[], void>({
            query: () => ({
                url: ApiUrl.Tags,
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.Tags as const, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetAllTagsQuery } = tagsApiSlice;
