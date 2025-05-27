import { ApiUrl, buildUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types';
import type { RoleContract, RoleUpdate } from '@/types/roles';

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
        updateRole: builder.mutation<RoleContract, RoleUpdate>({
            query: (request) => ({
                url: ApiUrl.Roles,
                method: 'PATCH',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
        deleteRole: builder.mutation<void, string>({
            query: (id: string) => ({
                url: buildUrl(ApiUrl.RolesDelete, { roleId: id }),
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

export const { useGetRolesQuery, useCreateRoleMutation, useUpdateRoleMutation, useDeleteRoleMutation } = rolesApiSlice;
