import { ApiUrl, buildUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types';
import { DecisionStatus } from '@/types/roles';
import { RoleAssignmentContract, RoleAssignmentCreateContract } from '@/types/roles/role.contract';

export const roleTags: string[] = [TagTypes.Role];

export const roleAssignmentsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: roleTags }).injectEndpoints({
    endpoints: (builder) => ({
        getRoleAssignment: builder.query<
            RoleAssignmentContract[],
            { data_product_id: string; user_id: string | undefined }
        >({
            query: (request) => ({
                url: ApiUrl.RoleAssignmentsDataProductGet,
                method: 'GET',
                params: {
                    data_product_id: request.data_product_id,
                    ...(request.user_id ? { user_id: request.user_id } : {}),
                },
            }),
            providesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
        createRoleAssignment: builder.mutation<RoleAssignmentContract, RoleAssignmentCreateContract>({
            query: (request) => ({
                url: ApiUrl.RoleAssignmentsDataProductGet,
                method: 'POST',
                data: request,
            }),
            invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
        requestRoleAssignment: builder.mutation<RoleAssignmentContract, RoleAssignmentCreateContract>({
            query: (request) => ({
                url: ApiUrl.RoleAssignmentsDataProductRequest,
                method: 'POST',
                data: request,
            }),
            invalidatesTags: (_, _error, request) => [
                { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const, id: request.data_product_id },
                { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        updateRoleAssignment: builder.mutation<RoleAssignmentContract, { role_assignment_id: string; role_id: string }>(
            {
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProductUpdate, { id: request.role_assignment_id }),
                    method: 'PATCH',
                    data: { role_id: request.role_id },
                }),
                invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
            },
        ),
        decideRoleAssignment: builder.mutation<
            RoleAssignmentContract,
            { role_assignment_id: string; decision_status: DecisionStatus }
        >({
            query: (request) => ({
                url: buildUrl(ApiUrl.RoleAssignmentsDataProductDecide, { id: request.role_assignment_id }),
                method: 'PATCH',
                data: { decision: request.decision_status },
            }),
            invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
        deleteRoleAssignment: builder.mutation<void, string>({
            query: (id: string) => ({
                url: buildUrl(ApiUrl.RoleAssignmentsDataProductDelete, { id }),
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

export const {
    useGetRoleAssignmentQuery,
    useLazyGetRoleAssignmentQuery,
    useUpdateRoleAssignmentMutation,
    useDeleteRoleAssignmentMutation,
    useCreateRoleAssignmentMutation,
    useRequestRoleAssignmentMutation,
    useDecideRoleAssignmentMutation,
} = roleAssignmentsApiSlice;
