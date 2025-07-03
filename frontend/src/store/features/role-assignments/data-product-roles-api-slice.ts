import { ApiUrl, buildUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types';
import type { DecisionStatus } from '@/types/roles';
import type {
    DataProductRoleAssignmentContract,
    DataProductRoleAssignmentCreateContract,
} from '@/types/roles/role.contract';

export const assignmentTags: string[] = [TagTypes.DataProductAssignments];

export const dataProductRoleAssignmentsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: assignmentTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getDataProductRoleAssignments: builder.query<
                DataProductRoleAssignmentContract[],
                { data_product_id?: string; user_id?: string; role_id?: string; decision?: DecisionStatus }
            >({
                query: (request) => ({
                    url: ApiUrl.RoleAssignmentsDataProductGet,
                    method: 'GET',
                    params: {
                        ...(request.data_product_id ? { data_product_id: request.data_product_id } : {}),
                        ...(request.user_id ? { user_id: request.user_id } : {}),
                        ...(request.role_id ? { role_id: request.role_id } : {}),
                        ...(request.decision ? { decision: request.decision } : {}),
                    },
                }),
                providesTags: (assignments) => {
                    const individual = (assignments || []).map((assignment) => ({
                        type: TagTypes.DataProductAssignments,
                        id: assignment.data_product.id,
                    }));
                    return [...individual, { type: TagTypes.DataProductAssignments, id: STATIC_TAG_ID.LIST }];
                },
            }),
            createDataProductRoleAssignment: builder.mutation<
                DataProductRoleAssignmentContract,
                DataProductRoleAssignmentCreateContract
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProduct, { assignmentId: request.data_product_id }),
                    method: 'POST',
                    data: {
                        role_id: request.role_id,
                        user_id: request.user_id,
                    },
                }),
                invalidatesTags: (_, _error, { data_product_id }) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: data_product_id },
                    { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct, id: data_product_id },
                    { type: TagTypes.History, id: data_product_id },
                ],
            }),
            requestDataProductRoleAssignment: builder.mutation<
                DataProductRoleAssignmentContract,
                DataProductRoleAssignmentCreateContract
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProductRequest, { dataProductId: request.data_product_id }),
                    method: 'POST',
                    data: {
                        role_id: request.role_id,
                        user_id: request.user_id,
                    },
                }),
                invalidatesTags: (_, _error, { data_product_id }) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: data_product_id },
                    { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct, id: data_product_id },
                    { type: TagTypes.History, id: data_product_id },
                ],
            }),
            updateDataProductRoleAssignment: builder.mutation<
                DataProductRoleAssignmentContract,
                { role_assignment_id: string; role_id: string; data_product_id: string }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProduct, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'PATCH',
                    data: { role_id: request.role_id },
                }),
                invalidatesTags: (_, _error, { data_product_id }) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: data_product_id },
                    { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct, id: data_product_id },
                    { type: TagTypes.History, id: data_product_id },
                ],
            }),
            decideDataProductRoleAssignment: builder.mutation<
                DataProductRoleAssignmentContract,
                { role_assignment_id: string; decision_status: DecisionStatus; data_product_id: string }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProductDecide, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'PATCH',
                    data: { decision: request.decision_status },
                }),
                invalidatesTags: (_, _error, { data_product_id }) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: data_product_id },
                    { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct, id: data_product_id },
                    { type: TagTypes.History, id: data_product_id },
                ],
            }),
            deleteDataProductRoleAssignment: builder.mutation<
                void,
                { role_assignment_id: string; data_product_id: string }
            >({
                query: (request) => ({
                    url: buildUrl(ApiUrl.RoleAssignmentsDataProduct, {
                        assignmentId: request.role_assignment_id,
                    }),
                    method: 'DELETE',
                }),
                invalidatesTags: (_, _error, { data_product_id }) => [
                    { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProductAssignments, id: data_product_id },
                    { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.DataProduct, id: data_product_id },
                    { type: TagTypes.History, id: data_product_id },
                ],
            }),
        }),
        overrideExisting: false,
    });

export const {
    useGetDataProductRoleAssignmentsQuery,
    useUpdateDataProductRoleAssignmentMutation,
    useDeleteDataProductRoleAssignmentMutation,
    useCreateDataProductRoleAssignmentMutation,
    useDecideDataProductRoleAssignmentMutation,
    useRequestDataProductRoleAssignmentMutation,
} = dataProductRoleAssignmentsApiSlice;
