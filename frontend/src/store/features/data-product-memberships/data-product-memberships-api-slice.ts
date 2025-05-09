import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import { dataProductTags } from '@/store/features/data-products/data-products-api-slice.ts';
import {
    DataProductMembershipContract,
    DataProductMembershipRequestAccessRequest,
    DataProductMembershipRequestAccessResponse,
} from '@/types/data-product-membership';

export const dataProductMembershipsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            requestMembershipAccess: builder.mutation<
                DataProductMembershipRequestAccessResponse,
                DataProductMembershipRequestAccessRequest
            >({
                query: ({ dataProductId, userId }) => ({
                    url: ApiUrl.DataProductMembershipRequest,
                    method: 'POST',
                    params: { data_product_id: dataProductId, user_id: userId },
                }),
                invalidatesTags: (_result, _error, { dataProductId }) => [
                    { type: TagTypes.DataProduct as const, id: dataProductId },
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
            getDataProductMembershipPendingActions: builder.query<DataProductMembershipContract[], void>({
                query: () => ({
                    url: buildUrl(ApiUrl.DataProductMembershipPendingActions, {}),
                    method: 'GET',
                }),
                providesTags: () => [
                    { type: TagTypes.UserDataProducts as const, id: STATIC_TAG_ID.LIST },
                    { type: TagTypes.UserDatasets as const, id: STATIC_TAG_ID.LIST },
                ],
            }),
        }),
        overrideExisting: false,
    });

export const { useRequestMembershipAccessMutation, useGetDataProductMembershipPendingActionsQuery } =
    dataProductMembershipsApiSlice;
