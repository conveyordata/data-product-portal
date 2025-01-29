import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { dataProductsApiSlice, dataProductTags } from '@/store/features/data-products/data-products-api-slice.ts';
import {
    DataProductMembershipApprovalRequest,
    DataProductMembershipApprovalResponse,
    DataProductMembershipContract,
    DataProductMembershipRequestAccessRequest,
    DataProductMembershipRequestAccessResponse,
    DataProductMembershipRoleUpdateRequest,
    DataProductUserMembershipCreateContract,
} from '@/types/data-product-membership';
import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';

export const dataProductMembershipsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            addDataProductMembership: builder.mutation<
                DataProductMembershipApprovalResponse,
                DataProductUserMembershipCreateContract & {
                    dataProductId: string;
                }
            >({
                query: ({ user_id, role, dataProductId }) => ({
                    url: ApiUrl.DataProductMembershipAdd,
                    method: 'POST',
                    data: { data_product_id: dataProductId, user_id, role },
                    params: { data_product_id: dataProductId },
                }),
                invalidatesTags: (_, __, { dataProductId }) => [
                    { type: TagTypes.DataProduct as const, id: dataProductId },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            requestMembershipAccess: builder.mutation<
                DataProductMembershipRequestAccessResponse,
                DataProductMembershipRequestAccessRequest
            >({
                query: ({ dataProductId, userId }) => ({
                    url: ApiUrl.DataProductMembershipRequest,
                    method: 'POST',
                    params: { data_product_id: dataProductId, user_id: userId },
                }),
                invalidatesTags: (_, __, { dataProductId }) => [
                    { type: TagTypes.DataProduct as const, id: dataProductId },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            grantMembershipAccess: builder.mutation<
                DataProductMembershipApprovalResponse,
                DataProductMembershipApprovalRequest
            >({
                query: ({ membershipId }) => ({
                    url: buildUrl(ApiUrl.DataProductMembershipApprove, { membershipId }),
                    method: 'POST',
                }),
                invalidatesTags: (result) => [
                    { type: TagTypes.DataProduct as const, id: result?.data_product_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            denyMembershipAccess: builder.mutation<
                DataProductMembershipApprovalResponse,
                DataProductMembershipApprovalRequest
            >({
                query: ({ membershipId }) => ({
                    url: buildUrl(ApiUrl.DataProductMembershipDeny, { membershipId }),
                    method: 'POST',
                }),
                invalidatesTags: (result) => [
                    { type: TagTypes.DataProduct as const, id: result?.data_product_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            removeMembershipAccess: builder.mutation<
                DataProductMembershipApprovalResponse,
                DataProductMembershipApprovalRequest
            >({
                query: ({ membershipId }) => ({
                    url: buildUrl(ApiUrl.DataProductMembershipRemove, { membershipId }),
                    method: 'POST',
                }),
                invalidatesTags: (result) => [
                    { type: TagTypes.DataProduct as const, id: result?.data_product_id },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            updateMembershipRole: builder.mutation<void, DataProductMembershipRoleUpdateRequest>({
                query: ({ membershipId, role }) => ({
                    url: buildUrl(ApiUrl.DataProductMembershipUpdate, { membershipId }),
                    method: 'PUT',
                    params: { membership_role: role },
                }),
                onQueryStarted: async ({ dataProductId, membershipId, role }, { dispatch, queryFulfilled }) => {
                    const patchResult = dispatch(
                        dataProductsApiSlice.util.updateQueryData(
                            'getDataProductById',
                            dataProductId as string,
                            (draft) => {
                                const userMembership = draft.memberships.find((u) => u.id === membershipId);
                                if (userMembership) {
                                    userMembership.role = role;
                                }
                            },
                        ),
                    );

                    queryFulfilled.catch(patchResult.undo);
                },
            }),
            getDataProductMembershipPendingActions: builder.query<DataProductMembershipContract[], void>({
                query: () => ({
                    url: buildUrl(ApiUrl.DataProductMembershipPendingActions, {}),
                    method: 'GET',
                }),
                providesTags: (_, __) => [
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
        }),
        overrideExisting: false,
    });

export const {
    useAddDataProductMembershipMutation,
    useRequestMembershipAccessMutation,
    useGrantMembershipAccessMutation,
    useDenyMembershipAccessMutation,
    useRemoveMembershipAccessMutation,
    useUpdateMembershipRoleMutation,
    useGetDataProductMembershipPendingActionsQuery,
} = dataProductMembershipsApiSlice;
