import { ApiUrl, buildUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types';
import type { DecisionStatus } from '@/types/roles';
import type { GlobalRoleAssignmentContract, GlobalRoleAssignmentCreateContract } from '@/types/roles/role.contract';

export const assignmentTags: string[] = [TagTypes.GlobalAssignments];

export const globalRoleAssignmentsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: assignmentTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getGlobalRoleAssignments: builder.query<
                GlobalRoleAssignmentContract[],
                { role_id?: string; user_id?: string; decision?: DecisionStatus }
            >({
                query: (request) => ({
                    url: ApiUrl.RoleAssignmentsGlobal,
                    method: 'GET',
                    params: {
                        ...(request.role_id ? { global_id: request.role_id } : {}),
                        ...(request.user_id ? { user_id: request.user_id } : {}),
                        ...(request.decision ? { decision: request.decision } : {}),
                    },
                }),
                providesTags: (assignments) =>
                    (assignments || []).map((assignment) => ({
                        type: TagTypes.GlobalAssignments as const,
                        id: assignment.id,
                    })),
            }),
            createGlobalRoleAssignment: builder.mutation<
                GlobalRoleAssignmentContract,
                GlobalRoleAssignmentCreateContract
            >({
                query: (request) => ({
                    url: ApiUrl.RoleAssignmentsGlobal,
                    method: 'POST',
                    data: {
                        role_id: request.role_id,
                        user_id: request.user_id,
                    },
                }),
                invalidatesTags: (_, _error, { user_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.User as const, id: user_id },
                ],
            }),
            requestGlobalRoleAssignment: builder.mutation<
                GlobalRoleAssignmentContract,
                GlobalRoleAssignmentCreateContract
            >({
                query: (request) => ({
                    url: ApiUrl.RoleAssignmentsGlobalRequest,
                    method: 'POST',
                    data: {
                        role_id: request.role_id,
                        user_id: request.user_id,
                    },
                }),
                invalidatesTags: (_, _error, { role_id, user_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments as const, id: role_id },
                    { type: TagTypes.User as const, id: user_id },
                ],
            }),
            updateGlobalRoleAssignment: builder.mutation<
                GlobalRoleAssignmentContract,
                { role_assignment_id: string; role_id: string }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsGlobalUpdate, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'PATCH',
                    data: { role_id: request.role_id },
                }),
                invalidatesTags: (_result, _error) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.User as const, id: _result?.user.id || STATIC_TAG_ID.LIST },
                ],
            }),
            decideGlobalRoleAssignment: builder.mutation<
                GlobalRoleAssignmentContract,
                { role_assignment_id: string; decision_status: DecisionStatus }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsGlobalDecide, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'PATCH',
                    data: { decision: request.decision_status },
                }),
                invalidatesTags: (_result, _error) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.User as const, id: _result?.user.id || STATIC_TAG_ID.LIST },
                ],
            }),
            deleteGlobalRoleAssignment: builder.mutation<void, { role_assignment_id: string }>({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsGlobalDelete, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'DELETE',
                }),
                invalidatesTags: (_, _error) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.User as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
        }),
        overrideExisting: false,
    });

export const {
    useGetGlobalRoleAssignmentsQuery,
    useUpdateGlobalRoleAssignmentMutation,
    useDeleteGlobalRoleAssignmentMutation,
    useCreateGlobalRoleAssignmentMutation,
    useDecideGlobalRoleAssignmentMutation,
} = globalRoleAssignmentsApiSlice;
