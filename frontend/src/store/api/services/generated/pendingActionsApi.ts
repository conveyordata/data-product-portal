import { api } from '@/store/api/services/generated/notificationsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getUserPendingActionsApiDataProductDatasetLinksActionsGet: build.query<
            GetUserPendingActionsApiDataProductDatasetLinksActionsGetApiResponse,
            GetUserPendingActionsApiDataProductDatasetLinksActionsGetApiArg
        >({
            query: () => ({ url: '/api/data_product_dataset_links/actions' }),
        }),
        getUserPendingActionsApiDataOutputDatasetLinksActionsGet: build.query<
            GetUserPendingActionsApiDataOutputDatasetLinksActionsGetApiResponse,
            GetUserPendingActionsApiDataOutputDatasetLinksActionsGetApiArg
        >({
            query: () => ({ url: '/api/data_output_dataset_links/actions' }),
        }),
        getUserPendingActionsApiPendingActionsGet: build.query<
            GetUserPendingActionsApiPendingActionsGetApiResponse,
            GetUserPendingActionsApiPendingActionsGetApiArg
        >({
            query: () => ({ url: '/api/pending_actions' }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetUserPendingActionsApiDataProductDatasetLinksActionsGetApiResponse =
    /** status 200 Successful Response */ DataProductDatasetPendingAction[];
export type GetUserPendingActionsApiDataProductDatasetLinksActionsGetApiArg = void;
export type GetUserPendingActionsApiDataOutputDatasetLinksActionsGetApiResponse =
    /** status 200 Successful Response */ DataOutputDatasetPendingAction[];
export type GetUserPendingActionsApiDataOutputDatasetLinksActionsGetApiArg = void;
export type GetUserPendingActionsApiPendingActionsGetApiResponse = /** status 200 Successful Response */ (
    | DataProductDatasetPendingAction
    | DataOutputDatasetPendingAction
    | DataProductRoleAssignmentPendingAction
)[];
export type GetUserPendingActionsApiPendingActionsGetApiArg = void;
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
export type Scope = 'dataset' | 'data_product' | 'domain' | 'global';
export type AuthorizationAction =
    | 101
    | 102
    | 103
    | 104
    | 105
    | 106
    | 107
    | 301
    | 302
    | 303
    | 304
    | 305
    | 306
    | 307
    | 308
    | 309
    | 310
    | 311
    | 312
    | 313
    | 314
    | 315
    | 401
    | 402
    | 403
    | 404
    | 405
    | 406
    | 407
    | 408
    | 409
    | 410
    | 411
    | 412
    | 413;
export type Prototype = 0 | 1 | 2 | 3;
export type Role = {
    name: string;
    scope: Scope;
    description: string;
    permissions: AuthorizationAction[];
    id: string;
    prototype: Prototype;
};
export type DataProductRoleAssignmentPendingAction = {
    id: string;
    data_product: DataProduct;
    user: User;
    role: Role | null;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: User | null;
    decided_on: string | null;
    decided_by: User | null;
    pending_action_type?: 'DataProductRoleAssignment';
};
export const {
    useGetUserPendingActionsApiDataProductDatasetLinksActionsGetQuery,
    useLazyGetUserPendingActionsApiDataProductDatasetLinksActionsGetQuery,
    useGetUserPendingActionsApiDataOutputDatasetLinksActionsGetQuery,
    useLazyGetUserPendingActionsApiDataOutputDatasetLinksActionsGetQuery,
    useGetUserPendingActionsApiPendingActionsGetQuery,
    useLazyGetUserPendingActionsApiPendingActionsGetQuery,
} = injectedRtkApi;
