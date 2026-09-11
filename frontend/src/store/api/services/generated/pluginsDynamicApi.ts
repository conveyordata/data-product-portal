import { api } from "@/store/api/services/generated/pluginsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    listPlugins: build.query<ListPluginsApiResponse, ListPluginsApiArg>({
      query: () => ({ url: `/api/v2/plugins/dynamic/` }),
    }),
    getPluginIcon: build.query<GetPluginIconApiResponse, GetPluginIconApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/plugins/dynamic/${queryArg}/icon`,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type ListPluginsApiResponse =
  /** status 200 Successful Response */ PluginListResponse;
export type ListPluginsApiArg = void;
export type GetPluginIconApiResponse =
  /** status 200 Successful Response */ any;
export type GetPluginIconApiArg = string;
export type PluginSummary = {
  key: string;
  display_name: string;
  fields: {
    [key: string]: any;
  }[];
};
export type PluginListResponse = {
  plugins: PluginSummary[];
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
export const {
  useListPluginsQuery,
  useLazyListPluginsQuery,
  useGetPluginIconQuery,
  useLazyGetPluginIconQuery,
} = injectedRtkApi;
