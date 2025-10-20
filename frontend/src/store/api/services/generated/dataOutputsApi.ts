import { api } from '@/store/api/services/generated/dataOutputDatasetLinksApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getDataOutputsApiDataProductsIdDataOutputsGet: build.query<
            GetDataOutputsApiDataProductsIdDataOutputsGetApiResponse,
            GetDataOutputsApiDataProductsIdDataOutputsGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/data_outputs`,
            }),
        }),
        getDataOutputsApiDataOutputsGet: build.query<
            GetDataOutputsApiDataOutputsGetApiResponse,
            GetDataOutputsApiDataOutputsGetApiArg
        >({
            query: () => ({ url: '/api/data_outputs' }),
        }),
        getDataOutputNamespaceSuggestionApiDataOutputsNamespaceSuggestionGet: build.query<
            GetDataOutputNamespaceSuggestionApiDataOutputsNamespaceSuggestionGetApiResponse,
            GetDataOutputNamespaceSuggestionApiDataOutputsNamespaceSuggestionGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_outputs/namespace_suggestion',
                params: {
                    name: queryArg.name,
                },
            }),
        }),
        getDataOutputNamespaceLengthLimitsApiDataOutputsNamespaceLengthLimitsGet: build.query<
            GetDataOutputNamespaceLengthLimitsApiDataOutputsNamespaceLengthLimitsGetApiResponse,
            GetDataOutputNamespaceLengthLimitsApiDataOutputsNamespaceLengthLimitsGetApiArg
        >({
            query: () => ({ url: '/api/data_outputs/namespace_length_limits' }),
        }),
        getDataOutputResultStringApiDataOutputsResultStringPost: build.mutation<
            GetDataOutputResultStringApiDataOutputsResultStringPostApiResponse,
            GetDataOutputResultStringApiDataOutputsResultStringPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_outputs/result_string',
                method: 'POST',
                body: queryArg.dataOutputResultStringRequest,
            }),
        }),
        getDataOutputApiDataOutputsIdGet: build.query<
            GetDataOutputApiDataOutputsIdGetApiResponse,
            GetDataOutputApiDataOutputsIdGetApiArg
        >({
            query: (queryArg) => ({ url: `/api/data_outputs/${queryArg.id}` }),
        }),
        removeDataOutputApiDataOutputsIdDelete: build.mutation<
            RemoveDataOutputApiDataOutputsIdDeleteApiResponse,
            RemoveDataOutputApiDataOutputsIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_outputs/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
        updateDataOutputApiDataOutputsIdPut: build.mutation<
            UpdateDataOutputApiDataOutputsIdPutApiResponse,
            UpdateDataOutputApiDataOutputsIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_outputs/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.dataOutputUpdate,
            }),
        }),
        getEventHistoryApiDataOutputsIdHistoryGet: build.query<
            GetEventHistoryApiDataOutputsIdHistoryGetApiResponse,
            GetEventHistoryApiDataOutputsIdHistoryGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_outputs/${queryArg.id}/history`,
            }),
        }),
        updateDataOutputStatusApiDataOutputsIdStatusPut: build.mutation<
            UpdateDataOutputStatusApiDataOutputsIdStatusPutApiResponse,
            UpdateDataOutputStatusApiDataOutputsIdStatusPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_outputs/${queryArg.id}/status`,
                method: 'PUT',
                body: queryArg.dataOutputStatusUpdate,
            }),
        }),
        linkDatasetToDataOutputApiDataOutputsIdDatasetDatasetIdPost: build.mutation<
            LinkDatasetToDataOutputApiDataOutputsIdDatasetDatasetIdPostApiResponse,
            LinkDatasetToDataOutputApiDataOutputsIdDatasetDatasetIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_outputs/${queryArg.id}/dataset/${queryArg.datasetId}`,
                method: 'POST',
            }),
        }),
        unlinkDatasetFromDataOutputApiDataOutputsIdDatasetDatasetIdDelete: build.mutation<
            UnlinkDatasetFromDataOutputApiDataOutputsIdDatasetDatasetIdDeleteApiResponse,
            UnlinkDatasetFromDataOutputApiDataOutputsIdDatasetDatasetIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_outputs/${queryArg.id}/dataset/${queryArg.datasetId}`,
                method: 'DELETE',
            }),
        }),
        getGraphDataApiDataOutputsIdGraphGet: build.query<
            GetGraphDataApiDataOutputsIdGraphGetApiResponse,
            GetGraphDataApiDataOutputsIdGraphGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_outputs/${queryArg.id}/graph`,
                params: {
                    level: queryArg.level,
                },
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataOutputsApiDataProductsIdDataOutputsGetApiResponse =
    /** status 200 Successful Response */ DataOutputGetRead[];
export type GetDataOutputsApiDataProductsIdDataOutputsGetApiArg = {
    id: string;
};
export type GetDataOutputsApiDataOutputsGetApiResponse = /** status 200 Successful Response */ DataOutputsGetRead[];
export type GetDataOutputsApiDataOutputsGetApiArg = void;
export type GetDataOutputNamespaceSuggestionApiDataOutputsNamespaceSuggestionGetApiResponse =
    /** status 200 Successful Response */ NamespaceSuggestion;
export type GetDataOutputNamespaceSuggestionApiDataOutputsNamespaceSuggestionGetApiArg = {
    name: string;
};
export type GetDataOutputNamespaceLengthLimitsApiDataOutputsNamespaceLengthLimitsGetApiResponse =
    /** status 200 Successful Response */ NamespaceLengthLimits;
export type GetDataOutputNamespaceLengthLimitsApiDataOutputsNamespaceLengthLimitsGetApiArg = void;
export type GetDataOutputResultStringApiDataOutputsResultStringPostApiResponse =
    /** status 200 Successful Response */ string;
export type GetDataOutputResultStringApiDataOutputsResultStringPostApiArg = {
    dataOutputResultStringRequest: DataOutputResultStringRequest;
};
export type GetDataOutputApiDataOutputsIdGetApiResponse = /** status 200 Successful Response */ DataOutputGetRead;
export type GetDataOutputApiDataOutputsIdGetApiArg = {
    id: string;
};
export type RemoveDataOutputApiDataOutputsIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveDataOutputApiDataOutputsIdDeleteApiArg = {
    id: string;
};
export type UpdateDataOutputApiDataOutputsIdPutApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type UpdateDataOutputApiDataOutputsIdPutApiArg = {
    id: string;
    dataOutputUpdate: DataOutputUpdate;
};
export type GetEventHistoryApiDataOutputsIdHistoryGetApiResponse = /** status 200 Successful Response */ EventGet[];
export type GetEventHistoryApiDataOutputsIdHistoryGetApiArg = {
    id: string;
};
export type UpdateDataOutputStatusApiDataOutputsIdStatusPutApiResponse = /** status 200 Successful Response */ any;
export type UpdateDataOutputStatusApiDataOutputsIdStatusPutApiArg = {
    id: string;
    dataOutputStatusUpdate: DataOutputStatusUpdate;
};
export type LinkDatasetToDataOutputApiDataOutputsIdDatasetDatasetIdPostApiResponse =
    /** status 200 Successful Response */ {
        [key: string]: string;
    };
export type LinkDatasetToDataOutputApiDataOutputsIdDatasetDatasetIdPostApiArg = {
    id: string;
    datasetId: string;
};
export type UnlinkDatasetFromDataOutputApiDataOutputsIdDatasetDatasetIdDeleteApiResponse =
    /** status 200 Successful Response */ any;
export type UnlinkDatasetFromDataOutputApiDataOutputsIdDatasetDatasetIdDeleteApiArg = {
    id: string;
    datasetId: string;
};
export type GetGraphDataApiDataOutputsIdGraphGetApiResponse = /** status 200 Successful Response */ Graph;
export type GetGraphDataApiDataOutputsIdGraphGetApiArg = {
    id: string;
    level?: number;
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
export type DatasetLink = {
    id: string;
    dataset_id: string;
    data_output_id: string;
    status: DecisionStatus;
    dataset: Dataset;
};
export type Tag = {
    id: string;
    value: string;
};
export type DataOutputGet = {
    id: string;
    name: string;
    description: string;
    namespace: string;
    owner_id: string;
    platform_id: string;
    service_id: string;
    status: DataOutputStatus;
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
    dataset_links: DatasetLink[];
    tags: Tag[];
};
export type TechnicalInfo = {
    environment_id: string;
    environment: string;
    info: string | null;
};
export type DataOutputGetRead = {
    id: string;
    name: string;
    description: string;
    namespace: string;
    owner_id: string;
    platform_id: string;
    service_id: string;
    status: DataOutputStatus;
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
    dataset_links: DatasetLink[];
    tags: Tag[];
    result_string: string;
    technical_info: TechnicalInfo[];
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type DataOutputsGet = {
    id: string;
    name: string;
    description: string;
    namespace: string;
    owner_id: string;
    platform_id: string;
    service_id: string;
    status: DataOutputStatus;
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
export type DataOutputsGetRead = {
    id: string;
    name: string;
    description: string;
    namespace: string;
    owner_id: string;
    platform_id: string;
    service_id: string;
    status: DataOutputStatus;
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
    result_string: string;
    technical_info: TechnicalInfo[];
};
export type NamespaceSuggestion = {
    namespace: string;
};
export type NamespaceLengthLimits = {
    max_length: number;
};
export type DataOutputResultStringRequest = {
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
export type DataOutputUpdate = {
    name: string;
    description: string;
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
    data_output?: DataOutput | null;
};
export type DataOutputStatusUpdate = {
    status: DataOutputStatus;
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
    useGetDataOutputsApiDataProductsIdDataOutputsGetQuery,
    useLazyGetDataOutputsApiDataProductsIdDataOutputsGetQuery,
    useGetDataOutputsApiDataOutputsGetQuery,
    useLazyGetDataOutputsApiDataOutputsGetQuery,
    useGetDataOutputNamespaceSuggestionApiDataOutputsNamespaceSuggestionGetQuery,
    useLazyGetDataOutputNamespaceSuggestionApiDataOutputsNamespaceSuggestionGetQuery,
    useGetDataOutputNamespaceLengthLimitsApiDataOutputsNamespaceLengthLimitsGetQuery,
    useLazyGetDataOutputNamespaceLengthLimitsApiDataOutputsNamespaceLengthLimitsGetQuery,
    useGetDataOutputResultStringApiDataOutputsResultStringPostMutation,
    useGetDataOutputApiDataOutputsIdGetQuery,
    useLazyGetDataOutputApiDataOutputsIdGetQuery,
    useRemoveDataOutputApiDataOutputsIdDeleteMutation,
    useUpdateDataOutputApiDataOutputsIdPutMutation,
    useGetEventHistoryApiDataOutputsIdHistoryGetQuery,
    useLazyGetEventHistoryApiDataOutputsIdHistoryGetQuery,
    useUpdateDataOutputStatusApiDataOutputsIdStatusPutMutation,
    useLinkDatasetToDataOutputApiDataOutputsIdDatasetDatasetIdPostMutation,
    useUnlinkDatasetFromDataOutputApiDataOutputsIdDatasetDatasetIdDeleteMutation,
    useGetGraphDataApiDataOutputsIdGraphGetQuery,
    useLazyGetGraphDataApiDataOutputsIdGraphGetQuery,
} = injectedRtkApi;
