import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { DomainCreateRequest, DomainCreateResponse, DomainsGetContract, DomainGetContract } from '@/types/domain';

export const domainTags: string[] = [
    TagTypes.Domain,
    TagTypes.DataProduct,
    TagTypes.UserDataProducts,
    TagTypes.Dataset,
    TagTypes.UserDatasets,
];
export const domainsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: domainTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllDomains: builder.query<DomainsGetContract[], void>({
            query: () => ({
                url: ApiUrl.Domains,
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.Domain as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ id }) => ({ type: TagTypes.Domain as const, id })),
                      ]
                    : [{ type: TagTypes.Domain, id: STATIC_TAG_ID.LIST }],
        }),
        getDomain: builder.query<DomainGetContract, string>({
            query: (domainId) => ({
                url: buildUrl(ApiUrl.DomainsId, { domainId }),
                method: 'GET',
            }),
            providesTags: (_, __, id) => [{ type: TagTypes.Domain as const, id }],
        }),
        createDomain: builder.mutation<DomainCreateResponse, DomainCreateRequest>({
            query: (request) => ({
                url: ApiUrl.Domains,
                method: 'POST',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.Domain, id: STATIC_TAG_ID.LIST }],
        }),
        updateDomain: builder.mutation<DomainCreateResponse, { domain: DomainCreateRequest; domainId: string }>({
            query: ({ domain, domainId }) => ({
                url: buildUrl(ApiUrl.DomainsId, { domainId }),
                method: 'PUT',
                data: domain,
            }),
            invalidatesTags: [
                { type: TagTypes.Domain as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const },
                { type: TagTypes.UserDataProducts as const },
                { type: TagTypes.Dataset as const },
                { type: TagTypes.UserDatasets as const },
            ],
        }),
        removeDomain: builder.mutation<void, string>({
            query: (domainId) => ({
                url: buildUrl(ApiUrl.DomainsId, { domainId }),
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: TagTypes.Domain, id: STATIC_TAG_ID.LIST }],
        }),
        migrateDomain: builder.mutation<void, { fromId: string; toId: string }>({
            query: ({ fromId, toId }) => ({
                url: buildUrl(ApiUrl.DomainsMigrate, { fromId, toId }),
                method: 'PUT',
            }),
            invalidatesTags: (_, __, { fromId, toId }) => [
                { type: TagTypes.Domain, id: fromId },
                { type: TagTypes.Domain, id: toId },
                { type: TagTypes.DataProduct as const },
                { type: TagTypes.UserDataProducts as const },
                { type: TagTypes.Dataset as const },
                { type: TagTypes.UserDatasets as const },
            ],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useCreateDomainMutation,
    useGetAllDomainsQuery,
    useUpdateDomainMutation,
    useRemoveDomainMutation,
    useGetDomainQuery,
    useMigrateDomainMutation,
} = domainsApiSlice;
