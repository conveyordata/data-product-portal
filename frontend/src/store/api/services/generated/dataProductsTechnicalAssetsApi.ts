import { api } from "@/store/api/services/generated/dataProductsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    approveOutputPortTechnicalAssetLink: build.mutation<
      ApproveOutputPortTechnicalAssetLinkApiResponse,
      ApproveOutputPortTechnicalAssetLinkApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/technical_assets/approve_link_request`,
        method: "POST",
        body: queryArg.approveLinkBetweenTechnicalAssetAndOutputPortRequest,
      }),
    }),
    denyOutputPortTechnicalAssetLink: build.mutation<
      DenyOutputPortTechnicalAssetLinkApiResponse,
      DenyOutputPortTechnicalAssetLinkApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/technical_assets/deny_link_request`,
        method: "POST",
        body: queryArg.denyLinkBetweenTechnicalAssetAndOutputPortRequest,
      }),
    }),
    linkOutputPortToTechnicalAsset: build.mutation<
      LinkOutputPortToTechnicalAssetApiResponse,
      LinkOutputPortToTechnicalAssetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/technical_assets/add`,
        method: "POST",
        body: queryArg.linkTechnicalAssetToOutputPortRequest,
      }),
    }),
    unlinkOutputPortFromTechnicalAsset: build.mutation<
      UnlinkOutputPortFromTechnicalAssetApiResponse,
      UnlinkOutputPortFromTechnicalAssetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/technical_assets/remove`,
        method: "DELETE",
        body: queryArg.unLinkTechnicalAssetToOutputPortRequest,
      }),
    }),
    getDataProductTechnicalAssets: build.query<
      GetDataProductTechnicalAssetsApiResponse,
      GetDataProductTechnicalAssetsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg}/technical_assets`,
      }),
    }),
    createTechnicalAsset: build.mutation<
      CreateTechnicalAssetApiResponse,
      CreateTechnicalAssetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/technical_assets`,
        method: "POST",
        body: queryArg.createTechnicalAssetRequest,
      }),
    }),
    getTechnicalAsset: build.query<
      GetTechnicalAssetApiResponse,
      GetTechnicalAssetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/technical_assets/${queryArg.id}`,
      }),
    }),
    removeTechnicalAsset: build.mutation<
      RemoveTechnicalAssetApiResponse,
      RemoveTechnicalAssetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/technical_assets/${queryArg.id}`,
        method: "DELETE",
      }),
    }),
    updateTechnicalAsset: build.mutation<
      UpdateTechnicalAssetApiResponse,
      UpdateTechnicalAssetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/technical_assets/${queryArg.id}`,
        method: "PUT",
        body: queryArg.dataOutputUpdate,
      }),
    }),
    getTechnicalAssetEventHistory: build.query<
      GetTechnicalAssetEventHistoryApiResponse,
      GetTechnicalAssetEventHistoryApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/technical_assets/${queryArg.id}/history`,
      }),
    }),
    updateTechnicalAssetStatus: build.mutation<
      UpdateTechnicalAssetStatusApiResponse,
      UpdateTechnicalAssetStatusApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/technical_assets/${queryArg.id}/status`,
        method: "PUT",
        body: queryArg.dataOutputStatusUpdate,
      }),
    }),
    getTechnicalAssetGraphData: build.query<
      GetTechnicalAssetGraphDataApiResponse,
      GetTechnicalAssetGraphDataApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/technical_assets/${queryArg.id}/graph`,
        params: {
          level: queryArg.level,
        },
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type ApproveOutputPortTechnicalAssetLinkApiResponse =
  /** status 200 Successful Response */ any;
export type ApproveOutputPortTechnicalAssetLinkApiArg = {
  dataProductId: string;
  outputPortId: string;
  approveLinkBetweenTechnicalAssetAndOutputPortRequest: ApproveLinkBetweenTechnicalAssetAndOutputPortRequest;
};
export type DenyOutputPortTechnicalAssetLinkApiResponse =
  /** status 200 Successful Response */ any;
export type DenyOutputPortTechnicalAssetLinkApiArg = {
  dataProductId: string;
  outputPortId: string;
  denyLinkBetweenTechnicalAssetAndOutputPortRequest: DenyLinkBetweenTechnicalAssetAndOutputPortRequest;
};
export type LinkOutputPortToTechnicalAssetApiResponse =
  /** status 200 Successful Response */ LinkTechnicalAssetsToOutputPortResponse;
export type LinkOutputPortToTechnicalAssetApiArg = {
  dataProductId: string;
  outputPortId: string;
  linkTechnicalAssetToOutputPortRequest: LinkTechnicalAssetToOutputPortRequest;
};
export type UnlinkOutputPortFromTechnicalAssetApiResponse =
  /** status 200 Successful Response */ any;
export type UnlinkOutputPortFromTechnicalAssetApiArg = {
  dataProductId: string;
  outputPortId: string;
  unLinkTechnicalAssetToOutputPortRequest: UnLinkTechnicalAssetToOutputPortRequest;
};
export type GetDataProductTechnicalAssetsApiResponse =
  /** status 200 Successful Response */ GetTechnicalAssetsResponseRead;
export type GetDataProductTechnicalAssetsApiArg = string;
export type CreateTechnicalAssetApiResponse =
  /** status 200 Technical asset successfully created */ CreateTechnicalAssetResponse;
export type CreateTechnicalAssetApiArg = {
  dataProductId: string;
  createTechnicalAssetRequest: CreateTechnicalAssetRequest;
};
export type GetTechnicalAssetApiResponse =
  /** status 200 Successful Response */ GetTechnicalAssetsResponseItemRead;
export type GetTechnicalAssetApiArg = {
  dataProductId: string;
  id: string;
};
export type RemoveTechnicalAssetApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveTechnicalAssetApiArg = {
  dataProductId: string;
  id: string;
};
export type UpdateTechnicalAssetApiResponse =
  /** status 200 Successful Response */ UpdateTechnicalAssetResponse;
export type UpdateTechnicalAssetApiArg = {
  dataProductId: string;
  id: string;
  dataOutputUpdate: DataOutputUpdate;
};
export type GetTechnicalAssetEventHistoryApiResponse =
  /** status 200 Successful Response */ GetEventHistoryResponse;
export type GetTechnicalAssetEventHistoryApiArg = {
  dataProductId: string;
  id: string;
};
export type UpdateTechnicalAssetStatusApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateTechnicalAssetStatusApiArg = {
  dataProductId: string;
  id: string;
  dataOutputStatusUpdate: DataOutputStatusUpdate;
};
export type GetTechnicalAssetGraphDataApiResponse =
  /** status 200 Successful Response */ Graph;
export type GetTechnicalAssetGraphDataApiArg = {
  dataProductId: string;
  id: string;
  level?: number;
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
export type ApproveLinkBetweenTechnicalAssetAndOutputPortRequest = {
  technical_asset_id: string;
};
export type DenyLinkBetweenTechnicalAssetAndOutputPortRequest = {
  technical_asset_id: string;
};
export type LinkTechnicalAssetsToOutputPortResponse = {
  link_id: string;
};
export type LinkTechnicalAssetToOutputPortRequest = {
  technical_asset_id: string;
};
export type UnLinkTechnicalAssetToOutputPortRequest = {
  technical_asset_id: string;
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
export type DataProductType = {
  id: string;
  name: string;
  description: string;
  icon_key: DataProductIconKey;
};
export type DataProduct = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: DataProductStatus;
  type: DataProductType;
};
export type Tag = {
  id: string;
  value: string;
};
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
export type UpdateTechnicalAssetResponse = {
  id: string;
};
export type DataOutputUpdate = {
  name: string;
  description: string;
  tag_ids: string[];
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
export type DataOutputStatusUpdate = {
  status: TechnicalAssetStatus;
};
export type Edge = {
  id: string;
  source: string;
  target: string;
  animated: boolean;
  sourceHandle?: string;
  targetHandle?: string;
};
export type NodeData = {
  id: string;
  name: string;
  link_to_id?: string | null;
  icon_key?: string | null;
  domain?: string | null;
  domain_id?: string | null;
  description?: string | null;
};
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
export enum TechnicalAssetStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum TechnicalMapping {
  Default = "default",
  Custom = "custom",
}
export enum AccessGranularity {
  Schema = "schema",
  Table = "table",
}
export enum DataProductStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum DataProductIconKey {
  Reporting = "reporting",
  Processing = "processing",
  Exploration = "exploration",
  Ingestion = "ingestion",
  MachineLearning = "machine_learning",
  Analytics = "analytics",
  Default = "default",
}
export enum DecisionStatus {
  Approved = "approved",
  Pending = "pending",
  Denied = "denied",
}
export enum OutputPortStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum OutputPortAccessType {
  Public = "public",
  Restricted = "restricted",
  Private = "private",
}
export enum EventEntityType {
  DataProduct = "data_product",
  OutputPort = "output_port",
  TechnicalAsset = "technical_asset",
  User = "user",
}
export enum NodeType {
  DataProductNode = "dataProductNode",
  DataOutputNode = "dataOutputNode",
  DatasetNode = "datasetNode",
  DomainNode = "domainNode",
}
export const {
  useApproveOutputPortTechnicalAssetLinkMutation,
  useDenyOutputPortTechnicalAssetLinkMutation,
  useLinkOutputPortToTechnicalAssetMutation,
  useUnlinkOutputPortFromTechnicalAssetMutation,
  useGetDataProductTechnicalAssetsQuery,
  useLazyGetDataProductTechnicalAssetsQuery,
  useCreateTechnicalAssetMutation,
  useGetTechnicalAssetQuery,
  useLazyGetTechnicalAssetQuery,
  useRemoveTechnicalAssetMutation,
  useUpdateTechnicalAssetMutation,
  useGetTechnicalAssetEventHistoryQuery,
  useLazyGetTechnicalAssetEventHistoryQuery,
  useUpdateTechnicalAssetStatusMutation,
  useGetTechnicalAssetGraphDataQuery,
  useLazyGetTechnicalAssetGraphDataQuery,
} = injectedRtkApi;
