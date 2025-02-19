import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import {
    BusinessAreaCreateRequest,
    BusinessAreaCreateResponse,
    BusinessAreasGetContract,
    BusinessAreaGetContract,
} from '@/types/business-area';

export const businessAreaTags: string[] = [TagTypes.BusinessArea];
export const businessAreasApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: businessAreaTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllBusinessAreas: builder.query<BusinessAreasGetContract[], void>({
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
        getBusinessArea: builder.query<BusinessAreaGetContract, string>({
            query: (businessAreaId) => ({
                url: buildUrl(ApiUrl.BusinessAreasId, { businessAreaId }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [{ type: TagTypes.BusinessArea as const, id }],
        }),
        createBusinessArea: builder.mutation<BusinessAreaCreateResponse, BusinessAreaCreateRequest>({
            query: (request) => ({
                url: ApiUrl.BusinessAreas,
                method: 'POST',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.BusinessArea, id: STATIC_TAG_ID.LIST }],
        }),
        updateBusinessArea: builder.mutation<
            BusinessAreaCreateResponse,
            { businessArea: BusinessAreaCreateRequest; businessAreaId: string }
        >({
            query: ({ businessArea, businessAreaId }) => ({
                url: buildUrl(ApiUrl.BusinessAreasId, { businessAreaId }),
                method: 'PUT',
                data: businessArea,
            }),
            invalidatesTags: [{ type: TagTypes.BusinessArea, id: STATIC_TAG_ID.LIST }],
        }),
        removeBusinessArea: builder.mutation<void, string>({
            query: (businessAreaId) => ({
                url: buildUrl(ApiUrl.BusinessAreasId, { businessAreaId }),
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: TagTypes.BusinessArea, id: STATIC_TAG_ID.LIST }],
        }),
        migrateBusinessArea: builder.mutation<void, { fromId: string; toId: string }>({
            query: ({ fromId, toId }) => ({
                url: buildUrl(ApiUrl.BusinessAreasMigrate, { fromId, toId }),
                method: 'PUT',
            }),
            invalidatesTags: (_, __, { fromId, toId }) => [
                { type: TagTypes.BusinessArea, id: fromId },
                { type: TagTypes.BusinessArea, id: toId },
            ],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useCreateBusinessAreaMutation,
    useGetAllBusinessAreasQuery,
    useUpdateBusinessAreaMutation,
    useRemoveBusinessAreaMutation,
    useGetBusinessAreaQuery,
    useMigrateBusinessAreaMutation,
} = businessAreasApiSlice;
