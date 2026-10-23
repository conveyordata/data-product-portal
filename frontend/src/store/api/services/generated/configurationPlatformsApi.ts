import { api } from "@/store/api/services/generated/configurationEnvironmentsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getAllPlatforms: build.query<
      GetAllPlatformsApiResponse,
      GetAllPlatformsApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/platforms` }),
    }),
    getPlatformEnvironmentSettings: build.query<
      GetPlatformEnvironmentSettingsApiResponse,
      GetPlatformEnvironmentSettingsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/platforms/${queryArg.platformKey}/environments/${queryArg.environmentId}/settings`,
      }),
    }),
    updatePlatformEnvironmentSettings: build.mutation<
      UpdatePlatformEnvironmentSettingsApiResponse,
      UpdatePlatformEnvironmentSettingsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/platforms/${queryArg.platformKey}/environments/${queryArg.environmentId}/settings`,
        method: "PUT",
        body: queryArg.settings,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetAllPlatformsApiResponse =
  /** status 200 Successful Response */ GetAllPlatformsResponse;
export type GetAllPlatformsApiArg = void;
export type GetPlatformEnvironmentSettingsApiResponse =
  /** status 200 Successful Response */ PlatformEnvironmentSettings;
export type GetPlatformEnvironmentSettingsApiArg = {
  platformKey: string;
  environmentId: string;
};
export type UpdatePlatformEnvironmentSettingsApiResponse =
  /** status 200 Successful Response */ PlatformEnvironmentSettings;
export type UpdatePlatformEnvironmentSettingsApiArg = {
  platformKey: string;
  environmentId: string;
  settings: {
    [key: string]: any;
  };
};
export type OverridableProperty = {
  name: string;
  label: string;
  allowed_values: string[];
  default: string;
};
export type PlatformType = {
  kind: PlatformTypeKind;
  name: string;
  display_name: string;
  overridable_properties?: OverridableProperty[];
};
export type Platform = {
  key: string;
  display_name: string;
  icon_name: string;
  icon_data_uri: string | null;
  has_environments: boolean;
  settings_schema: {
    [key: string]: any;
  };
  types: PlatformType[];
};
export type GetAllPlatformsResponse = {
  platforms: Platform[];
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
export type PlatformEnvironmentSettings = {
  platform_key: string;
  environment_id: string;
  settings: {
    [key: string]: any;
  };
};
export enum PlatformTypeKind {
  Asset = "asset",
  Tool = "tool",
}
export const {
  useGetAllPlatformsQuery,
  useLazyGetAllPlatformsQuery,
  useGetPlatformEnvironmentSettingsQuery,
  useLazyGetPlatformEnvironmentSettingsQuery,
  useUpdatePlatformEnvironmentSettingsMutation,
} = injectedRtkApi;
