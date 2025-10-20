import { api } from "@/store/api/services/baseApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getDataProductNamespaceSuggestion: build.query<
      GetDataProductNamespaceSuggestionApiResponse,
      GetDataProductNamespaceSuggestionApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/namespace_suggestion`,
        params: {
          name: queryArg.name,
        },
      }),
    }),
    validateDataProductNamespace: build.query<
      ValidateDataProductNamespaceApiResponse,
      ValidateDataProductNamespaceApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/validate_namespace`,
        params: {
          namespace: queryArg["namespace"],
        },
      }),
    }),
    getDataProductNamespaceLengthLimits: build.query<
      GetDataProductNamespaceLengthLimitsApiResponse,
      GetDataProductNamespaceLengthLimitsApiArg
    >({
      query: () => ({ url: `/api/v2/data_products/namespace_length_limits` }),
    }),
    createDataProduct: build.mutation<
      CreateDataProductApiResponse,
      CreateDataProductApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products`,
        method: "POST",
        body: queryArg.dataProductCreate,
      }),
    }),
    getDataProducts: build.query<
      GetDataProductsApiResponse,
      GetDataProductsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products`,
        params: {
          filter_to_user_with_assigment: queryArg.filterToUserWithAssigment,
        },
      }),
    }),
    removeDataProduct: build.mutation<
      RemoveDataProductApiResponse,
      RemoveDataProductApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}`,
        method: "DELETE",
      }),
    }),
    updateDataProduct: build.mutation<
      UpdateDataProductApiResponse,
      UpdateDataProductApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}`,
        method: "PUT",
        body: queryArg.dataProductUpdate,
      }),
    }),
    getDataProduct: build.query<
      GetDataProductApiResponse,
      GetDataProductApiArg
    >({
      query: (queryArg) => ({ url: `/api/v2/data_products/${queryArg.id}` }),
    }),
    updateDataProductAbout: build.mutation<
      UpdateDataProductAboutApiResponse,
      UpdateDataProductAboutApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/about`,
        method: "PUT",
        body: queryArg.dataProductAboutUpdate,
      }),
    }),
    updateDataProductStatus: build.mutation<
      UpdateDataProductStatusApiResponse,
      UpdateDataProductStatusApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/status`,
        method: "PUT",
        body: queryArg.dataProductStatusUpdate,
      }),
    }),
    updateDataProductUsage: build.mutation<
      UpdateDataProductUsageApiResponse,
      UpdateDataProductUsageApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/usage`,
        method: "PUT",
        body: queryArg.dataProductUsageUpdate,
      }),
    }),
    getGraphData: build.query<GetGraphDataApiResponse, GetGraphDataApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/graph`,
        params: {
          level: queryArg.level,
        },
      }),
    }),
    setValueForDataProduct: build.mutation<
      SetValueForDataProductApiResponse,
      SetValueForDataProductApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/settings/${queryArg.settingId}`,
        method: "POST",
        params: {
          value: queryArg.value,
        },
      }),
    }),
    linkInputPortsToDataProduct: build.mutation<
      LinkInputPortsToDataProductApiResponse,
      LinkInputPortsToDataProductApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/link_input_ports`,
        method: "POST",
        body: queryArg.linkInputPortsToDataProduct,
      }),
    }),
    createTechnicalAsset: build.mutation<
      CreateTechnicalAssetApiResponse,
      CreateTechnicalAssetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/technical_asset`,
        method: "POST",
        body: queryArg.createTechnicalAssetRequest,
      }),
    }),
    getSigninUrl: build.query<GetSigninUrlApiResponse, GetSigninUrlApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/signin_url`,
        params: {
          environment: queryArg.environment,
        },
      }),
    }),
    getConveyorIdeUrl: build.query<
      GetConveyorIdeUrlApiResponse,
      GetConveyorIdeUrlApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/conveyor_ide_url`,
      }),
    }),
    getDatabricksWorkspaceUrl: build.query<
      GetDatabricksWorkspaceUrlApiResponse,
      GetDatabricksWorkspaceUrlApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/databricks_workspace_url`,
        params: {
          environment: queryArg.environment,
        },
      }),
    }),
    getSnowflakeUrl: build.query<
      GetSnowflakeUrlApiResponse,
      GetSnowflakeUrlApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/snowflake_url`,
        params: {
          environment: queryArg.environment,
        },
      }),
    }),
    getTechnicalAssets: build.query<
      GetTechnicalAssetsApiResponse,
      GetTechnicalAssetsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/technical_assets`,
      }),
    }),
    getDataProductInputPorts: build.query<
      GetDataProductInputPortsApiResponse,
      GetDataProductInputPortsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/input_ports`,
      }),
    }),
    getDataProductRolledUpTags: build.query<
      GetDataProductRolledUpTagsApiResponse,
      GetDataProductRolledUpTagsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/rolled_up_tags`,
      }),
    }),
    unlinkInputPortFromDataProduct: build.mutation<
      UnlinkInputPortFromDataProductApiResponse,
      UnlinkInputPortFromDataProductApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/input_ports/${queryArg.inputPortId}`,
        method: "DELETE",
      }),
    }),
    validateTechnicalAssetNamespace: build.query<
      ValidateTechnicalAssetNamespaceApiResponse,
      ValidateTechnicalAssetNamespaceApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.id}/technical_asset/validate_namespace`,
        params: {
          namespace: queryArg["namespace"],
        },
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductNamespaceSuggestionApiResponse =
  /** status 200 Successful Response */ NamespaceSuggestion;
export type GetDataProductNamespaceSuggestionApiArg = {
  name: string;
};
export type ValidateDataProductNamespaceApiResponse =
  /** status 200 Successful Response */ NamespaceValidation;
export type ValidateDataProductNamespaceApiArg = {
  namespace: string;
};
export type GetDataProductNamespaceLengthLimitsApiResponse =
  /** status 200 Successful Response */ NamespaceLengthLimits;
export type GetDataProductNamespaceLengthLimitsApiArg = void;
export type CreateDataProductApiResponse =
  /** status 200 Data Product successfully created */ CreateDataProductResponse;
export type CreateDataProductApiArg = {
  dataProductCreate: DataProductCreate;
};
export type GetDataProductsApiResponse =
  /** status 200 Successful Response */ GetDataProductsResponse;
export type GetDataProductsApiArg = {
  filterToUserWithAssigment?: string | null;
};
export type RemoveDataProductApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveDataProductApiArg = {
  id: string;
};
export type UpdateDataProductApiResponse =
  /** status 200 Successful Response */ UpdateDataProductResponse;
export type UpdateDataProductApiArg = {
  id: string;
  dataProductUpdate: DataProductUpdate;
};
export type GetDataProductApiResponse =
  /** status 200 Successful Response */ GetDataProductResponse;
export type GetDataProductApiArg = {
  id: string;
};
export type UpdateDataProductAboutApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateDataProductAboutApiArg = {
  id: string;
  dataProductAboutUpdate: DataProductAboutUpdate;
};
export type UpdateDataProductStatusApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateDataProductStatusApiArg = {
  id: string;
  dataProductStatusUpdate: DataProductStatusUpdate;
};
export type UpdateDataProductUsageApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateDataProductUsageApiArg = {
  id: string;
  dataProductUsageUpdate: DataProductUsageUpdate;
};
export type GetGraphDataApiResponse =
  /** status 200 Successful Response */ Graph;
export type GetGraphDataApiArg = {
  id: string;
  level?: number;
};
export type SetValueForDataProductApiResponse =
  /** status 200 Successful Response */ any;
export type SetValueForDataProductApiArg = {
  id: string;
  settingId: string;
  value: string;
};
export type LinkInputPortsToDataProductApiResponse =
  /** status 200 Successful Response */ LinkInputPortsToDataProductPost;
export type LinkInputPortsToDataProductApiArg = {
  id: string;
  linkInputPortsToDataProduct: LinkInputPortsToDataProduct;
};
export type CreateTechnicalAssetApiResponse =
  /** status 200 DataOutput successfully created */ CreateTechnicalAssetResponse;
export type CreateTechnicalAssetApiArg = {
  id: string;
  createTechnicalAssetRequest: CreateTechnicalAssetRequest;
};
export type GetSigninUrlApiResponse =
  /** status 200 Successful Response */ GetSigninUrlResponse;
export type GetSigninUrlApiArg = {
  id: string;
  environment: string;
};
export type GetConveyorIdeUrlApiResponse =
  /** status 200 Successful Response */ GetConveyorIdeUrlResponse;
export type GetConveyorIdeUrlApiArg = {
  id: string;
};
export type GetDatabricksWorkspaceUrlApiResponse =
  /** status 200 Successful Response */ GetDatabricksWorkspaceUrlResponse;
export type GetDatabricksWorkspaceUrlApiArg = {
  id: string;
  environment: string;
};
export type GetSnowflakeUrlApiResponse =
  /** status 200 Successful Response */ GetSnowflakeUrlResponse;
export type GetSnowflakeUrlApiArg = {
  id: string;
  environment: string;
};
export type GetTechnicalAssetsApiResponse =
  /** status 200 Successful Response */ GetTechnicalAssetsResponseRead;
export type GetTechnicalAssetsApiArg = {
  id: string;
};
export type GetDataProductInputPortsApiResponse =
  /** status 200 Successful Response */ GetDataProductInputPortsResponse;
export type GetDataProductInputPortsApiArg = {
  id: string;
};
export type GetDataProductRolledUpTagsApiResponse =
  /** status 200 Successful Response */ GetDataProductRolledUpTagsResponse;
export type GetDataProductRolledUpTagsApiArg = {
  id: string;
};
export type UnlinkInputPortFromDataProductApiResponse =
  /** status 200 Successful Response */ any;
export type UnlinkInputPortFromDataProductApiArg = {
  id: string;
  inputPortId: string;
};
export type ValidateTechnicalAssetNamespaceApiResponse =
  /** status 200 Successful Response */ NamespaceValidation;
export type ValidateTechnicalAssetNamespaceApiArg = {
  id: string;
  namespace: string;
};
export type NamespaceSuggestion = {
  namespace: string;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type NamespaceValidityType =
  | "VALID"
  | "INVALID_LENGTH"
  | "INVALID_CHARACTERS"
  | "DUPLICATE_NAMESPACE";
export type NamespaceValidation = {
  validity: NamespaceValidityType;
};
export type NamespaceLengthLimits = {
  max_length: number;
};
export type CreateDataProductResponse = {
  id: string;
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
export type DataProductStatus = "pending" | "active" | "archived";
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
  | "reporting"
  | "processing"
  | "exploration"
  | "ingestion"
  | "machine_learning"
  | "analytics"
  | "default";
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
export type DataProductSettingType = "checkbox" | "tags" | "input";
export type DataProductSettingScope = "dataproduct" | "dataset";
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
  data_product_setting_id: string;
  value: string;
  data_product_setting: DataProductSetting;
  data_product_id: string;
};
export type GetDataProductsResponseItem = {
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
  output_port_count: number;
  technical_asset_count: number;
};
export type GetDataProductsResponse = {
  data_products: GetDataProductsResponseItem[];
};
export type UpdateDataProductResponse = {
  id: string;
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
export type GetDataProductResponse = {
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
export type Edge = {
  id: string;
  source: string;
  target: string;
  animated: boolean;
  sourceHandle?: string;
  targetHandle?: string;
};
export type DataProduct = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: DataProductStatus;
  type: DataProductType;
};
export type User = {
  id: string;
  email: string;
  external_id: string;
  first_name: string;
  last_name: string;
  has_seen_tour: boolean;
  can_become_admin: boolean;
  admin_expiry?: string | null;
};
export type Scope = "dataset" | "data_product" | "domain" | "global";
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
export type DecisionStatus = "approved" | "pending" | "denied";
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
export type OutputPortStatus = "pending" | "active" | "archived";
export type OutputPortAccessType = "public" | "restricted" | "private";
export type OutputPort = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: OutputPortStatus;
  access_type: OutputPortAccessType;
  data_product_id: string;
  tags: Tag[];
};
export type RoleAssignment2 = {
  id: string;
  output_port: OutputPort;
  user: User;
  role: Role | null;
  decision: DecisionStatus;
  requested_on: string | null;
  requested_by: User | null;
  decided_on: string | null;
  decided_by: User | null;
  output_port_id: string;
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
export type NodeType =
  | "dataProductNode"
  | "dataOutputNode"
  | "datasetNode"
  | "domainNode";
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
export type LinkInputPortsToDataProductPost = {
  input_port_links: string[];
};
export type LinkInputPortsToDataProduct = {
  input_ports: string[];
  justification: string;
};
export type CreateTechnicalAssetResponse = {
  id: string;
};
export type TechnicalAssetStatus = "pending" | "active" | "archived";
export type DatabricksDataOutput = {
  configuration_type: "DatabricksDataOutput";
  catalog: string;
  schema?: string;
  table?: string;
  bucket_identifier?: string;
  catalog_path?: string;
  table_path?: string;
};
export type GlueDataOutput = {
  configuration_type: "GlueDataOutput";
  database: string;
  database_suffix?: string;
  table?: string;
  bucket_identifier?: string;
  database_path?: string;
  table_path?: string;
};
export type RedshiftDataOutput = {
  configuration_type: "RedshiftDataOutput";
  database: string;
  schema?: string;
  table?: string;
  bucket_identifier?: string;
  database_path?: string;
  table_path?: string;
};
export type S3DataOutput = {
  configuration_type: "S3DataOutput";
  bucket: string;
  suffix?: string;
  path: string;
};
export type SnowflakeDataOutput = {
  configuration_type: "SnowflakeDataOutput";
  database: string;
  schema?: string;
  table?: string;
  bucket_identifier?: string;
  database_path?: string;
  table_path?: string;
};
export type CreateTechnicalAssetRequest = {
  name: string;
  description: string;
  namespace: string;
  platform_id: string;
  service_id: string;
  status: TechnicalAssetStatus;
  configuration:
    | ({
        configuration_type: "DatabricksDataOutput";
      } & DatabricksDataOutput)
    | ({
        configuration_type: "GlueDataOutput";
      } & GlueDataOutput)
    | ({
        configuration_type: "RedshiftDataOutput";
      } & RedshiftDataOutput)
    | ({
        configuration_type: "S3DataOutput";
      } & S3DataOutput)
    | ({
        configuration_type: "SnowflakeDataOutput";
      } & SnowflakeDataOutput);
  sourceAligned: boolean;
  tag_ids: string[];
};
export type GetSigninUrlResponse = {
  signin_url: string;
};
export type GetConveyorIdeUrlResponse = {
  ide_url: string;
};
export type GetDatabricksWorkspaceUrlResponse = {
  databricks_workspace_url: string;
};
export type GetSnowflakeUrlResponse = {
  snowflake_url: string;
};
export type OutputPortLink = {
  id: string;
  output_port_id: string;
  technical_asset_id: string;
  status: DecisionStatus;
  output: OutputPort;
};
export type GetTechnicalAssetsResponseItem = {
  id: string;
  name: string;
  description: string;
  namespace: string;
  owner_id: string;
  platform_id: string;
  service_id: string;
  status: TechnicalAssetStatus;
  sourceAligned: boolean | null;
  configuration:
    | ({
        configuration_type: "DatabricksDataOutput";
      } & DatabricksDataOutput)
    | ({
        configuration_type: "GlueDataOutput";
      } & GlueDataOutput)
    | ({
        configuration_type: "RedshiftDataOutput";
      } & RedshiftDataOutput)
    | ({
        configuration_type: "S3DataOutput";
      } & S3DataOutput)
    | ({
        configuration_type: "SnowflakeDataOutput";
      } & SnowflakeDataOutput);
  owner: DataProduct;
  output_port_links: OutputPortLink[];
  tags: Tag[];
};
export type TechnicalInfo = {
  environment_id: string;
  environment: string;
  info: string | null;
};
export type GetTechnicalAssetsResponseItemRead = {
  id: string;
  name: string;
  description: string;
  namespace: string;
  owner_id: string;
  platform_id: string;
  service_id: string;
  status: TechnicalAssetStatus;
  sourceAligned: boolean | null;
  configuration:
    | ({
        configuration_type: "DatabricksDataOutput";
      } & DatabricksDataOutput)
    | ({
        configuration_type: "GlueDataOutput";
      } & GlueDataOutput)
    | ({
        configuration_type: "RedshiftDataOutput";
      } & RedshiftDataOutput)
    | ({
        configuration_type: "S3DataOutput";
      } & S3DataOutput)
    | ({
        configuration_type: "SnowflakeDataOutput";
      } & SnowflakeDataOutput);
  owner: DataProduct;
  output_port_links: OutputPortLink[];
  tags: Tag[];
  result_string: string;
  technical_info: TechnicalInfo[];
};
export type GetTechnicalAssetsResponse = {
  technical_assets: GetTechnicalAssetsResponseItem[];
};
export type GetTechnicalAssetsResponseRead = {
  technical_assets: GetTechnicalAssetsResponseItemRead[];
};
export type InputPort = {
  id: string;
  justification: string;
  data_product_id: string;
  output_port_id: string;
  status: DecisionStatus;
  input_port: OutputPort;
};
export type GetDataProductInputPortsResponse = {
  input_ports: InputPort[];
};
export type GetDataProductRolledUpTagsResponse = {
  rolled_up_tags: Tag[];
};
export const {
  useGetDataProductNamespaceSuggestionQuery,
  useLazyGetDataProductNamespaceSuggestionQuery,
  useValidateDataProductNamespaceQuery,
  useLazyValidateDataProductNamespaceQuery,
  useGetDataProductNamespaceLengthLimitsQuery,
  useLazyGetDataProductNamespaceLengthLimitsQuery,
  useCreateDataProductMutation,
  useGetDataProductsQuery,
  useLazyGetDataProductsQuery,
  useRemoveDataProductMutation,
  useUpdateDataProductMutation,
  useGetDataProductQuery,
  useLazyGetDataProductQuery,
  useUpdateDataProductAboutMutation,
  useUpdateDataProductStatusMutation,
  useUpdateDataProductUsageMutation,
  useGetGraphDataQuery,
  useLazyGetGraphDataQuery,
  useSetValueForDataProductMutation,
  useLinkInputPortsToDataProductMutation,
  useCreateTechnicalAssetMutation,
  useGetSigninUrlQuery,
  useLazyGetSigninUrlQuery,
  useGetConveyorIdeUrlQuery,
  useLazyGetConveyorIdeUrlQuery,
  useGetDatabricksWorkspaceUrlQuery,
  useLazyGetDatabricksWorkspaceUrlQuery,
  useGetSnowflakeUrlQuery,
  useLazyGetSnowflakeUrlQuery,
  useGetTechnicalAssetsQuery,
  useLazyGetTechnicalAssetsQuery,
  useGetDataProductInputPortsQuery,
  useLazyGetDataProductInputPortsQuery,
  useGetDataProductRolledUpTagsQuery,
  useLazyGetDataProductRolledUpTagsQuery,
  useUnlinkInputPortFromDataProductMutation,
  useValidateTechnicalAssetNamespaceQuery,
  useLazyValidateTechnicalAssetNamespaceQuery,
} = injectedRtkApi;
