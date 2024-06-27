import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { BusinessAreaCreateRequest, BusinessAreaCreateResponse, BusinessAreaGetResponse } from '@/types/business-area';

export const businessAreaTags: string[] = [TagTypes.BusinessArea];
export const businessAreasApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: businessAreaTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllBusinessAreas: builder.query<BusinessAreaGetResponse[], void>({
            query: () => ({
                url: ApiUrl.BusinessAreas,
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.BusinessArea as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ id }) => ({ type: TagTypes.BusinessArea as const, id })),
                      ]
                    : [{ type: TagTypes.BusinessArea, id: STATIC_TAG_ID.LIST }],
        }),
        createBusinessArea: builder.mutation<BusinessAreaCreateResponse, BusinessAreaCreateRequest>({
            query: (request) => ({
                url: ApiUrl.BusinessAreas,
                method: 'POST',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.BusinessArea, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useCreateBusinessAreaMutation, useGetAllBusinessAreasQuery } = businessAreasApiSlice;
