import { api } from '@/store/api/services/generated/dataProductDatasetLinksApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        approveDataOutputLinkApiDataOutputDatasetLinksApproveIdPost: build.mutation<
            ApproveDataOutputLinkApiDataOutputDatasetLinksApproveIdPostApiResponse,
            ApproveDataOutputLinkApiDataOutputDatasetLinksApproveIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_output_dataset_links/approve/${queryArg.id}`,
                method: 'POST',
            }),
        }),
        denyDataOutputLinkApiDataOutputDatasetLinksDenyIdPost: build.mutation<
            DenyDataOutputLinkApiDataOutputDatasetLinksDenyIdPostApiResponse,
            DenyDataOutputLinkApiDataOutputDatasetLinksDenyIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_output_dataset_links/deny/${queryArg.id}`,
                method: 'POST',
            }),
        }),
        removeDataOutputLinkApiDataOutputDatasetLinksRemoveIdPost: build.mutation<
            RemoveDataOutputLinkApiDataOutputDatasetLinksRemoveIdPostApiResponse,
            RemoveDataOutputLinkApiDataOutputDatasetLinksRemoveIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_output_dataset_links/remove/${queryArg.id}`,
                method: 'POST',
            }),
        }),
        getUserPendingActionsApiDataOutputDatasetLinksActionsGet: build.query<
            GetUserPendingActionsApiDataOutputDatasetLinksActionsGetApiResponse,
            GetUserPendingActionsApiDataOutputDatasetLinksActionsGetApiArg
        >({
            query: () => ({ url: '/api/data_output_dataset_links/actions' }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type ApproveDataOutputLinkApiDataOutputDatasetLinksApproveIdPostApiResponse =
    /** status 200 Successful Response */ any;
export type ApproveDataOutputLinkApiDataOutputDatasetLinksApproveIdPostApiArg = {
    id: string;
};
export type DenyDataOutputLinkApiDataOutputDatasetLinksDenyIdPostApiResponse =
    /** status 200 Successful Response */ any;
export type DenyDataOutputLinkApiDataOutputDatasetLinksDenyIdPostApiArg = {
    id: string;
};
export type RemoveDataOutputLinkApiDataOutputDatasetLinksRemoveIdPostApiResponse =
    /** status 200 Successful Response */ any;
export type RemoveDataOutputLinkApiDataOutputDatasetLinksRemoveIdPostApiArg = {
    id: string;
};
export type GetUserPendingActionsApiDataOutputDatasetLinksActionsGetApiResponse =
    /** status 200 Successful Response */ DataOutputDatasetPendingAction[];
export type GetUserPendingActionsApiDataOutputDatasetLinksActionsGetApiArg = void;
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
export type DataOutputStatus = 'pending' | 'active' | 'archived';
export type DatabricksDataOutput = {
    configuration_type: 'DatabricksDataOutput';
    catalog: string;
    schema?: string;
    table?: string;
    bucket_identifier?: string;
    catalog_path?: string;
    table_path?: string;
};
export type GlueDataOutput = {
    configuration_type: 'GlueDataOutput';
    database: string;
    database_suffix?: string;
    table?: string;
    bucket_identifier?: string;
    database_path?: string;
    table_path?: string;
};
export type RedshiftDataOutput = {
    configuration_type: 'RedshiftDataOutput';
    database: string;
    schema?: string;
    table?: string;
    bucket_identifier?: string;
    database_path?: string;
    table_path?: string;
};
export type S3DataOutput = {
    configuration_type: 'S3DataOutput';
    bucket: string;
    suffix?: string;
    path: string;
};
export type SnowflakeDataOutput = {
    configuration_type: 'SnowflakeDataOutput';
    database: string;
    schema?: string;
    table?: string;
    bucket_identifier?: string;
    database_path?: string;
    table_path?: string;
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
export type DataOutput = {
    id: string;
    name: string;
    namespace: string;
    description: string;
    status: DataOutputStatus;
    sourceAligned: boolean | null;
    owner_id: string;
    platform_id: string;
    service_id: string;
    configuration:
        | ({
              configuration_type: 'DatabricksDataOutput';
          } & DatabricksDataOutput)
        | ({
              configuration_type: 'GlueDataOutput';
          } & GlueDataOutput)
        | ({
              configuration_type: 'RedshiftDataOutput';
          } & RedshiftDataOutput)
        | ({
              configuration_type: 'S3DataOutput';
          } & S3DataOutput)
        | ({
              configuration_type: 'SnowflakeDataOutput';
          } & SnowflakeDataOutput);
    owner: DataProduct;
};
export type User = {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
};
export type DataOutputDatasetPendingAction = {
    id: string;
    dataset_id: string;
    data_output_id: string;
    status: DecisionStatus;
    requested_on: string;
    denied_on: string | null;
    approved_on: string | null;
    dataset: Dataset;
    data_output: DataOutput;
    requested_by: User;
    denied_by: User | null;
    approved_by: User | null;
    pending_action_type?: 'DataOutputDataset';
};
export const {
    useApproveDataOutputLinkApiDataOutputDatasetLinksApproveIdPostMutation,
    useDenyDataOutputLinkApiDataOutputDatasetLinksDenyIdPostMutation,
    useRemoveDataOutputLinkApiDataOutputDatasetLinksRemoveIdPostMutation,
    useGetUserPendingActionsApiDataOutputDatasetLinksActionsGetQuery,
    useLazyGetUserPendingActionsApiDataOutputDatasetLinksActionsGetQuery,
} = injectedRtkApi;
