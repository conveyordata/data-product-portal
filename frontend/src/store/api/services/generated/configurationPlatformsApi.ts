import { api } from "@/store/api/services/generated/configurationEnvironmentsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getPlatformServiceConfig: build.query<
      GetPlatformServiceConfigApiResponse,
      GetPlatformServiceConfigApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/platforms/${queryArg.id}/services/${queryArg.serviceId}`,
      }),
    }),
    getSinglePlatformServiceConfiguration: build.query<
      GetSinglePlatformServiceConfigurationApiResponse,
      GetSinglePlatformServiceConfigurationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/platforms/configs/${queryArg}`,
      }),
    }),
    getAllPlatformServiceConfigurations: build.query<
      GetAllPlatformServiceConfigurationsApiResponse,
      GetAllPlatformServiceConfigurationsApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/platforms/configs` }),
    }),
    getAllPlatforms: build.query<
      GetAllPlatformsApiResponse,
      GetAllPlatformsApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/platforms` }),
    }),
    getPlatformServices: build.query<
      GetPlatformServicesApiResponse,
      GetPlatformServicesApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/platforms/${queryArg}/services`,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetPlatformServiceConfigApiResponse =
  /** status 200 Successful Response */ PlatformServiceConfiguration;
export type GetPlatformServiceConfigApiArg = {
  id: string;
  serviceId: string;
};
export type GetSinglePlatformServiceConfigurationApiResponse =
  /** status 200 Successful Response */ PlatformServiceConfiguration;
export type GetSinglePlatformServiceConfigurationApiArg = string;
export type GetAllPlatformServiceConfigurationsApiResponse =
  /** status 200 Successful Response */ GetAllPlatformServiceConfigurationsResponse;
export type GetAllPlatformServiceConfigurationsApiArg = void;
export type GetAllPlatformsApiResponse =
  /** status 200 Successful Response */ GetAllPlatformsResponse;
export type GetAllPlatformsApiArg = void;
export type GetPlatformServicesApiResponse =
  /** status 200 Successful Response */ GetPlatformServicesResponse;
export type GetPlatformServicesApiArg = string;
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
export type PlatformServiceConfiguration = {
  id: string;
  platform: Platform;
  service: PlatformService;
  config: string[];
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
export type GetAllPlatformServiceConfigurationsResponse = {
  platform_service_configurations: PlatformServiceConfiguration[];
};
export type GetAllPlatformsResponse = {
  platforms: Platform[];
};
export type GetPlatformServicesResponse = {
  platform_services: PlatformService[];
};
export const {
  useGetPlatformServiceConfigQuery,
  useLazyGetPlatformServiceConfigQuery,
  useGetSinglePlatformServiceConfigurationQuery,
  useLazyGetSinglePlatformServiceConfigurationQuery,
  useGetAllPlatformServiceConfigurationsQuery,
  useLazyGetAllPlatformServiceConfigurationsQuery,
  useGetAllPlatformsQuery,
  useLazyGetAllPlatformsQuery,
  useGetPlatformServicesQuery,
  useLazyGetPlatformServicesQuery,
} = injectedRtkApi;
