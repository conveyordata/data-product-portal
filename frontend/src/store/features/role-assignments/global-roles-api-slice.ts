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
                { user_id?: string; role_id?: string; decision?: DecisionStatus }
            >({
                query: (request) => ({
                    url: ApiUrl.RoleAssignmentsGlobal,
                    method: 'GET',
                    params: {
                        ...(request.user_id ? { user_id: request.user_id } : {}),
                        ...(request.role_id ? { role_id: request.role_id } : {}),
                        ...(request.decision ? { decision: request.decision } : {}),
                    },
                }),
                providesTags: (assignments) => {
                    const individual = (assignments || []).map((assignment) => ({
                        type: TagTypes.GlobalAssignments,
                        id: assignment.id,
                    }));

                    return [...individual, { type: TagTypes.GlobalAssignments, id: STATIC_TAG_ID.LIST }];
                },
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
                invalidatesTags: (result, _error, { user_id }) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: result?.id },
                    { type: TagTypes.User, id: user_id },
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
                invalidatesTags: (result, _error) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: result?.id },
                    { type: TagTypes.User, id: result?.user.id },
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
                invalidatesTags: (result, _error) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: result?.id },
                    { type: TagTypes.User, id: result?.user.id },
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
                invalidatesTags: (result, _error) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: result?.id },
                    { type: TagTypes.User, id: result?.user.id },
                ],
            }),
            deleteGlobalRoleAssignment: builder.mutation<void, { role_assignment_id: string }>({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsGlobalDelete, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'DELETE',
                }),
                invalidatesTags: (_, _error, request) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.GlobalAssignments, id: request.role_assignment_id },
                    { type: TagTypes.User, id: STATIC_TAG_ID.LIST },
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
