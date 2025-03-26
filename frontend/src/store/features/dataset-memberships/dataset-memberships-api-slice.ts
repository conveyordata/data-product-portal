import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { datasetsApiSlice, datasetTags } from '@/store/features/datasets/datasets-api-slice.ts';
import {
    DatasetMembershipApprovalRequest,
    DatasetMembershipApprovalResponse,
    DatasetMembershipContract,
    DatasetMembershipRequestAccessRequest,
    DatasetMembershipRequestAccessResponse,
    DatasetMembershipRoleUpdateRequest,
    DatasetUserMembershipCreateContract,
} from '@/types/dataset-membership';

export const datasetMembershipsApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: datasetTags }).injectEndpoints({
    endpoints: (builder) => ({
        addDatasetMembership: builder.mutation<
            DatasetMembershipApprovalResponse,
            DatasetUserMembershipCreateContract & {
                datasetId: string;
            }
        >({
            query: ({ user_id, role, datasetId }) => ({
                url: ApiUrl.DatasetMembershipAdd,
                method: 'POST',
                data: { dataset_id: datasetId, user_id, role },
                params: { dataset_id: datasetId },
            }),
            invalidatesTags: (_result, _error, { datasetId }) => [
                { type: TagTypes.Dataset as const, id: datasetId },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        requestMembershipAccess: builder.mutation<
            DatasetMembershipRequestAccessResponse,
            DatasetMembershipRequestAccessRequest
        >({
            query: ({ datasetId, userId }) => ({
                url: ApiUrl.DatasetMembershipRequest,
                method: 'POST',
                params: { dataset_id: datasetId, user_id: userId },
            }),
            invalidatesTags: (_result, _error, { datasetId }) => [
                { type: TagTypes.Dataset as const, id: datasetId },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        grantMembershipAccess: builder.mutation<DatasetMembershipApprovalResponse, DatasetMembershipApprovalRequest>({
            query: ({ membershipId }) => ({
                url: buildUrl(ApiUrl.DatasetMembershipApprove, { membershipId }),
                method: 'POST',
            }),
            invalidatesTags: (result) => [
                { type: TagTypes.Dataset as const, id: result?.dataset_id },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        denyMembershipAccess: builder.mutation<DatasetMembershipApprovalResponse, DatasetMembershipApprovalRequest>({
            query: ({ membershipId }) => ({
                url: buildUrl(ApiUrl.DatasetMembershipDeny, { membershipId }),
                method: 'POST',
            }),
            invalidatesTags: (result) => [
                { type: TagTypes.Dataset as const, id: result?.dataset_id },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        removeMembershipAccess: builder.mutation<DatasetMembershipApprovalResponse, DatasetMembershipApprovalRequest>({
            query: ({ membershipId }) => ({
                url: buildUrl(ApiUrl.DatasetMembershipRemove, { membershipId }),
                method: 'POST',
            }),
            invalidatesTags: (result) => [
                { type: TagTypes.Dataset as const, id: result?.dataset_id },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
        updateMembershipRole: builder.mutation<void, DatasetMembershipRoleUpdateRequest>({
            query: ({ membershipId, role }) => ({
                url: buildUrl(ApiUrl.DatasetMembershipUpdate, { membershipId }),
                method: 'PUT',
                params: { membership_role: role },
            }),
            onQueryStarted: async ({ datasetId, membershipId, role }, { dispatch, queryFulfilled }) => {
                const patchResult = dispatch(
                    datasetsApiSlice.util.updateQueryData('getDatasetById', datasetId as string, (draft) => {
                        const userMembership = draft.memberships.find((u) => u.id === membershipId);
                        if (userMembership) {
                            userMembership.role = role;
                        }
                    }),
                );

                queryFulfilled.catch(patchResult.undo);
            },
        }),
        getDatasetMembershipPendingActions: builder.query<DatasetMembershipContract[], void>({
            query: () => ({
                url: buildUrl(ApiUrl.DatasetMembershipPendingActions, {}),
                method: 'GET',
            }),
            providesTags: () => [
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
            ],
        }),
    }),
    overrideExisting: false,
});

export const {
    useAddDatasetMembershipMutation,
    useRequestMembershipAccessMutation,
    useGrantMembershipAccessMutation,
    useDenyMembershipAccessMutation,
    useRemoveMembershipAccessMutation,
    useUpdateMembershipRoleMutation,
    useGetDatasetMembershipPendingActionsQuery,
} = datasetMembershipsApiSlice;
