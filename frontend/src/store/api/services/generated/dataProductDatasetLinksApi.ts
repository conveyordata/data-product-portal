import { api } from '@/store/api/services/generated/dataProductSettingsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        approveDataProductLinkApiDataProductDatasetLinksApproveIdPost: build.mutation<
            ApproveDataProductLinkApiDataProductDatasetLinksApproveIdPostApiResponse,
            ApproveDataProductLinkApiDataProductDatasetLinksApproveIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_dataset_links/approve/${queryArg.id}`,
                method: 'POST',
            }),
        }),
        denyDataProductLinkApiDataProductDatasetLinksDenyIdPost: build.mutation<
            DenyDataProductLinkApiDataProductDatasetLinksDenyIdPostApiResponse,
            DenyDataProductLinkApiDataProductDatasetLinksDenyIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_dataset_links/deny/${queryArg.id}`,
                method: 'POST',
            }),
        }),
        removeDataProductLinkApiDataProductDatasetLinksRemoveIdPost: build.mutation<
            RemoveDataProductLinkApiDataProductDatasetLinksRemoveIdPostApiResponse,
            RemoveDataProductLinkApiDataProductDatasetLinksRemoveIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_dataset_links/remove/${queryArg.id}`,
                method: 'POST',
            }),
        }),
        getUserPendingActionsApiDataProductDatasetLinksActionsGet: build.query<
            GetUserPendingActionsApiDataProductDatasetLinksActionsGetApiResponse,
            GetUserPendingActionsApiDataProductDatasetLinksActionsGetApiArg
        >({
            query: () => ({ url: '/api/data_product_dataset_links/actions' }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type ApproveDataProductLinkApiDataProductDatasetLinksApproveIdPostApiResponse =
    /** status 200 Successful Response */ any;
export type ApproveDataProductLinkApiDataProductDatasetLinksApproveIdPostApiArg = {
    id: string;
};
export type DenyDataProductLinkApiDataProductDatasetLinksDenyIdPostApiResponse =
    /** status 200 Successful Response */ any;
export type DenyDataProductLinkApiDataProductDatasetLinksDenyIdPostApiArg = {
    id: string;
};
export type RemoveDataProductLinkApiDataProductDatasetLinksRemoveIdPostApiResponse =
    /** status 200 Successful Response */ any;
export type RemoveDataProductLinkApiDataProductDatasetLinksRemoveIdPostApiArg = {
    id: string;
};
export type GetUserPendingActionsApiDataProductDatasetLinksActionsGetApiResponse =
    /** status 200 Successful Response */ DataProductDatasetPendingAction[];
export type GetUserPendingActionsApiDataProductDatasetLinksActionsGetApiArg = void;
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type DecisionStatus = 'approved' | 'pending' | 'denied';
export type DatasetStatus = 'pending' | 'active' | 'archived';
export type DatasetAccessType = 'public' | 'restricted' | 'private';
export type Dataset = {
    id: string;
    name: string;
    namespace: string;
    description: string;
    status: DatasetStatus;
    access_type: DatasetAccessType;
};
export type DataProductStatus = 'pending' | 'active' | 'archived';
export type DataProductIconKey =
    | 'reporting'
    | 'processing'
    | 'exploration'
    | 'ingestion'
    | 'machine_learning'
    | 'analytics'
    | 'default';
export type DataProductType = {
    id: string;
    name: string;
    description: string;
    icon_key: DataProductIconKey;
};
export type DataProduct = {
    id: string;
    name: string;
    namespace: string;
    description: string;
    status: DataProductStatus;
    type: DataProductType;
};
export type User = {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
};
export type DataProductDatasetPendingAction = {
    id: string;
    data_product_id: string;
    dataset_id: string;
    status: DecisionStatus;
    requested_on: string;
    dataset: Dataset;
    data_product: DataProduct;
    requested_by: User;
    denied_by: User | null;
    approved_by: User | null;
    pending_action_type?: 'DataProductDataset';
};
export const {
    useApproveDataProductLinkApiDataProductDatasetLinksApproveIdPostMutation,
    useDenyDataProductLinkApiDataProductDatasetLinksDenyIdPostMutation,
    useRemoveDataProductLinkApiDataProductDatasetLinksRemoveIdPostMutation,
    useGetUserPendingActionsApiDataProductDatasetLinksActionsGetQuery,
    useLazyGetUserPendingActionsApiDataProductDatasetLinksActionsGetQuery,
} = injectedRtkApi;
