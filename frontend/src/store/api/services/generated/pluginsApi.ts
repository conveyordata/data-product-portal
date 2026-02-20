import { api } from "@/store/api/services/generated/configurationTagsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getPlatformTiles: build.query<
      GetPlatformTilesApiResponse,
      GetPlatformTilesApiArg
    >({
      query: () => ({ url: `/api/v2/plugins/platform-tiles` }),
    }),
    getPlugins: build.query<GetPluginsApiResponse, GetPluginsApiArg>({
      query: () => ({ url: `/api/v2/plugins/` }),
    }),
    getPluginForm: build.query<GetPluginFormApiResponse, GetPluginFormApiArg>({
      query: (queryArg) => ({ url: `/api/v2/plugins/${queryArg}/form` }),
    }),
    getPluginUrl: build.query<GetPluginUrlApiResponse, GetPluginUrlApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/plugins/${queryArg.pluginName}/url`,
        params: {
          id: queryArg.id,
          environment: queryArg.environment,
        },
      }),
    }),
    renderTechnicalAssetAccessPath: build.mutation<
      RenderTechnicalAssetAccessPathApiResponse,
      RenderTechnicalAssetAccessPathApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/plugins/render_technical_asset_access_path`,
        method: "POST",
        body: queryArg,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetPlatformTilesApiResponse =
  /** status 200 Successful Response */ PlatformTileResponse;
export type GetPlatformTilesApiArg = void;
export type GetPluginsApiResponse =
  /** status 200 Successful Response */ PluginResponse;
export type GetPluginsApiArg = void;
export type GetPluginFormApiResponse =
  /** status 200 Successful Response */ UiElementMetadataResponse;
export type GetPluginFormApiArg = string;
export type GetPluginUrlApiResponse =
  /** status 200 Successful Response */ UrlResponse;
export type GetPluginUrlApiArg = {
  pluginName: string;
  id: string;
  environment?: string | null;
};
export type RenderTechnicalAssetAccessPathApiResponse =
  /** status 200 Successful Response */ RenderTechnicalAssetAccessPathResponse;
export type RenderTechnicalAssetAccessPathApiArg =
  RenderTechnicalAssetAccessPathRequest;
export type PlatformTile = {
  label: string;
  value: string;
  icon_name: string;
  has_environments?: boolean;
  has_config?: boolean;
  children?: PlatformTile[];
  show_in_form?: boolean;
};
export type PlatformTileResponse = {
  platform_tiles: PlatformTile[];
};
export type UiElementCheckbox = {
  initial_value?: boolean | null;
};
export type SelectOption = {
  label: string;
  value: string | boolean;
};
export type UiElementSelect = {
  max_count?: number | null;
  options?: SelectOption[] | null;
};
export type UiElementString = {
  initial_value?: string | null;
};
export type UiElementRadio = {
  max_count?: number | null;
  initial_value?: string | null;
  options?: SelectOption[] | null;
};
export type FieldDependency = {
  field_name: string;
  value: any;
};
export type UiElementMetadata = {
  label: string;
  type: UIElementType;
  required: boolean;
  name: string;
  tooltip?: string | null;
  hidden?: boolean | null;
  checkbox?: UiElementCheckbox | null;
  select?: UiElementSelect | null;
  string?: UiElementString | null;
  radio?: UiElementRadio | null;
  depends_on?: FieldDependency[] | null;
  disabled?: boolean | null;
  use_namespace_when_not_source_aligned?: boolean | null;
};
export type UiElementMetadataResponse = {
  not_configured?: boolean;
  ui_metadata: UiElementMetadata[];
  plugin: string;
  has_environments: boolean;
  result_label?: string;
  result_tooltip?: string;
  platform: string;
  display_name: string;
  icon_name: string;
  parent_platform?: string | null;
  platform_tile?: PlatformTile | null;
  show_in_form?: boolean;
  detailed_name: string;
};
export type PluginResponse = {
  plugins: UiElementMetadataResponse[];
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
export type UrlResponse = {
  url: string;
};
export type RenderTechnicalAssetAccessPathResponse = {
  technical_asset_access_path: string;
};
export type DatabricksTechnicalAssetConfiguration = {
  configuration_type: "DatabricksTechnicalAssetConfiguration";
  catalog: string;
  schema?: string;
  table?: string;
  bucket_identifier?: string;
  catalog_path?: string;
  table_path?: string;
  access_granularity: AccessGranularity;
};
export type GlueTechnicalAssetConfiguration = {
  configuration_type: "GlueTechnicalAssetConfiguration";
  database: string;
  database_suffix?: string;
  table?: string;
  bucket_identifier?: string;
  database_path?: string;
  table_path?: string;
  access_granularity: AccessGranularity;
};
export type RedshiftTechnicalAssetConfiguration = {
  configuration_type: "RedshiftTechnicalAssetConfiguration";
  database: string;
  schema?: string;
  table?: string;
  bucket_identifier?: string;
  database_path?: string;
  table_path?: string;
  access_granularity: AccessGranularity;
};
export type S3TechnicalAssetConfiguration = {
  configuration_type: "S3TechnicalAssetConfiguration";
  bucket: string;
  suffix?: string;
  path: string;
};
export type SnowflakeTechnicalAssetConfiguration = {
  configuration_type: "SnowflakeTechnicalAssetConfiguration";
  database: string;
  schema?: string;
  table?: string;
  bucket_identifier?: string;
  database_path?: string;
  table_path?: string;
  access_granularity: AccessGranularity;
};
export type RenderTechnicalAssetAccessPathRequest = {
  platform_id: string;
  service_id: string;
  configuration:
    | ({
        configuration_type: "DatabricksTechnicalAssetConfiguration";
      } & DatabricksTechnicalAssetConfiguration)
    | ({
        configuration_type: "GlueTechnicalAssetConfiguration";
      } & GlueTechnicalAssetConfiguration)
    | ({
        configuration_type: "RedshiftTechnicalAssetConfiguration";
      } & RedshiftTechnicalAssetConfiguration)
    | ({
        configuration_type: "S3TechnicalAssetConfiguration";
      } & S3TechnicalAssetConfiguration)
    | ({
        configuration_type: "SnowflakeTechnicalAssetConfiguration";
      } & SnowflakeTechnicalAssetConfiguration);
};
export enum UIElementType {
  String = "string",
  Select = "select",
  Checkbox = "checkbox",
  Radio = "radio",
}
export enum AccessGranularity {
  Schema = "schema",
  Table = "table",
}
export const {
  useGetPlatformTilesQuery,
  useLazyGetPlatformTilesQuery,
  useGetPluginsQuery,
  useLazyGetPluginsQuery,
  useGetPluginFormQuery,
  useLazyGetPluginFormQuery,
  useGetPluginUrlQuery,
  useLazyGetPluginUrlQuery,
  useRenderTechnicalAssetAccessPathMutation,
} = injectedRtkApi;
