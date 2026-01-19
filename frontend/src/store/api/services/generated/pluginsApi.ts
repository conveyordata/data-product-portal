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
export type PlatformTile = {
  label: string;
  value: string;
  icon_name: string;
  has_menu?: boolean;
  has_config?: boolean;
  children?: PlatformTile[];
};
export type PlatformTileResponse = {
  platform_tiles: PlatformTile[];
};
export type UiElementType = "string" | "select" | "checkbox";
export type UiElementCheckbox = {
  type?: UiElementType;
  initial_value?: boolean | null;
};
export type UiElementSelect = {
  type?: UiElementType;
  max_count?: number | null;
};
export type UiElementString = {
  type?: UiElementType;
  initial_value?: string | null;
};
export type FieldDependency = {
  field_name: string;
  value: any;
};
export type SelectOption = {
  label: string;
  value: string | boolean;
};
export type UiElementMetadata = {
  label: string;
  type: UiElementType;
  required: boolean;
  name: string;
  tooltip?: string | null;
  hidden?: boolean | null;
  checkbox?: UiElementCheckbox | null;
  select?: UiElementSelect | null;
  string?: UiElementString | null;
  depends_on?: FieldDependency[] | null;
  disabled?: boolean | null;
  use_namespace_when_not_source_aligned?: boolean | null;
  options?: SelectOption[] | null;
};
export type UiElementMetadataResponse = {
  not_configured?: boolean;
  ui_metadata: UiElementMetadata[];
  plugin: string;
  result_label?: string;
  result_tooltip?: string;
  platform: string;
  display_name: string;
  icon_name: string;
  parent_platform?: string | null;
  platform_tile?: PlatformTile | null;
};
export type PluginResponse = {
  plugins: UiElementMetadataResponse[];
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export const {
  useGetPlatformTilesQuery,
  useLazyGetPlatformTilesQuery,
  useGetPluginsQuery,
  useLazyGetPluginsQuery,
  useGetPluginFormQuery,
  useLazyGetPluginFormQuery,
} = injectedRtkApi;
