import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type { TagContract, TagCreateRequest, TagCreateResponse } from '@/types/tag';

export const tagTags: string[] = [TagTypes.Tags, TagTypes.DataProduct, TagTypes.Dataset, TagTypes.DataOutput];

export const tagsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: tagTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllTags: builder.query<TagContract[], void>({
            query: () => ({
                url: ApiUrl.Tags,
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.Tags as const, id: STATIC_TAG_ID.LIST }],
        }),
        createTag: builder.mutation<TagCreateResponse, TagCreateRequest>({
            query: (request) => ({
                url: ApiUrl.Tags,
                method: 'POST',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.Tags as const, id: STATIC_TAG_ID.LIST }],
        }),
        updateTag: builder.mutation<TagCreateResponse, { tag: TagCreateRequest; tagId: string }>({
            query: ({ tag, tagId }) => ({
                url: buildUrl(ApiUrl.TagsId, { tagId }),
                method: 'PUT',
                data: tag,
            }),
            invalidatesTags: [
                { type: TagTypes.Tags as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const },
                { type: TagTypes.Dataset as const },
                { type: TagTypes.DataOutput as const },
            ],
        }),
        removeTag: builder.mutation<void, string>({
            query: (tagId) => ({
                url: buildUrl(ApiUrl.TagsId, { tagId }),
                method: 'DELETE',
            }),
            invalidatesTags: [
                { type: TagTypes.Tags as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const },
                { type: TagTypes.Dataset as const },
                { type: TagTypes.DataOutput as const },
            ],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetAllTagsQuery, useCreateTagMutation, useUpdateTagMutation, useRemoveTagMutation } = tagsApiSlice;
