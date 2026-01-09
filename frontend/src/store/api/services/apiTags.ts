import { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

api.enhanceEndpoints({
    addTagTypes: Object.values(TagTypes),

    endpoints: {
        becomeAdmin: {
            invalidatesTags: (_, __) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.CurrentUser },
            ],
        },
        revokeAdmin: {
            invalidatesTags: (_, __) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.CurrentUser },
            ],
        },

        getRoles: {
            providesTags: (_) => [{ type: TagTypes.Role, id: STATIC_TAG_ID.LIST }],
        },
        createRole: {
            invalidatesTags: (_) => [{ type: TagTypes.Role, id: STATIC_TAG_ID.LIST }],
        },
        removeRole: {
            invalidatesTags: (_) => [{ type: TagTypes.Role, id: STATIC_TAG_ID.LIST }],
        },
        updateRole: {
            invalidatesTags: (_) => [{ type: TagTypes.Role, id: STATIC_TAG_ID.LIST }],
        },

        listGlobalRoleAssignments: {
            providesTags: (response) => {
                const individual = (response?.role_assignments || []).map((assignment) => ({
                    type: TagTypes.GlobalRoleAssignments,
                    id: assignment.id,
                }));

                return [...individual, { type: TagTypes.GlobalRoleAssignments, id: STATIC_TAG_ID.LIST }];
            },
        },
        createGlobalRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: result?.id },
                { type: TagTypes.User, id: result?.user?.id },
            ],
        },
        modifyGlobalRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: result?.id },
                { type: TagTypes.User, id: result?.user?.id },
            ],
        },
        decideGlobalRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: result?.id },
                { type: TagTypes.User, id: result?.user?.id },
            ],
        },
        deleteGlobalRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.GlobalRoleAssignments, id: result?.id },
            ],
        },
        listDataProductRoleAssignments: {
            providesTags: (response) => {
                const items =
                    response?.role_assignments?.map((item) => ({
                        type: TagTypes.DataProductRoleAssignments,
                        id: item.id,
                    })) || [];
                return [...items, { type: TagTypes.DataProductRoleAssignments, id: STATIC_TAG_ID.LIST }];
            },
        },
        createDataProductRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductRoleAssignments, id: result?.id },
                { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct, id: result?.data_product?.id },
                { type: TagTypes.History, id: result?.data_product?.id },
            ],
        },
        modifyDataProductRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductRoleAssignments, id: result?.id },
                { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct, id: result?.data_product?.id },
                { type: TagTypes.History, id: result?.data_product?.id },
            ],
        },
        decideDataProductRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductRoleAssignments, id: result?.id },
                { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct, id: result?.data_product?.id },
                { type: TagTypes.History, id: result?.data_product?.id },
            ],
        },
        deleteDataProductRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductRoleAssignments, id: result?.id },
                { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct, id: result?.data_product_id },
                { type: TagTypes.History, id: result?.data_product_id },
            ],
        },

        createOutputPortRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPortRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPortRoleAssignments, id: result?.id },
                { type: TagTypes.UserDataProducts, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPort, id: result?.output_port?.id },
                { type: TagTypes.History, id: result?.output_port?.id },
            ],
        },
        modifyOutputPortRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPortRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPortRoleAssignments, id: result?.id },
                { type: TagTypes.UserOutputPorts, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPort, id: result?.output_port?.id },
                { type: TagTypes.History, id: result?.output_port?.id },
            ],
        },
        decideOutputPortRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPortRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPortRoleAssignments, id: result?.id },
                { type: TagTypes.UserOutputPorts, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPort, id: result?.output_port?.id },
                { type: TagTypes.History, id: result?.output_port?.id },
            ],
        },
        deleteOutputPortRoleAssignment: {
            invalidatesTags: (result) => [
                { type: TagTypes.Role, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPortRoleAssignments, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPortRoleAssignments, id: result?.id },
                { type: TagTypes.UserOutputPorts, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.OutputPort, id: result?.output_port_id },
                { type: TagTypes.History, id: result?.output_port_id },
            ],
        },

        getDataProductsLifecycles: {
            providesTags: [{ type: TagTypes.DataProductLifecycle, id: STATIC_TAG_ID.LIST }],
        },
        createDataProductLifecycle: {
            invalidatesTags: [{ type: TagTypes.DataProductLifecycle, id: STATIC_TAG_ID.LIST }],
        },
        removeDataProductLifecycle: {
            invalidatesTags: [{ type: TagTypes.DataProductLifecycle, id: STATIC_TAG_ID.LIST }],
        },
        updateDataProductLifecycle: {
            invalidatesTags: [{ type: TagTypes.DataProductLifecycle, id: STATIC_TAG_ID.LIST }],
        },

        getDataProductsSettings: {
            providesTags: [{ type: TagTypes.DataProductSetting, id: STATIC_TAG_ID.LIST }],
        },
        createDataProductSetting: {
            invalidatesTags: [{ type: TagTypes.DataProductSetting, id: STATIC_TAG_ID.LIST }],
        },
        removeDataProductSetting: {
            invalidatesTags: [{ type: TagTypes.DataProductSetting, id: STATIC_TAG_ID.LIST }],
        },
        updateDataProductSetting: {
            invalidatesTags: [{ type: TagTypes.DataProductSetting, id: STATIC_TAG_ID.LIST }],
        },

        getDataProductsTypes: {
            providesTags: (response) => {
                return response?.data_product_types
                    ? [{ type: TagTypes.DataProductType, id: STATIC_TAG_ID.LIST }]
                    : [{ type: TagTypes.DataProductType, id: STATIC_TAG_ID.LIST }];
            },
        },
        getDataProductType: {
            providesTags: (response) => {
                return response?.id ? [{ type: TagTypes.DataProductType as const, id: response.id }] : [];
            },
        },
        createDataProductType: {
            invalidatesTags: [{ type: TagTypes.DataProductType, id: STATIC_TAG_ID.LIST }],
        },
        removeDataProductType: {
            invalidatesTags: [{ type: TagTypes.DataProductType, id: STATIC_TAG_ID.LIST }],
        },
        updateDataProductType: {
            invalidatesTags: (response) => [
                { type: TagTypes.DataProductType, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProductType, id: response?.id },
            ],
        },

        getTags: {
            providesTags: [{ type: TagTypes.Tags as const, id: STATIC_TAG_ID.LIST }],
        },
        createTag: {
            invalidatesTags: [{ type: TagTypes.Tags, id: STATIC_TAG_ID.LIST }],
        },
        updateTag: {
            invalidatesTags: [
                { type: TagTypes.Tags, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const },
                { type: TagTypes.OutputPort as const },
                { type: TagTypes.TechnicalAsset as const },
            ],
        },
        removeTag: {
            invalidatesTags: [
                { type: TagTypes.Tags, id: STATIC_TAG_ID.LIST },
                { type: TagTypes.DataProduct as const },
                { type: TagTypes.OutputPort as const },
                { type: TagTypes.TechnicalAsset as const },
            ],
        },

        getThemeSettings: {
            providesTags: [{ type: TagTypes.ThemeSettings }],
        },
        updateThemeSettings: {
            invalidatesTags: [{ type: TagTypes.ThemeSettings }],
        },
    },
});
