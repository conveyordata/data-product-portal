import { api } from '@/store/api/services/generated/authzApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getDatasetsApiDatasetsGet: build.query<GetDatasetsApiDatasetsGetApiResponse, GetDatasetsApiDatasetsGetApiArg>({
            query: () => ({ url: '/api/datasets' }),
        }),
        createDatasetApiDatasetsPost: build.mutation<
            CreateDatasetApiDatasetsPostApiResponse,
            CreateDatasetApiDatasetsPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/datasets',
                method: 'POST',
                body: queryArg.datasetCreate,
            }),
        }),
        getDatasetNamespaceSuggestionApiDatasetsNamespaceSuggestionGet: build.query<
            GetDatasetNamespaceSuggestionApiDatasetsNamespaceSuggestionGetApiResponse,
            GetDatasetNamespaceSuggestionApiDatasetsNamespaceSuggestionGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/datasets/namespace_suggestion',
                params: {
                    name: queryArg.name,
                },
            }),
        }),
        validateDatasetNamespaceApiDatasetsValidateNamespaceGet: build.query<
            ValidateDatasetNamespaceApiDatasetsValidateNamespaceGetApiResponse,
            ValidateDatasetNamespaceApiDatasetsValidateNamespaceGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/datasets/validate_namespace',
                params: {
                    namespace: queryArg['namespace'],
                },
            }),
        }),
        getDatasetNamespaceLengthLimitsApiDatasetsNamespaceLengthLimitsGet: build.query<
            GetDatasetNamespaceLengthLimitsApiDatasetsNamespaceLengthLimitsGetApiResponse,
            GetDatasetNamespaceLengthLimitsApiDatasetsNamespaceLengthLimitsGetApiArg
        >({
            query: () => ({ url: '/api/datasets/namespace_length_limits' }),
        }),
        getDatasetApiDatasetsIdGet: build.query<
            GetDatasetApiDatasetsIdGetApiResponse,
            GetDatasetApiDatasetsIdGetApiArg
        >({
            query: (queryArg) => ({ url: `/api/datasets/${queryArg.id}` }),
        }),
        removeDatasetApiDatasetsIdDelete: build.mutation<
            RemoveDatasetApiDatasetsIdDeleteApiResponse,
            RemoveDatasetApiDatasetsIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/datasets/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
        updateDatasetApiDatasetsIdPut: build.mutation<
            UpdateDatasetApiDatasetsIdPutApiResponse,
            UpdateDatasetApiDatasetsIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/datasets/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.datasetUpdate,
            }),
        }),
        getUserDatasetsApiDatasetsUserUserIdGet: build.query<
            GetUserDatasetsApiDatasetsUserUserIdGetApiResponse,
            GetUserDatasetsApiDatasetsUserUserIdGetApiArg
        >({
            query: (queryArg) => ({ url: `/api/datasets/user/${queryArg.userId}` }),
        }),
        getEventHistoryApiDatasetsIdHistoryGet: build.query<
            GetEventHistoryApiDatasetsIdHistoryGetApiResponse,
            GetEventHistoryApiDatasetsIdHistoryGetApiArg
        >({
            query: (queryArg) => ({ url: `/api/datasets/${queryArg.id}/history` }),
        }),
        updateDatasetAboutApiDatasetsIdAboutPut: build.mutation<
            UpdateDatasetAboutApiDatasetsIdAboutPutApiResponse,
            UpdateDatasetAboutApiDatasetsIdAboutPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/datasets/${queryArg.id}/about`,
                method: 'PUT',
                body: queryArg.datasetAboutUpdate,
            }),
        }),
        updateDatasetStatusApiDatasetsIdStatusPut: build.mutation<
            UpdateDatasetStatusApiDatasetsIdStatusPutApiResponse,
            UpdateDatasetStatusApiDatasetsIdStatusPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/datasets/${queryArg.id}/status`,
                method: 'PUT',
                body: queryArg.datasetStatusUpdate,
            }),
        }),
        updateDatasetUsageApiDatasetsIdUsagePut: build.mutation<
            UpdateDatasetUsageApiDatasetsIdUsagePutApiResponse,
            UpdateDatasetUsageApiDatasetsIdUsagePutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/datasets/${queryArg.id}/usage`,
                method: 'PUT',
                body: queryArg.datasetUsageUpdate,
            }),
        }),
        getGraphDataApiDatasetsIdGraphGet: build.query<
            GetGraphDataApiDatasetsIdGraphGetApiResponse,
            GetGraphDataApiDatasetsIdGraphGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/datasets/${queryArg.id}/graph`,
                params: {
                    level: queryArg.level,
                },
            }),
        }),
        setValueForDatasetApiDatasetsIdSettingsSettingIdPost: build.mutation<
            SetValueForDatasetApiDatasetsIdSettingsSettingIdPostApiResponse,
            SetValueForDatasetApiDatasetsIdSettingsSettingIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/datasets/${queryArg.id}/settings/${queryArg.settingId}`,
                method: 'POST',
                params: {
                    value: queryArg.value,
                },
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDatasetsApiDatasetsGetApiResponse = /** status 200 Successful Response */ DatasetsGet[];
export type GetDatasetsApiDatasetsGetApiArg = void;
export type CreateDatasetApiDatasetsPostApiResponse = /** status 200 Dataset successfully created */ {
    [key: string]: string;
};
export type CreateDatasetApiDatasetsPostApiArg = {
    datasetCreate: DatasetCreate;
};
export type GetDatasetNamespaceSuggestionApiDatasetsNamespaceSuggestionGetApiResponse =
    /** status 200 Successful Response */ NamespaceSuggestion;
export type GetDatasetNamespaceSuggestionApiDatasetsNamespaceSuggestionGetApiArg = {
    name: string;
};
export type ValidateDatasetNamespaceApiDatasetsValidateNamespaceGetApiResponse =
    /** status 200 Successful Response */ NamespaceValidation;
export type ValidateDatasetNamespaceApiDatasetsValidateNamespaceGetApiArg = {
    namespace: string;
};
export type GetDatasetNamespaceLengthLimitsApiDatasetsNamespaceLengthLimitsGetApiResponse =
    /** status 200 Successful Response */ NamespaceLengthLimits;
export type GetDatasetNamespaceLengthLimitsApiDatasetsNamespaceLengthLimitsGetApiArg = void;
export type GetDatasetApiDatasetsIdGetApiResponse = /** status 200 Successful Response */ DatasetGet;
export type GetDatasetApiDatasetsIdGetApiArg = {
    id: string;
};
export type RemoveDatasetApiDatasetsIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveDatasetApiDatasetsIdDeleteApiArg = {
    id: string;
};
export type UpdateDatasetApiDatasetsIdPutApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type UpdateDatasetApiDatasetsIdPutApiArg = {
    id: string;
    datasetUpdate: DatasetUpdate;
};
export type GetUserDatasetsApiDatasetsUserUserIdGetApiResponse = /** status 200 Successful Response */ DatasetsGet[];
export type GetUserDatasetsApiDatasetsUserUserIdGetApiArg = {
    userId: string;
};
export type GetEventHistoryApiDatasetsIdHistoryGetApiResponse = /** status 200 Successful Response */ EventGet[];
export type GetEventHistoryApiDatasetsIdHistoryGetApiArg = {
    id: string;
};
export type UpdateDatasetAboutApiDatasetsIdAboutPutApiResponse = /** status 200 Successful Response */ any;
export type UpdateDatasetAboutApiDatasetsIdAboutPutApiArg = {
    id: string;
    datasetAboutUpdate: DatasetAboutUpdate;
};
export type UpdateDatasetStatusApiDatasetsIdStatusPutApiResponse = /** status 200 Successful Response */ any;
export type UpdateDatasetStatusApiDatasetsIdStatusPutApiArg = {
    id: string;
    datasetStatusUpdate: DatasetStatusUpdate;
};
export type UpdateDatasetUsageApiDatasetsIdUsagePutApiResponse = /** status 200 Successful Response */ any;
export type UpdateDatasetUsageApiDatasetsIdUsagePutApiArg = {
    id: string;
    datasetUsageUpdate: DatasetUsageUpdate;
};
export type GetGraphDataApiDatasetsIdGraphGetApiResponse = /** status 200 Successful Response */ Graph;
export type GetGraphDataApiDatasetsIdGraphGetApiArg = {
    id: string;
    level?: number;
};
export type SetValueForDatasetApiDatasetsIdSettingsSettingIdPostApiResponse = /** status 200 Successful Response */ any;
export type SetValueForDatasetApiDatasetsIdSettingsSettingIdPostApiArg = {
    id: string;
    settingId: string;
    value: string;
};
export type DatasetStatus = 'pending' | 'active' | 'archived';
export type DatasetAccessType = 'public' | 'restricted' | 'private';
export type Tag = {
    id: string;
    value: string;
};
export type Domain = {
    id: string;
    name: string;
    description: string;
};
export type DataProductLifeCycle = {
    id: string;
    name: string;
    value: number;
    color: string;
    is_default: boolean;
};
export type DataProductSettingType = 'checkbox' | 'tags' | 'input';
export type DataProductSettingScope = 'dataproduct' | 'dataset';
export type DataProductSetting = {
    id: string;
    category: string;
    type: DataProductSettingType;
    tooltip: string;
    namespace: string;
    name: string;
    default: string;
    order?: number;
    scope: DataProductSettingScope;
};
export type DataProductSettingValue = {
    id: string;
    data_product_id?: string | null;
    dataset_id?: string | null;
    data_product_setting_id: string;
    value: string;
    data_product_setting: DataProductSetting;
};
export type DecisionStatus = 'approved' | 'pending' | 'denied';
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
export type DataOutputLink = {
    id: string;
    dataset_id: string;
    data_output_id: string;
    status: DecisionStatus;
    data_output: DataOutput;
};
export type DatasetsGet = {
    id: string;
    namespace: string;
    name: string;
    description: string;
    status: DatasetStatus;
    usage: string | null;
    access_type: DatasetAccessType;
    tags: Tag[];
    domain: Domain;
    lifecycle: DataProductLifeCycle | null;
    data_product_settings: DataProductSettingValue[];
    data_output_links: DataOutputLink[];
    data_product_count: number;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type DatasetCreate = {
    name: string;
    namespace: string;
    description: string;
    access_type: DatasetAccessType;
    about?: string | null;
    lifecycle_id?: string | null;
    domain_id: string;
    tag_ids: string[];
    owners: string[];
};
export type NamespaceSuggestion = {
    namespace: string;
};
export type NamespaceValidityType = 'VALID' | 'INVALID_LENGTH' | 'INVALID_CHARACTERS' | 'DUPLICATE_NAMESPACE';
export type NamespaceValidation = {
    validity: NamespaceValidityType;
};
export type NamespaceLengthLimits = {
    max_length: number;
};
export type DataProductLink = {
    id: string;
    data_product_id: string;
    dataset_id: string;
    status: DecisionStatus;
    data_product: DataProduct;
};
export type DatasetGet = {
    id: string;
    namespace: string;
    name: string;
    description: string;
    status: DatasetStatus;
    usage: string | null;
    access_type: DatasetAccessType;
    tags: Tag[];
    domain: Domain;
    lifecycle: DataProductLifeCycle | null;
    data_product_settings: DataProductSettingValue[];
    data_output_links: DataOutputLink[];
    about: string | null;
    data_product_links: DataProductLink[];
    rolled_up_tags: Tag[];
};
export type DatasetUpdate = {
    name: string;
    namespace: string;
    description: string;
    access_type: DatasetAccessType;
    about?: string | null;
    lifecycle_id?: string | null;
    domain_id: string;
    tag_ids: string[];
};
export type EventReferenceEntity = 'data_product' | 'dataset' | 'data_output' | 'user';
export type User = {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
};
export type Dataset = {
    id: string;
    name: string;
    namespace: string;
    description: string;
    status: DatasetStatus;
    access_type: DatasetAccessType;
};
export type DataOutput2 = {
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
};
export type EventGet = {
    id: string;
    name: string;
    subject_id: string;
    target_id?: string | null;
    subject_type: EventReferenceEntity;
    target_type?: EventReferenceEntity | null;
    actor_id: string;
    created_on: string;
    deleted_subject_identifier?: string | null;
    deleted_target_identifier?: string | null;
    actor: User;
    data_product?: DataProduct | null;
    user?: User | null;
    dataset?: Dataset | null;
    data_output?: DataOutput2 | null;
};
export type DatasetAboutUpdate = {
    about: string;
};
export type DatasetStatusUpdate = {
    status: DatasetStatus;
};
export type DatasetUsageUpdate = {
    usage: string;
};
export type Edge = {
    id: string;
    source: string;
    target: string;
    animated: boolean;
    sourceHandle?: string;
    targetHandle?: string;
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
export type RoleAssignment = {
    id: string;
    data_product: DataProduct;
    user: User;
    role: Role | null;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: User | null;
    decided_on: string | null;
    decided_by: User | null;
    data_product_id: string;
    user_id: string;
    role_id: string | null;
    requested_by_id: string | null;
    decided_by_id: string | null;
};
export type RoleAssignment2 = {
    id: string;
    dataset: Dataset;
    user: User;
    role: Role | null;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: User | null;
    decided_on: string | null;
    decided_by: User | null;
    dataset_id: string;
    user_id: string;
    role_id: string | null;
    requested_by_id: string | null;
    decided_by_id: string | null;
};
export type NodeData = {
    id: string;
    name: string;
    link_to_id?: string | null;
    icon_key?: string | null;
    domain?: string | null;
    domain_id?: string | null;
    description?: string | null;
    assignments?: (RoleAssignment | RoleAssignment2)[] | null;
};
export type NodeType = 'dataProductNode' | 'dataOutputNode' | 'datasetNode' | 'domainNode';
export type Node = {
    id: string;
    data: NodeData;
    type: NodeType;
    isMain?: boolean;
};
export type Graph = {
    edges: Edge[];
    nodes: Node[];
};
export const {
    useGetDatasetsApiDatasetsGetQuery,
    useLazyGetDatasetsApiDatasetsGetQuery,
    useCreateDatasetApiDatasetsPostMutation,
    useGetDatasetNamespaceSuggestionApiDatasetsNamespaceSuggestionGetQuery,
    useLazyGetDatasetNamespaceSuggestionApiDatasetsNamespaceSuggestionGetQuery,
    useValidateDatasetNamespaceApiDatasetsValidateNamespaceGetQuery,
    useLazyValidateDatasetNamespaceApiDatasetsValidateNamespaceGetQuery,
    useGetDatasetNamespaceLengthLimitsApiDatasetsNamespaceLengthLimitsGetQuery,
    useLazyGetDatasetNamespaceLengthLimitsApiDatasetsNamespaceLengthLimitsGetQuery,
    useGetDatasetApiDatasetsIdGetQuery,
    useLazyGetDatasetApiDatasetsIdGetQuery,
    useRemoveDatasetApiDatasetsIdDeleteMutation,
    useUpdateDatasetApiDatasetsIdPutMutation,
    useGetUserDatasetsApiDatasetsUserUserIdGetQuery,
    useLazyGetUserDatasetsApiDatasetsUserUserIdGetQuery,
    useGetEventHistoryApiDatasetsIdHistoryGetQuery,
    useLazyGetEventHistoryApiDatasetsIdHistoryGetQuery,
    useUpdateDatasetAboutApiDatasetsIdAboutPutMutation,
    useUpdateDatasetStatusApiDatasetsIdStatusPutMutation,
    useUpdateDatasetUsageApiDatasetsIdUsagePutMutation,
    useGetGraphDataApiDatasetsIdGraphGetQuery,
    useLazyGetGraphDataApiDatasetsIdGraphGetQuery,
    useSetValueForDatasetApiDatasetsIdSettingsSettingIdPostMutation,
} = injectedRtkApi;
