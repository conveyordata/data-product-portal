import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type { RoleContract } from '@/types/roles';

export const roleTags: string[] = [TagTypes.Role];

export const rolesApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: roleTags }).injectEndpoints({
    endpoints: (builder) => ({
        getRoles: builder.query<RoleContract[], string>({
            query: (scope: string) => ({
                url: buildUrl(ApiUrl.RolesGet, { scope }),
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
        createRole: builder.mutation<RoleContract, Omit<RoleContract, 'id'>>({
            query: (request) => ({
                url: ApiUrl.Roles,
                method: 'POST',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
        updateRole: builder.mutation<RoleContract, RoleContract>({
            query: (request) => ({
                url: ApiUrl.Roles,
                method: 'PUT',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
        deleteRole: builder.mutation<void, string>({
            query: (id: string) => ({
                url: buildUrl(ApiUrl.RolesDelete, { id }),
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

export const { useGetRolesQuery, useCreateRoleMutation, useUpdateRoleMutation, useDeleteRoleMutation } = rolesApiSlice;
