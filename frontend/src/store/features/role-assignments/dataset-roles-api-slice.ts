import { ApiUrl, buildUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types';
import type { DecisionStatus } from '@/types/roles';
import type { DatasetRoleAssignmentContract, DatasetRoleAssignmentCreateContract } from '@/types/roles/role.contract';

export const assignmentTags: string[] = [TagTypes.DatasetAssignments];

export const datasetRoleAssignmentsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: assignmentTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getDatasetRoleAssignments: builder.query<
                DatasetRoleAssignmentContract[],
                { dataset_id?: string; user_id?: string; decision?: DecisionStatus }
            >({
                query: (request) => ({
                    url: ApiUrl.RoleAssignmentsDatasetGet,
                    method: 'GET',
                    params: {
                        ...(request.dataset_id ? { dataset_id: request.dataset_id } : {}),
                        ...(request.user_id ? { user_id: request.user_id } : {}),
                        ...(request.decision ? { decision: request.decision } : {}),
                    },
                }),
                providesTags: (assignments) =>
                    (assignments || []).map((assignment) => ({
                        type: TagTypes.DatasetAssignments as const,
                        id: assignment.dataset.id,
                    })),
            }),
            createDatasetRoleAssignment: builder.mutation<
                DatasetRoleAssignmentContract,
                DatasetRoleAssignmentCreateContract
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataset, { assignmentId: request.dataset_id }),
                    method: 'POST',
                    data: {
                        role_id: request.role_id,
                        user_id: request.user_id,
                    },
                }),
                invalidatesTags: (_, _error, { dataset_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DatasetAssignments as const, id: dataset_id },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.Dataset as const, id: dataset_id },
                ],
            }),
            requestDatasetRoleAssignment: builder.mutation<
                DatasetRoleAssignmentContract,
                DatasetRoleAssignmentCreateContract
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDatasetRequest, { datasetId: request.dataset_id }),
                    method: 'POST',
                    data: {
                        role_id: request.role_id,
                        user_id: request.user_id,
                    },
                }),
                invalidatesTags: (_, _error, { dataset_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DatasetAssignments as const, id: dataset_id },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.Dataset as const, id: dataset_id },
                ],
            }),
            updateDatasetRoleAssignment: builder.mutation<
                DatasetRoleAssignmentContract,
                { role_assignment_id: string; role_id: string; dataset_id: string }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataset, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'PATCH',
                    data: { role_id: request.role_id },
                }),
                invalidatesTags: (_, _error, { dataset_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DatasetAssignments as const, id: dataset_id },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.Dataset as const, id: dataset_id },
                ],
            }),
            decideDatasetRoleAssignment: builder.mutation<
                DatasetRoleAssignmentContract,
                { role_assignment_id: string; decision_status: DecisionStatus; dataset_id: string }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDatasetDecide, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'PATCH',
                    data: { decision: request.decision_status },
                }),
                invalidatesTags: (_, _error, { dataset_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DatasetAssignments as const, id: dataset_id },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.Dataset as const, id: dataset_id },
                ],
            }),
            deleteDatasetRoleAssignment: builder.mutation<void, { role_assignment_id: string; dataset_id: string }>({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataset, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'DELETE',
                }),
                invalidatesTags: (_, _error, { dataset_id }) => [
                    { type: TagTypes.Role as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DatasetAssignments as const, id: dataset_id },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.Dataset as const, id: dataset_id },
                ],
            }),
        }),
        overrideExisting: false,
    });

export const {
    useGetDatasetRoleAssignmentsQuery,
    useUpdateDatasetRoleAssignmentMutation,
    useDeleteDatasetRoleAssignmentMutation,
    useCreateDatasetRoleAssignmentMutation,
    useDecideDatasetRoleAssignmentMutation,
} = datasetRoleAssignmentsApiSlice;
