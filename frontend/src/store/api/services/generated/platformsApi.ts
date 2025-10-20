import { api } from '@/store/api/services/generated/environmentsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getEnvironmentPlatformServiceConfigApiEnvsIdPlatformsPlatformIdServicesServiceIdConfigGet: build.query<
            GetEnvironmentPlatformServiceConfigApiEnvsIdPlatformsPlatformIdServicesServiceIdConfigGetApiResponse,
            GetEnvironmentPlatformServiceConfigApiEnvsIdPlatformsPlatformIdServicesServiceIdConfigGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/envs/${queryArg.id}/platforms/${queryArg.platformId}/services/${queryArg.serviceId}/config`,
            }),
        }),
        getEnvironmentPlatformServiceConfigForAllEnvsApiEnvsPlatformsPlatformIdServicesServiceIdConfigGet: build.query<
            GetEnvironmentPlatformServiceConfigForAllEnvsApiEnvsPlatformsPlatformIdServicesServiceIdConfigGetApiResponse,
            GetEnvironmentPlatformServiceConfigForAllEnvsApiEnvsPlatformsPlatformIdServicesServiceIdConfigGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/envs/platforms/${queryArg.platformId}/services/${queryArg.serviceId}/config`,
            }),
        }),
        getEnvironmentPlatformConfigApiEnvsIdPlatformsPlatformIdConfigGet: build.query<
            GetEnvironmentPlatformConfigApiEnvsIdPlatformsPlatformIdConfigGetApiResponse,
            GetEnvironmentPlatformConfigApiEnvsIdPlatformsPlatformIdConfigGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/envs/${queryArg.id}/platforms/${queryArg.platformId}/config`,
            }),
        }),
        getAllPlatformsApiPlatformsGet: build.query<
            GetAllPlatformsApiPlatformsGetApiResponse,
            GetAllPlatformsApiPlatformsGetApiArg
        >({
            query: () => ({ url: '/api/platforms' }),
        }),
        getPlatformServicesApiPlatformsIdServicesGet: build.query<
            GetPlatformServicesApiPlatformsIdServicesGetApiResponse,
            GetPlatformServicesApiPlatformsIdServicesGetApiArg
        >({
            query: (queryArg) => ({ url: `/api/platforms/${queryArg.id}/services` }),
        }),
        getPlatformServiceConfigApiPlatformsIdServicesServiceIdGet: build.query<
            GetPlatformServiceConfigApiPlatformsIdServicesServiceIdGetApiResponse,
            GetPlatformServiceConfigApiPlatformsIdServicesServiceIdGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/platforms/${queryArg.id}/services/${queryArg.serviceId}`,
            }),
        }),
        getAllPlatformServiceConfigurationsApiPlatformsConfigsGet: build.query<
            GetAllPlatformServiceConfigurationsApiPlatformsConfigsGetApiResponse,
            GetAllPlatformServiceConfigurationsApiPlatformsConfigsGetApiArg
        >({
            query: () => ({ url: '/api/platforms/configs' }),
        }),
        getSinglePlatformServiceConfigurationApiPlatformsConfigsConfigIdGet: build.query<
            GetSinglePlatformServiceConfigurationApiPlatformsConfigsConfigIdGetApiResponse,
            GetSinglePlatformServiceConfigurationApiPlatformsConfigsConfigIdGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/platforms/configs/${queryArg.configId}`,
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetEnvironmentPlatformServiceConfigApiEnvsIdPlatformsPlatformIdServicesServiceIdConfigGetApiResponse =
    /** status 200 Successful Response */ EnvironmentPlatformServiceConfiguration;
export type GetEnvironmentPlatformServiceConfigApiEnvsIdPlatformsPlatformIdServicesServiceIdConfigGetApiArg = {
    id: string;
    platformId: string;
    serviceId: string;
};
export type GetEnvironmentPlatformServiceConfigForAllEnvsApiEnvsPlatformsPlatformIdServicesServiceIdConfigGetApiResponse =
    /** status 200 Successful Response */ EnvironmentPlatformServiceConfiguration[];
export type GetEnvironmentPlatformServiceConfigForAllEnvsApiEnvsPlatformsPlatformIdServicesServiceIdConfigGetApiArg = {
    platformId: string;
    serviceId: string;
};
export type GetEnvironmentPlatformConfigApiEnvsIdPlatformsPlatformIdConfigGetApiResponse =
    /** status 200 Successful Response */ EnvironmentPlatformConfiguration;
export type GetEnvironmentPlatformConfigApiEnvsIdPlatformsPlatformIdConfigGetApiArg = {
    id: string;
    platformId: string;
};
export type GetAllPlatformsApiPlatformsGetApiResponse = /** status 200 Successful Response */ Platform[];
export type GetAllPlatformsApiPlatformsGetApiArg = void;
export type GetPlatformServicesApiPlatformsIdServicesGetApiResponse =
    /** status 200 Successful Response */ PlatformService[];
export type GetPlatformServicesApiPlatformsIdServicesGetApiArg = {
    id: string;
};
export type GetPlatformServiceConfigApiPlatformsIdServicesServiceIdGetApiResponse =
    /** status 200 Successful Response */ PlatformServiceConfiguration;
export type GetPlatformServiceConfigApiPlatformsIdServicesServiceIdGetApiArg = {
    id: string;
    serviceId: string;
};
export type GetAllPlatformServiceConfigurationsApiPlatformsConfigsGetApiResponse =
    /** status 200 Successful Response */ PlatformServiceConfiguration[];
export type GetAllPlatformServiceConfigurationsApiPlatformsConfigsGetApiArg = void;
export type GetSinglePlatformServiceConfigurationApiPlatformsConfigsConfigIdGetApiResponse =
    /** status 200 Successful Response */ PlatformServiceConfiguration;
export type GetSinglePlatformServiceConfigurationApiPlatformsConfigsConfigIdGetApiArg = {
    configId: string;
};
export type Awss3Config = {
    identifier: string;
    bucket_name: string;
    bucket_arn: string;
    kms_key_arn: string;
    is_default: boolean;
};
export type AwsGlueConfig = {
    identifier: string;
    database_name: string;
    bucket_identifier: string;
    s3_path: string;
};
export type DatabricksConfig = {
    identifier: string;
};
export type SnowflakeConfig = {
    identifier: string;
    database_name: string;
};
export type RedshiftConfig = {
    identifier: string;
    database_name: string;
    bucket_identifier: string;
    s3_path: string;
};
export type Platform = {
    id: string;
    name: string;
};
export type Environment = {
    id: string;
    name: string;
    acronym: string;
    context: string;
    is_default?: boolean;
};
export type PlatformService = {
    id: string;
    name: string;
    platform: Platform;
    result_string_template: string;
    technical_info_template: string;
};
export type EnvironmentPlatformServiceConfiguration = {
    config: (Awss3Config | AwsGlueConfig | DatabricksConfig | SnowflakeConfig | RedshiftConfig)[];
    id: string;
    platform: Platform;
    environment: Environment;
    service: PlatformService;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type AwsEnvironmentPlatformConfiguration = {
    account_id: string;
    region: string;
    can_read_from: string[];
};
export type DatabricksEnvironmentPlatformConfiguration = {
    workspace_urls: {
        [key: string]: string;
    };
    account_id: string;
    metastore_id: string;
    credential_name: string;
};
export type EnvironmentPlatformConfiguration = {
    config: AwsEnvironmentPlatformConfiguration | DatabricksEnvironmentPlatformConfiguration;
    id: string;
    environment: Environment;
    platform: Platform;
};
export type PlatformServiceConfiguration = {
    id: string;
    platform: Platform;
    service: PlatformService;
    config: string[];
};
export const {
    useGetEnvironmentPlatformServiceConfigApiEnvsIdPlatformsPlatformIdServicesServiceIdConfigGetQuery,
    useLazyGetEnvironmentPlatformServiceConfigApiEnvsIdPlatformsPlatformIdServicesServiceIdConfigGetQuery,
    useGetEnvironmentPlatformServiceConfigForAllEnvsApiEnvsPlatformsPlatformIdServicesServiceIdConfigGetQuery,
    useLazyGetEnvironmentPlatformServiceConfigForAllEnvsApiEnvsPlatformsPlatformIdServicesServiceIdConfigGetQuery,
    useGetEnvironmentPlatformConfigApiEnvsIdPlatformsPlatformIdConfigGetQuery,
    useLazyGetEnvironmentPlatformConfigApiEnvsIdPlatformsPlatformIdConfigGetQuery,
    useGetAllPlatformsApiPlatformsGetQuery,
    useLazyGetAllPlatformsApiPlatformsGetQuery,
    useGetPlatformServicesApiPlatformsIdServicesGetQuery,
    useLazyGetPlatformServicesApiPlatformsIdServicesGetQuery,
    useGetPlatformServiceConfigApiPlatformsIdServicesServiceIdGetQuery,
    useLazyGetPlatformServiceConfigApiPlatformsIdServicesServiceIdGetQuery,
    useGetAllPlatformServiceConfigurationsApiPlatformsConfigsGetQuery,
    useLazyGetAllPlatformServiceConfigurationsApiPlatformsConfigsGetQuery,
    useGetSinglePlatformServiceConfigurationApiPlatformsConfigsConfigIdGetQuery,
    useLazyGetSinglePlatformServiceConfigurationApiPlatformsConfigsConfigIdGetQuery,
} = injectedRtkApi;
