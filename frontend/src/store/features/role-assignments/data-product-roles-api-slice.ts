import { ApiUrl, buildUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types';
import { DecisionStatus } from '@/types/roles';
import { RoleAssignmentContract, RoleAssignmentCreateContract } from '@/types/roles/role.contract';

export const roleTags: string[] = [TagTypes.Role];

export const dataProductRoleAssignmentsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: roleTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getRoleAssignment: builder.query<
                RoleAssignmentContract[],
                { data_product_id?: string; user_id?: string; decision?: DecisionStatus }
            >({
                query: (request) => ({
                    url: ApiUrl.RoleAssignmentsDataProductGet,
                    method: 'GET',
                    params: {
                        ...(request.data_product_id ? { data_product_id: request.data_product_id } : {}),
                        ...(request.user_id ? { user_id: request.user_id } : {}),
                        ...(request.decision ? { decision: request.decision } : {}),
                    },
                }),
                providesTags: [{ type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST }],
            }),
            createRoleAssignment: builder.mutation<RoleAssignmentContract, RoleAssignmentCreateContract>({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProductDelete, { id: request.data_product_id }),
                    method: 'POST',
                    data: {
                        role_id: request.role_id,
                        user_id: request.user_id,
                    },
                }),
                invalidatesTags: (_, _error, request) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct as const, id: request.data_product_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            updateRoleAssignment: builder.mutation<
                RoleAssignmentContract,
                { role_assignment_id: string; role_id: string; data_product_id: string }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProductUpdate, { id: request.role_assignment_id }),
                    method: 'PATCH',
                    data: { role_id: request.role_id },
                }),
                invalidatesTags: (_, _error, { data_product_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct as const, id: data_product_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            decideRoleAssignment: builder.mutation<
                RoleAssignmentContract,
                { role_assignment_id: string; decision_status: DecisionStatus; data_product_id: string }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProductDecide, { id: request.role_assignment_id }),
                    method: 'PATCH',
                    data: { decision: request.decision_status },
                }),
                invalidatesTags: (_, _error, { data_product_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct as const, id: data_product_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            deleteRoleAssignment: builder.mutation<void, { id: string; data_product_id: string }>({
                query: ({ id }) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProductDelete, { id }),
                    method: 'DELETE',
                }),
                invalidatesTags: (_, _error, { data_product_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct as const, id: data_product_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
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
    useDecideRoleAssignmentMutation,
} = dataProductRoleAssignmentsApiSlice;
