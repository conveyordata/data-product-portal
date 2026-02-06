import { api } from "@/store/api/services/generated/configurationDomainsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getEnvironment: build.query<
      GetEnvironmentApiResponse,
      GetEnvironmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/environments/${queryArg}`,
      }),
    }),
    getEnvironmentConfigsById: build.query<
      GetEnvironmentConfigsByIdApiResponse,
      GetEnvironmentConfigsByIdApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/environments/configs/${queryArg}`,
      }),
    }),
    getEnvironmentPlatformServiceConfig: build.query<
      GetEnvironmentPlatformServiceConfigApiResponse,
      GetEnvironmentPlatformServiceConfigApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/environments/${queryArg.id}/platforms/${queryArg.platformId}/services/${queryArg.serviceId}/config`,
      }),
    }),
    getEnvironmentPlatformConfig: build.query<
      GetEnvironmentPlatformConfigApiResponse,
      GetEnvironmentPlatformConfigApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/environments/${queryArg.id}/platforms/${queryArg.platformId}/config`,
      }),
    }),
    getEnvironments: build.query<
      GetEnvironmentsApiResponse,
      GetEnvironmentsApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/environments` }),
    }),
    getEnvironmentConfigs: build.query<
      GetEnvironmentConfigsApiResponse,
      GetEnvironmentConfigsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/environments/${queryArg}/configs`,
      }),
    }),
    getEnvironmentPlatformServiceConfigForAllEnvs: build.query<
      GetEnvironmentPlatformServiceConfigForAllEnvsApiResponse,
      GetEnvironmentPlatformServiceConfigForAllEnvsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/environments/platforms/${queryArg.platformId}/services/${queryArg.serviceId}/config`,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetEnvironmentApiResponse =
  /** status 200 Successful Response */ Environment;
export type GetEnvironmentApiArg = string;
export type GetEnvironmentConfigsByIdApiResponse =
  /** status 200 Successful Response */ EnvironmentConfigsGetItem;
export type GetEnvironmentConfigsByIdApiArg = string;
export type GetEnvironmentPlatformServiceConfigApiResponse =
  /** status 200 Successful Response */ EnvironmentConfigsGetItem;
export type GetEnvironmentPlatformServiceConfigApiArg = {
  id: string;
  platformId: string;
  serviceId: string;
};
export type GetEnvironmentPlatformConfigApiResponse =
  /** status 200 Successful Response */ EnvironmentPlatformConfigGet;
export type GetEnvironmentPlatformConfigApiArg = {
  id: string;
  platformId: string;
};
export type GetEnvironmentsApiResponse =
  /** status 200 Successful Response */ EnvironmentsGet;
export type GetEnvironmentsApiArg = void;
export type GetEnvironmentConfigsApiResponse =
  /** status 200 Successful Response */ EnvironmentConfigsGet;
export type GetEnvironmentConfigsApiArg = string;
export type GetEnvironmentPlatformServiceConfigForAllEnvsApiResponse =
  /** status 200 Successful Response */ EnvironmentConfigsGet;
export type GetEnvironmentPlatformServiceConfigForAllEnvsApiArg = {
  platformId: string;
  serviceId: string;
};
export type Environment = {
  id: string;
  name: string;
  acronym: string;
  context: string;
  is_default?: boolean;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: any;
  ctx?: object;
};
export type HttpValidationError = {
  detail?: ValidationError[];
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
export type PlatformService = {
  id: string;
  name: string;
  platform: Platform;
  result_string_template: string;
  technical_info_template: string;
};
export type EnvironmentConfigsGetItem = {
  config: (
    | Awss3Config
    | AwsGlueConfig
    | DatabricksConfig
    | SnowflakeConfig
    | RedshiftConfig
  )[];
  id: string;
  platform: Platform;
  environment: Environment;
  service: PlatformService;
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
export type EnvironmentPlatformConfigGet = {
  config:
    | AwsEnvironmentPlatformConfiguration
    | DatabricksEnvironmentPlatformConfiguration;
  id: string;
  environment: Environment;
  platform: Platform;
};
export type EnvironmentGetItem = {
  id: string;
  name: string;
  acronym: string;
  context: string;
  is_default?: boolean;
};
export type EnvironmentsGet = {
  environments: EnvironmentGetItem[];
};
export type EnvironmentConfigsGet = {
  environment_configs: EnvironmentConfigsGetItem[];
};
export const {
  useGetEnvironmentQuery,
  useLazyGetEnvironmentQuery,
  useGetEnvironmentConfigsByIdQuery,
  useLazyGetEnvironmentConfigsByIdQuery,
  useGetEnvironmentPlatformServiceConfigQuery,
  useLazyGetEnvironmentPlatformServiceConfigQuery,
  useGetEnvironmentPlatformConfigQuery,
  useLazyGetEnvironmentPlatformConfigQuery,
  useGetEnvironmentsQuery,
  useLazyGetEnvironmentsQuery,
  useGetEnvironmentConfigsQuery,
  useLazyGetEnvironmentConfigsQuery,
  useGetEnvironmentPlatformServiceConfigForAllEnvsQuery,
  useLazyGetEnvironmentPlatformServiceConfigForAllEnvsQuery,
} = injectedRtkApi;
