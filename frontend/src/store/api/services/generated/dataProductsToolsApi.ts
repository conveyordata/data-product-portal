import { api } from "@/store/api/services/generated/dataProductsTechnicalAssetsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getDataProductTools: build.query<
      GetDataProductToolsApiResponse,
      GetDataProductToolsApiArg
    >({
      query: (queryArg) => ({ url: `/api/v2/data_products/${queryArg}/tools` }),
    }),
    createTool: build.mutation<CreateToolApiResponse, CreateToolApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/tools`,
        method: "POST",
        body: queryArg.createToolRequest,
      }),
    }),
    getTool: build.query<GetToolApiResponse, GetToolApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/tools/${queryArg.id}`,
      }),
    }),
    deleteTool: build.mutation<DeleteToolApiResponse, DeleteToolApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/tools/${queryArg.id}`,
        method: "DELETE",
      }),
    }),
    getToolEnvironmentConfiguration: build.query<
      GetToolEnvironmentConfigurationApiResponse,
      GetToolEnvironmentConfigurationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/tools/${queryArg.id}/environment-configuration`,
      }),
    }),
    updateToolEnvironmentConfiguration: build.mutation<
      UpdateToolEnvironmentConfigurationApiResponse,
      UpdateToolEnvironmentConfigurationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/tools/${queryArg.id}/environment-configuration`,
        method: "PUT",
        body: queryArg.updateToolEnvironmentConfigurationRequest,
      }),
    }),
    applyToolEnvironmentConfiguration: build.mutation<
      ApplyToolEnvironmentConfigurationApiResponse,
      ApplyToolEnvironmentConfigurationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/tools/${queryArg.id}/environments/${queryArg.environmentId}/apply`,
        method: "POST",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductToolsApiResponse =
  /** status 200 Successful Response */ GetToolsResponse;
export type GetDataProductToolsApiArg = string;
export type CreateToolApiResponse =
  /** status 200 Successful Response */ CreateToolResponse;
export type CreateToolApiArg = {
  dataProductId: string;
  createToolRequest: CreateToolRequest;
};
export type GetToolApiResponse = /** status 200 Successful Response */ Tool;
export type GetToolApiArg = {
  dataProductId: string;
  id: string;
};
export type DeleteToolApiResponse = /** status 200 Successful Response */ any;
export type DeleteToolApiArg = {
  dataProductId: string;
  id: string;
};
export type GetToolEnvironmentConfigurationApiResponse =
  /** status 200 Successful Response */ ToolEnvironmentConfiguration;
export type GetToolEnvironmentConfigurationApiArg = {
  dataProductId: string;
  id: string;
};
export type UpdateToolEnvironmentConfigurationApiResponse =
  /** status 200 Successful Response */ ToolEnvironmentConfiguration;
export type UpdateToolEnvironmentConfigurationApiArg = {
  dataProductId: string;
  id: string;
  updateToolEnvironmentConfigurationRequest: UpdateToolEnvironmentConfigurationRequest;
};
export type ApplyToolEnvironmentConfigurationApiResponse =
  /** status 200 Successful Response */ any;
export type ApplyToolEnvironmentConfigurationApiArg = {
  dataProductId: string;
  id: string;
  environmentId: string;
};
export type Tool = {
  id: string;
  name: string;
  description: string;
  data_product_id: string;
  platform_key: string;
  tool_type: string;
  base_values: {
    [key: string]: string;
  };
};
export type GetToolsResponse = {
  tools: Tool[];
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
export type CreateToolResponse = {
  id: string;
};
export type CreateToolRequest = {
  name: string;
  description?: string;
  platform_key: string;
  tool_type: string;
  base_values?: {
    [key: string]: string;
  };
};
export type EnvironmentPropertyValue = {
  id: string;
  name: string;
  acronym: string;
  override: string | null;
  effective_value: string;
};
export type OverridablePropertyConfiguration = {
  name: string;
  label: string;
  allowed_values: string[];
  default: string;
  base_value: string;
  environments: EnvironmentPropertyValue[];
};
export type ToolEnvironmentConfiguration = {
  properties: OverridablePropertyConfiguration[];
};
export type UpdateToolEnvironmentConfigurationRequest = {
  base_values?: {
    [key: string]: string;
  };
  overrides?: {
    [key: string]: {
      [key: string]: string;
    };
  };
};
export const {
  useGetDataProductToolsQuery,
  useLazyGetDataProductToolsQuery,
  useCreateToolMutation,
  useGetToolQuery,
  useLazyGetToolQuery,
  useDeleteToolMutation,
  useGetToolEnvironmentConfigurationQuery,
  useLazyGetToolEnvironmentConfigurationQuery,
  useUpdateToolEnvironmentConfigurationMutation,
  useApplyToolEnvironmentConfigurationMutation,
} = injectedRtkApi;
