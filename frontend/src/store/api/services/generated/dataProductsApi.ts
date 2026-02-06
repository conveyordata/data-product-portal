import { api } from "@/store/api/services/generated/pluginsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    createDataProduct: build.mutation<
      CreateDataProductApiResponse,
      CreateDataProductApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products`,
        method: "POST",
        body: queryArg,
      }),
    }),
    getDataProducts: build.query<
      GetDataProductsApiResponse,
      GetDataProductsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products`,
        params: {
          filter_to_user_with_assigment: queryArg,
        },
      }),
    }),
    removeDataProduct: build.mutation<
      RemoveDataProductApiResponse,
      RemoveDataProductApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg}`,
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
      query: (queryArg) => ({ url: `/api/v2/data_products/${queryArg}` }),
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
    getDataProductGraphData: build.query<
      GetDataProductGraphDataApiResponse,
      GetDataProductGraphDataApiArg
    >({
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
    getDataProductEventHistory: build.query<
      GetDataProductEventHistoryApiResponse,
      GetDataProductEventHistoryApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg}/history`,
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
        url: `/api/v2/data_products/${queryArg}/conveyor_ide_url`,
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
        url: `/api/v2/data_products/${queryArg}/technical_assets`,
      }),
    }),
    getDataProductInputPorts: build.query<
      GetDataProductInputPortsApiResponse,
      GetDataProductInputPortsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg}/input_ports`,
      }),
    }),
    getDataProductRolledUpTags: build.query<
      GetDataProductRolledUpTagsApiResponse,
      GetDataProductRolledUpTagsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg}/rolled_up_tags`,
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
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type CreateDataProductApiResponse =
  /** status 200 Data Product successfully created */ CreateDataProductResponse;
export type CreateDataProductApiArg = DataProductCreate;
export type GetDataProductsApiResponse =
  /** status 200 Successful Response */ GetDataProductsResponse;
export type GetDataProductsApiArg = (string | null) | undefined;
export type RemoveDataProductApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveDataProductApiArg = string;
export type UpdateDataProductApiResponse =
  /** status 200 Successful Response */ UpdateDataProductResponse;
export type UpdateDataProductApiArg = {
  id: string;
  dataProductUpdate: DataProductUpdate;
};
export type GetDataProductApiResponse =
  /** status 200 Successful Response */ GetDataProductResponse;
export type GetDataProductApiArg = string;
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
export type GetDataProductGraphDataApiResponse =
  /** status 200 Successful Response */ Graph;
export type GetDataProductGraphDataApiArg = {
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
export type GetDataProductEventHistoryApiResponse =
  /** status 200 Successful Response */ GetEventHistoryResponse;
export type GetDataProductEventHistoryApiArg = string;
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
export type GetConveyorIdeUrlApiArg = string;
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
export type GetTechnicalAssetsApiArg = string;
export type GetDataProductInputPortsApiResponse =
  /** status 200 Successful Response */ GetDataProductInputPortsResponse;
export type GetDataProductInputPortsApiArg = string;
export type GetDataProductRolledUpTagsApiResponse =
  /** status 200 Successful Response */ GetDataProductRolledUpTagsResponse;
export type GetDataProductRolledUpTagsApiArg = string;
export type UnlinkInputPortFromDataProductApiResponse =
  /** status 200 Successful Response */ any;
export type UnlinkInputPortFromDataProductApiArg = {
  id: string;
  inputPortId: string;
};
export type CreateDataProductResponse = {
  id: string;
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
  | 413
  | 414;
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
export type EventEntityType =
  | "data_product"
  | "output_port"
  | "technical_asset"
  | "user";
export type TechnicalAssetStatus = "pending" | "active" | "archived";
export type TechnicalMapping = "default" | "custom";
export type AccessGranularity = "schema" | "table";
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
export type TechnicalAsset = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: TechnicalAssetStatus;
  technical_mapping: TechnicalMapping;
  owner_id: string;
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
export type GetEventHistoryResponseItem = {
  id: string;
  name: string;
  subject_id: string;
  target_id?: string | null;
  subject_type: EventEntityType;
  target_type?: EventEntityType | null;
  actor_id: string;
  created_on: string;
  deleted_subject_identifier?: string | null;
  deleted_target_identifier?: string | null;
  actor: User;
  data_product?: DataProduct | null;
  user?: User | null;
  output_port?: OutputPort | null;
  technical_asset?: TechnicalAsset | null;
};
export type GetEventHistoryResponse = {
  events: GetEventHistoryResponseItem[];
};
export type CreateTechnicalAssetResponse = {
  id: string;
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
  /** DEPRECATED: Use 'technical_mapping' instead. This field will be removed in a future version. */
  sourceAligned?: boolean | null;
  technical_mapping?: TechnicalMapping | null;
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
  technical_mapping: TechnicalMapping;
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
  technical_mapping: TechnicalMapping;
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
  owner: DataProduct;
  output_port_links: OutputPortLink[];
  tags: Tag[];
  /** DEPRECATED: Use 'technical_mapping' instead. This field will be removed in a future version. */
  sourceAligned: boolean;
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
  useGetDataProductGraphDataQuery,
  useLazyGetDataProductGraphDataQuery,
  useSetValueForDataProductMutation,
  useLinkInputPortsToDataProductMutation,
  useGetDataProductEventHistoryQuery,
  useLazyGetDataProductEventHistoryQuery,
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
} = injectedRtkApi;
