import { api } from '@/store/api/services/generated/datasetsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getDataProductsApiDataProductsGet: build.query<
            GetDataProductsApiDataProductsGetApiResponse,
            GetDataProductsApiDataProductsGetApiArg
        >({
            query: () => ({ url: '/api/data_products' }),
        }),
        createDataProductApiDataProductsPost: build.mutation<
            CreateDataProductApiDataProductsPostApiResponse,
            CreateDataProductApiDataProductsPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_products',
                method: 'POST',
                body: queryArg.dataProductCreate,
            }),
        }),
        getDataProductNamespaceSuggestionApiDataProductsNamespaceSuggestionGet: build.query<
            GetDataProductNamespaceSuggestionApiDataProductsNamespaceSuggestionGetApiResponse,
            GetDataProductNamespaceSuggestionApiDataProductsNamespaceSuggestionGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_products/namespace_suggestion',
                params: {
                    name: queryArg.name,
                },
            }),
        }),
        validateDataProductNamespaceApiDataProductsValidateNamespaceGet: build.query<
            ValidateDataProductNamespaceApiDataProductsValidateNamespaceGetApiResponse,
            ValidateDataProductNamespaceApiDataProductsValidateNamespaceGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_products/validate_namespace',
                params: {
                    namespace: queryArg['namespace'],
                },
            }),
        }),
        getDataProductNamespaceLengthLimitsApiDataProductsNamespaceLengthLimitsGet: build.query<
            GetDataProductNamespaceLengthLimitsApiDataProductsNamespaceLengthLimitsGetApiResponse,
            GetDataProductNamespaceLengthLimitsApiDataProductsNamespaceLengthLimitsGetApiArg
        >({
            query: () => ({ url: '/api/data_products/namespace_length_limits' }),
        }),
        getUserDataProductsApiDataProductsUserUserIdGet: build.query<
            GetUserDataProductsApiDataProductsUserUserIdGetApiResponse,
            GetUserDataProductsApiDataProductsUserUserIdGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/user/${queryArg.userId}`,
            }),
        }),
        getDataProductApiDataProductsIdGet: build.query<
            GetDataProductApiDataProductsIdGetApiResponse,
            GetDataProductApiDataProductsIdGetApiArg
        >({
            query: (queryArg) => ({ url: `/api/data_products/${queryArg.id}` }),
        }),
        removeDataProductApiDataProductsIdDelete: build.mutation<
            RemoveDataProductApiDataProductsIdDeleteApiResponse,
            RemoveDataProductApiDataProductsIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
        updateDataProductApiDataProductsIdPut: build.mutation<
            UpdateDataProductApiDataProductsIdPutApiResponse,
            UpdateDataProductApiDataProductsIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.dataProductUpdate,
            }),
        }),
        getEventHistoryApiDataProductsIdHistoryGet: build.query<
            GetEventHistoryApiDataProductsIdHistoryGetApiResponse,
            GetEventHistoryApiDataProductsIdHistoryGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/history`,
            }),
        }),
        createDataOutputApiDataProductsIdDataOutputPost: build.mutation<
            CreateDataOutputApiDataProductsIdDataOutputPostApiResponse,
            CreateDataOutputApiDataProductsIdDataOutputPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/data_output`,
                method: 'POST',
                body: queryArg.dataOutputCreate,
            }),
        }),
        validateDataOutputNamespaceApiDataProductsIdDataOutputValidateNamespaceGet: build.query<
            ValidateDataOutputNamespaceApiDataProductsIdDataOutputValidateNamespaceGetApiResponse,
            ValidateDataOutputNamespaceApiDataProductsIdDataOutputValidateNamespaceGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/data_output/validate_namespace`,
                params: {
                    namespace: queryArg['namespace'],
                },
            }),
        }),
        updateDataProductAboutApiDataProductsIdAboutPut: build.mutation<
            UpdateDataProductAboutApiDataProductsIdAboutPutApiResponse,
            UpdateDataProductAboutApiDataProductsIdAboutPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/about`,
                method: 'PUT',
                body: queryArg.dataProductAboutUpdate,
            }),
        }),
        updateDataProductStatusApiDataProductsIdStatusPut: build.mutation<
            UpdateDataProductStatusApiDataProductsIdStatusPutApiResponse,
            UpdateDataProductStatusApiDataProductsIdStatusPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/status`,
                method: 'PUT',
                body: queryArg.dataProductStatusUpdate,
            }),
        }),
        updateDataProductUsageApiDataProductsIdUsagePut: build.mutation<
            UpdateDataProductUsageApiDataProductsIdUsagePutApiResponse,
            UpdateDataProductUsageApiDataProductsIdUsagePutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/usage`,
                method: 'PUT',
                body: queryArg.dataProductUsageUpdate,
            }),
        }),
        linkDatasetToDataProductApiDataProductsIdDatasetDatasetIdPost: build.mutation<
            LinkDatasetToDataProductApiDataProductsIdDatasetDatasetIdPostApiResponse,
            LinkDatasetToDataProductApiDataProductsIdDatasetDatasetIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/dataset/${queryArg.datasetId}`,
                method: 'POST',
            }),
        }),
        unlinkDatasetFromDataProductApiDataProductsIdDatasetDatasetIdDelete: build.mutation<
            UnlinkDatasetFromDataProductApiDataProductsIdDatasetDatasetIdDeleteApiResponse,
            UnlinkDatasetFromDataProductApiDataProductsIdDatasetDatasetIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/dataset/${queryArg.datasetId}`,
                method: 'DELETE',
            }),
        }),
        getRoleApiDataProductsIdRoleGet: build.query<
            GetRoleApiDataProductsIdRoleGetApiResponse,
            GetRoleApiDataProductsIdRoleGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/role`,
                params: {
                    environment: queryArg.environment,
                },
            }),
        }),
        getSigninUrlApiDataProductsIdSigninUrlGet: build.query<
            GetSigninUrlApiDataProductsIdSigninUrlGetApiResponse,
            GetSigninUrlApiDataProductsIdSigninUrlGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/signin_url`,
                params: {
                    environment: queryArg.environment,
                },
            }),
        }),
        getConveyorIdeUrlApiDataProductsIdConveyorIdeUrlGet: build.query<
            GetConveyorIdeUrlApiDataProductsIdConveyorIdeUrlGetApiResponse,
            GetConveyorIdeUrlApiDataProductsIdConveyorIdeUrlGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/conveyor_ide_url`,
            }),
        }),
        getDatabricksWorkspaceUrlApiDataProductsIdDatabricksWorkspaceUrlGet: build.query<
            GetDatabricksWorkspaceUrlApiDataProductsIdDatabricksWorkspaceUrlGetApiResponse,
            GetDatabricksWorkspaceUrlApiDataProductsIdDatabricksWorkspaceUrlGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/databricks_workspace_url`,
                params: {
                    environment: queryArg.environment,
                },
            }),
        }),
        getSnowflakeUrlApiDataProductsIdSnowflakeUrlGet: build.query<
            GetSnowflakeUrlApiDataProductsIdSnowflakeUrlGetApiResponse,
            GetSnowflakeUrlApiDataProductsIdSnowflakeUrlGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/snowflake_url`,
                params: {
                    environment: queryArg.environment,
                },
            }),
        }),
        getDataOutputsApiDataProductsIdDataOutputsGet: build.query<
            GetDataOutputsApiDataProductsIdDataOutputsGetApiResponse,
            GetDataOutputsApiDataProductsIdDataOutputsGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/data_outputs`,
            }),
        }),
        getGraphDataApiDataProductsIdGraphGet: build.query<
            GetGraphDataApiDataProductsIdGraphGetApiResponse,
            GetGraphDataApiDataProductsIdGraphGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/graph`,
                params: {
                    level: queryArg.level,
                },
            }),
        }),
        setValueForDataProductApiDataProductsIdSettingsSettingIdPost: build.mutation<
            SetValueForDataProductApiDataProductsIdSettingsSettingIdPostApiResponse,
            SetValueForDataProductApiDataProductsIdSettingsSettingIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/settings/${queryArg.settingId}`,
                method: 'POST',
                params: {
                    value: queryArg.value,
                },
            }),
        }),
        getDataProductsTypesApiDataProductTypesGet: build.query<
            GetDataProductsTypesApiDataProductTypesGetApiResponse,
            GetDataProductsTypesApiDataProductTypesGetApiArg
        >({
            query: () => ({ url: '/api/data_product_types' }),
        }),
        getDataProductsLifecyclesApiDataProductLifecyclesGet: build.query<
            GetDataProductsLifecyclesApiDataProductLifecyclesGetApiResponse,
            GetDataProductsLifecyclesApiDataProductLifecyclesGetApiArg
        >({
            query: () => ({ url: '/api/data_product_lifecycles' }),
        }),
        getDataProductsSettingsApiDataProductSettingsGet: build.query<
            GetDataProductsSettingsApiDataProductSettingsGetApiResponse,
            GetDataProductsSettingsApiDataProductSettingsGetApiArg
        >({
            query: () => ({ url: '/api/data_product_settings' }),
        }),
        createDataProductSettingApiDataProductSettingsPost: build.mutation<
            CreateDataProductSettingApiDataProductSettingsPostApiResponse,
            CreateDataProductSettingApiDataProductSettingsPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_product_settings',
                method: 'POST',
                body: queryArg.dataProductSettingCreate,
            }),
        }),
        getDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGet: build.query<
            GetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetApiResponse,
            GetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_product_settings/namespace_suggestion',
                params: {
                    name: queryArg.name,
                },
            }),
        }),
        validateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGet: build.query<
            ValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetApiResponse,
            ValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_product_settings/validate_namespace',
                params: {
                    namespace: queryArg['namespace'],
                    scope: queryArg.scope,
                },
            }),
        }),
        getDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGet: build.query<
            GetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetApiResponse,
            GetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetApiArg
        >({
            query: () => ({
                url: '/api/data_product_settings/namespace_length_limits',
            }),
        }),
        updateDataProductSettingApiDataProductSettingsIdPut: build.mutation<
            UpdateDataProductSettingApiDataProductSettingsIdPutApiResponse,
            UpdateDataProductSettingApiDataProductSettingsIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_settings/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.dataProductSettingUpdate,
            }),
        }),
        deleteDataProductSettingApiDataProductSettingsIdDelete: build.mutation<
            DeleteDataProductSettingApiDataProductSettingsIdDeleteApiResponse,
            DeleteDataProductSettingApiDataProductSettingsIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_settings/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductsApiDataProductsGetApiResponse = /** status 200 Successful Response */ DataProductsGet[];
export type GetDataProductsApiDataProductsGetApiArg = void;
export type CreateDataProductApiDataProductsPostApiResponse = /** status 200 Data Product successfully created */ {
    [key: string]: string;
};
export type CreateDataProductApiDataProductsPostApiArg = {
    dataProductCreate: DataProductCreate;
};
export type GetDataProductNamespaceSuggestionApiDataProductsNamespaceSuggestionGetApiResponse =
    /** status 200 Successful Response */ NamespaceSuggestion;
export type GetDataProductNamespaceSuggestionApiDataProductsNamespaceSuggestionGetApiArg = {
    name: string;
};
export type ValidateDataProductNamespaceApiDataProductsValidateNamespaceGetApiResponse =
    /** status 200 Successful Response */ NamespaceValidation;
export type ValidateDataProductNamespaceApiDataProductsValidateNamespaceGetApiArg = {
    namespace: string;
};
export type GetDataProductNamespaceLengthLimitsApiDataProductsNamespaceLengthLimitsGetApiResponse =
    /** status 200 Successful Response */ NamespaceLengthLimits;
export type GetDataProductNamespaceLengthLimitsApiDataProductsNamespaceLengthLimitsGetApiArg = void;
export type GetUserDataProductsApiDataProductsUserUserIdGetApiResponse =
    /** status 200 Successful Response */ DataProductsGet[];
export type GetUserDataProductsApiDataProductsUserUserIdGetApiArg = {
    userId: string;
};
export type GetDataProductApiDataProductsIdGetApiResponse = /** status 200 Successful Response */ DataProductGet;
export type GetDataProductApiDataProductsIdGetApiArg = {
    id: string;
};
export type RemoveDataProductApiDataProductsIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveDataProductApiDataProductsIdDeleteApiArg = {
    id: string;
};
export type UpdateDataProductApiDataProductsIdPutApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type UpdateDataProductApiDataProductsIdPutApiArg = {
    id: string;
    dataProductUpdate: DataProductUpdate;
};
export type GetEventHistoryApiDataProductsIdHistoryGetApiResponse = /** status 200 Successful Response */ EventGet[];
export type GetEventHistoryApiDataProductsIdHistoryGetApiArg = {
    id: string;
};
export type CreateDataOutputApiDataProductsIdDataOutputPostApiResponse =
    /** status 200 DataOutput successfully created */ {
        [key: string]: string;
    };
export type CreateDataOutputApiDataProductsIdDataOutputPostApiArg = {
    id: string;
    dataOutputCreate: DataOutputCreate;
};
export type ValidateDataOutputNamespaceApiDataProductsIdDataOutputValidateNamespaceGetApiResponse =
    /** status 200 Successful Response */ NamespaceValidation;
export type ValidateDataOutputNamespaceApiDataProductsIdDataOutputValidateNamespaceGetApiArg = {
    id: string;
    namespace: string;
};
export type UpdateDataProductAboutApiDataProductsIdAboutPutApiResponse = /** status 200 Successful Response */ any;
export type UpdateDataProductAboutApiDataProductsIdAboutPutApiArg = {
    id: string;
    dataProductAboutUpdate: DataProductAboutUpdate;
};
export type UpdateDataProductStatusApiDataProductsIdStatusPutApiResponse = /** status 200 Successful Response */ any;
export type UpdateDataProductStatusApiDataProductsIdStatusPutApiArg = {
    id: string;
    dataProductStatusUpdate: DataProductStatusUpdate;
};
export type UpdateDataProductUsageApiDataProductsIdUsagePutApiResponse = /** status 200 Successful Response */ any;
export type UpdateDataProductUsageApiDataProductsIdUsagePutApiArg = {
    id: string;
    dataProductUsageUpdate: DataProductUsageUpdate;
};
export type LinkDatasetToDataProductApiDataProductsIdDatasetDatasetIdPostApiResponse =
    /** status 200 Successful Response */ {
        [key: string]: string;
    };
export type LinkDatasetToDataProductApiDataProductsIdDatasetDatasetIdPostApiArg = {
    id: string;
    datasetId: string;
};
export type UnlinkDatasetFromDataProductApiDataProductsIdDatasetDatasetIdDeleteApiResponse =
    /** status 200 Successful Response */ any;
export type UnlinkDatasetFromDataProductApiDataProductsIdDatasetDatasetIdDeleteApiArg = {
    id: string;
    datasetId: string;
};
export type GetRoleApiDataProductsIdRoleGetApiResponse = /** status 200 Successful Response */ string;
export type GetRoleApiDataProductsIdRoleGetApiArg = {
    id: string;
    environment: string;
};
export type GetSigninUrlApiDataProductsIdSigninUrlGetApiResponse = /** status 200 Successful Response */ string;
export type GetSigninUrlApiDataProductsIdSigninUrlGetApiArg = {
    id: string;
    environment: string;
};
export type GetConveyorIdeUrlApiDataProductsIdConveyorIdeUrlGetApiResponse =
    /** status 200 Successful Response */ string;
export type GetConveyorIdeUrlApiDataProductsIdConveyorIdeUrlGetApiArg = {
    id: string;
};
export type GetDatabricksWorkspaceUrlApiDataProductsIdDatabricksWorkspaceUrlGetApiResponse =
    /** status 200 Successful Response */ string;
export type GetDatabricksWorkspaceUrlApiDataProductsIdDatabricksWorkspaceUrlGetApiArg = {
    id: string;
    environment: string;
};
export type GetSnowflakeUrlApiDataProductsIdSnowflakeUrlGetApiResponse = /** status 200 Successful Response */ string;
export type GetSnowflakeUrlApiDataProductsIdSnowflakeUrlGetApiArg = {
    id: string;
    environment: string;
};
export type GetDataOutputsApiDataProductsIdDataOutputsGetApiResponse =
    /** status 200 Successful Response */ DataOutputGetRead[];
export type GetDataOutputsApiDataProductsIdDataOutputsGetApiArg = {
    id: string;
};
export type GetGraphDataApiDataProductsIdGraphGetApiResponse = /** status 200 Successful Response */ Graph;
export type GetGraphDataApiDataProductsIdGraphGetApiArg = {
    id: string;
    level?: number;
};
export type SetValueForDataProductApiDataProductsIdSettingsSettingIdPostApiResponse =
    /** status 200 Successful Response */ any;
export type SetValueForDataProductApiDataProductsIdSettingsSettingIdPostApiArg = {
    id: string;
    settingId: string;
    value: string;
};
export type GetDataProductsTypesApiDataProductTypesGetApiResponse =
    /** status 200 Successful Response */ DataProductTypesGet[];
export type GetDataProductsTypesApiDataProductTypesGetApiArg = void;
export type GetDataProductsLifecyclesApiDataProductLifecyclesGetApiResponse =
    /** status 200 Successful Response */ DataProductLifeCyclesGet[];
export type GetDataProductsLifecyclesApiDataProductLifecyclesGetApiArg = void;
export type GetDataProductsSettingsApiDataProductSettingsGetApiResponse =
    /** status 200 Successful Response */ DataProductSettingsGet[];
export type GetDataProductsSettingsApiDataProductSettingsGetApiArg = void;
export type CreateDataProductSettingApiDataProductSettingsPostApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type CreateDataProductSettingApiDataProductSettingsPostApiArg = {
    dataProductSettingCreate: DataProductSettingCreate;
};
export type GetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetApiResponse =
    /** status 200 Successful Response */ NamespaceSuggestion;
export type GetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetApiArg = {
    name: string;
};
export type ValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetApiResponse =
    /** status 200 Successful Response */ NamespaceValidation;
export type ValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetApiArg = {
    namespace: string;
    scope: DataProductSettingScope;
};
export type GetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetApiResponse =
    /** status 200 Successful Response */ NamespaceLengthLimits;
export type GetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetApiArg = void;
export type UpdateDataProductSettingApiDataProductSettingsIdPutApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type UpdateDataProductSettingApiDataProductSettingsIdPutApiArg = {
    id: string;
    dataProductSettingUpdate: DataProductSettingUpdate;
};
export type DeleteDataProductSettingApiDataProductSettingsIdDeleteApiResponse =
    /** status 200 Successful Response */ any;
export type DeleteDataProductSettingApiDataProductSettingsIdDeleteApiArg = {
    id: string;
};
export type DataProductStatus = 'pending' | 'active' | 'archived';
export type Tag = {
    id: string;
    value: string;
};
export type Domain = {
    id: string;
    name: string;
    description: string;
};
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
export type DataProductsGet = {
    id: string;
    name: string;
    description: string;
    namespace: string;
    status: DataProductStatus;
    tags: Tag[];
    usage: string | null;
    domain: Domain;
    type: DataProductType;
    lifecycle: DataProductLifeCycle | null;
    data_product_settings: DataProductSettingValue[];
    user_count: number;
    dataset_count: number;
    data_outputs_count: number;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type DataProductCreate = {
    name: string;
    namespace: string;
    description: string;
    type_id: string;
    about?: string | null;
    domain_id: string;
    tag_ids: string[];
    lifecycle_id: string;
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
export type DatasetLinks = {
    id: string;
    data_product_id: string;
    dataset_id: string;
    status: DecisionStatus;
    dataset: Dataset;
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
export type DataOutputDatasetAssociation = {
    id: string;
    dataset_id: string;
    data_output_id: string;
    status: DecisionStatus;
};
export type DataOutputLinks = {
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
    dataset_links: DataOutputDatasetAssociation[];
};
export type DataProductGet = {
    id: string;
    name: string;
    description: string;
    namespace: string;
    status: DataProductStatus;
    tags: Tag[];
    usage: string | null;
    domain: Domain;
    type: DataProductType;
    lifecycle: DataProductLifeCycle | null;
    data_product_settings: DataProductSettingValue[];
    about: string | null;
    dataset_links: DatasetLinks[];
    data_outputs: DataOutputLinks[];
    rolled_up_tags: Tag[];
};
export type DataProductUpdate = {
    name: string;
    namespace: string;
    description: string;
    type_id: string;
    about?: string | null;
    domain_id: string;
    tag_ids: string[];
    lifecycle_id: string;
};
export type EventReferenceEntity = 'data_product' | 'dataset' | 'data_output' | 'user';
export type User = {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
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
export type DataOutputCreate = {
    name: string;
    description: string;
    namespace: string;
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
    sourceAligned: boolean;
    tag_ids: string[];
};
export type DataProductAboutUpdate = {
    about: string;
};
export type DataProductStatusUpdate = {
    status: DataProductStatus;
};
export type DataProductUsageUpdate = {
    usage: string;
};
export type DatasetLink = {
    id: string;
    dataset_id: string;
    data_output_id: string;
    status: DecisionStatus;
    dataset: Dataset;
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
export type DataProductTypesGet = {
    id: string;
    name: string;
    description: string;
    icon_key: DataProductIconKey;
    data_product_count: number;
};
export type DataProductLifeCyclesGet = {
    id: string;
    value: number;
    name: string;
    color: string;
    is_default: boolean;
};
export type DataProductSettingsGet = {
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
export type DataProductSettingCreate = {
    category: string;
    type: DataProductSettingType;
    tooltip: string;
    namespace: string;
    name: string;
    default: string;
    order?: number;
    scope: DataProductSettingScope;
};
export type DataProductSettingUpdate = {
    category: string;
    type: DataProductSettingType;
    tooltip: string;
    namespace: string;
    name: string;
    default: string;
    order?: number;
    scope: DataProductSettingScope;
};
export const {
    useGetDataProductsApiDataProductsGetQuery,
    useLazyGetDataProductsApiDataProductsGetQuery,
    useCreateDataProductApiDataProductsPostMutation,
    useGetDataProductNamespaceSuggestionApiDataProductsNamespaceSuggestionGetQuery,
    useLazyGetDataProductNamespaceSuggestionApiDataProductsNamespaceSuggestionGetQuery,
    useValidateDataProductNamespaceApiDataProductsValidateNamespaceGetQuery,
    useLazyValidateDataProductNamespaceApiDataProductsValidateNamespaceGetQuery,
    useGetDataProductNamespaceLengthLimitsApiDataProductsNamespaceLengthLimitsGetQuery,
    useLazyGetDataProductNamespaceLengthLimitsApiDataProductsNamespaceLengthLimitsGetQuery,
    useGetUserDataProductsApiDataProductsUserUserIdGetQuery,
    useLazyGetUserDataProductsApiDataProductsUserUserIdGetQuery,
    useGetDataProductApiDataProductsIdGetQuery,
    useLazyGetDataProductApiDataProductsIdGetQuery,
    useRemoveDataProductApiDataProductsIdDeleteMutation,
    useUpdateDataProductApiDataProductsIdPutMutation,
    useGetEventHistoryApiDataProductsIdHistoryGetQuery,
    useLazyGetEventHistoryApiDataProductsIdHistoryGetQuery,
    useCreateDataOutputApiDataProductsIdDataOutputPostMutation,
    useValidateDataOutputNamespaceApiDataProductsIdDataOutputValidateNamespaceGetQuery,
    useLazyValidateDataOutputNamespaceApiDataProductsIdDataOutputValidateNamespaceGetQuery,
    useUpdateDataProductAboutApiDataProductsIdAboutPutMutation,
    useUpdateDataProductStatusApiDataProductsIdStatusPutMutation,
    useUpdateDataProductUsageApiDataProductsIdUsagePutMutation,
    useLinkDatasetToDataProductApiDataProductsIdDatasetDatasetIdPostMutation,
    useUnlinkDatasetFromDataProductApiDataProductsIdDatasetDatasetIdDeleteMutation,
    useGetRoleApiDataProductsIdRoleGetQuery,
    useLazyGetRoleApiDataProductsIdRoleGetQuery,
    useGetSigninUrlApiDataProductsIdSigninUrlGetQuery,
    useLazyGetSigninUrlApiDataProductsIdSigninUrlGetQuery,
    useGetConveyorIdeUrlApiDataProductsIdConveyorIdeUrlGetQuery,
    useLazyGetConveyorIdeUrlApiDataProductsIdConveyorIdeUrlGetQuery,
    useGetDatabricksWorkspaceUrlApiDataProductsIdDatabricksWorkspaceUrlGetQuery,
    useLazyGetDatabricksWorkspaceUrlApiDataProductsIdDatabricksWorkspaceUrlGetQuery,
    useGetSnowflakeUrlApiDataProductsIdSnowflakeUrlGetQuery,
    useLazyGetSnowflakeUrlApiDataProductsIdSnowflakeUrlGetQuery,
    useGetDataOutputsApiDataProductsIdDataOutputsGetQuery,
    useLazyGetDataOutputsApiDataProductsIdDataOutputsGetQuery,
    useGetGraphDataApiDataProductsIdGraphGetQuery,
    useLazyGetGraphDataApiDataProductsIdGraphGetQuery,
    useSetValueForDataProductApiDataProductsIdSettingsSettingIdPostMutation,
    useGetDataProductsTypesApiDataProductTypesGetQuery,
    useLazyGetDataProductsTypesApiDataProductTypesGetQuery,
    useGetDataProductsLifecyclesApiDataProductLifecyclesGetQuery,
    useLazyGetDataProductsLifecyclesApiDataProductLifecyclesGetQuery,
    useGetDataProductsSettingsApiDataProductSettingsGetQuery,
    useLazyGetDataProductsSettingsApiDataProductSettingsGetQuery,
    useCreateDataProductSettingApiDataProductSettingsPostMutation,
    useGetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetQuery,
    useLazyGetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetQuery,
    useValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetQuery,
    useLazyValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetQuery,
    useGetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetQuery,
    useLazyGetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetQuery,
    useUpdateDataProductSettingApiDataProductSettingsIdPutMutation,
    useDeleteDataProductSettingApiDataProductSettingsIdDeleteMutation,
} = injectedRtkApi;
