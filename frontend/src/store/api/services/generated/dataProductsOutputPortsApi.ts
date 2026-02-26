import { api } from "@/store/api/services/generated/dataProductsTechnicalAssetsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getOutputPortQueryStats: build.query<
      GetOutputPortQueryStatsApiResponse,
      GetOutputPortQueryStatsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/query_stats`,
        params: {
          granularity: queryArg.granularity,
          day_range: queryArg.dayRange,
        },
      }),
    }),
    updateOutputPortQueryStats: build.mutation<
      UpdateOutputPortQueryStatsApiResponse,
      UpdateOutputPortQueryStatsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/query_stats`,
        method: "PATCH",
        body: queryArg.updateOutputPortQueryStatus,
      }),
    }),
    deleteOutputPortQueryStat: build.mutation<
      DeleteOutputPortQueryStatApiResponse,
      DeleteOutputPortQueryStatApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/query_stats`,
        method: "DELETE",
        body: queryArg.outputPortQueryStatsDelete,
      }),
    }),
    getOutputPortCuratedQueries: build.query<
      GetOutputPortCuratedQueriesApiResponse,
      GetOutputPortCuratedQueriesApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/curated_queries`,
      }),
    }),
    replaceOutputPortCuratedQueries: build.mutation<
      ReplaceOutputPortCuratedQueriesApiResponse,
      ReplaceOutputPortCuratedQueriesApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/curated_queries`,
        method: "PUT",
        body: queryArg.outputPortCuratedQueriesUpdate,
      }),
    }),
    getLatestDataQualitySummaryForOutputPort: build.query<
      GetLatestDataQualitySummaryForOutputPortApiResponse,
      GetLatestDataQualitySummaryForOutputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/data_quality_summary`,
      }),
    }),
    addOutputPortDataQualityRun: build.mutation<
      AddOutputPortDataQualityRunApiResponse,
      AddOutputPortDataQualityRunApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/data_quality_summary`,
        method: "POST",
        body: queryArg.outputPortDataQualitySummaryInput,
      }),
    }),
    overwriteOutputPortDataQualitySummary: build.mutation<
      OverwriteOutputPortDataQualitySummaryApiResponse,
      OverwriteOutputPortDataQualitySummaryApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/data_quality_summary/${queryArg.summaryId}`,
        method: "PUT",
        body: queryArg.outputPortDataQualitySummaryInput,
      }),
    }),
    getDataProductOutputPorts: build.query<
      GetDataProductOutputPortsApiResponse,
      GetDataProductOutputPortsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg}/output_ports`,
      }),
    }),
    createOutputPort: build.mutation<
      CreateOutputPortApiResponse,
      CreateOutputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports`,
        method: "POST",
        body: queryArg.createOutputPortRequest,
      }),
    }),
    getOutputPort: build.query<GetOutputPortApiResponse, GetOutputPortApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}`,
      }),
    }),
    removeOutputPort: build.mutation<
      RemoveOutputPortApiResponse,
      RemoveOutputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}`,
        method: "DELETE",
      }),
    }),
    updateOutputPort: build.mutation<
      UpdateOutputPortApiResponse,
      UpdateOutputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}`,
        method: "PUT",
        body: queryArg.datasetUpdate,
      }),
    }),
    getOutputPortsEventHistory: build.query<
      GetOutputPortsEventHistoryApiResponse,
      GetOutputPortsEventHistoryApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/history`,
      }),
    }),
    updateOutputPortAbout: build.mutation<
      UpdateOutputPortAboutApiResponse,
      UpdateOutputPortAboutApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/about`,
        method: "PUT",
        body: queryArg.datasetAboutUpdate,
      }),
    }),
    updateOutputPortStatus: build.mutation<
      UpdateOutputPortStatusApiResponse,
      UpdateOutputPortStatusApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/status`,
        method: "PUT",
        body: queryArg.datasetStatusUpdate,
      }),
    }),
    getOutputPortGraphData: build.query<
      GetOutputPortGraphDataApiResponse,
      GetOutputPortGraphDataApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/graph`,
        params: {
          level: queryArg.level,
        },
      }),
    }),
    setValueForOutputPort: build.mutation<
      SetValueForOutputPortApiResponse,
      SetValueForOutputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/settings/${queryArg.settingId}`,
        method: "POST",
        params: {
          value: queryArg.value,
        },
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetOutputPortQueryStatsApiResponse =
  /** status 200 Successful Response */ OutputPortQueryStatsResponses;
export type GetOutputPortQueryStatsApiArg = {
  dataProductId: string;
  id: string;
  granularity?: QueryStatsGranularity;
  dayRange?: number;
};
export type UpdateOutputPortQueryStatsApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateOutputPortQueryStatsApiArg = {
  dataProductId: string;
  id: string;
  updateOutputPortQueryStatus: UpdateOutputPortQueryStatus;
};
export type DeleteOutputPortQueryStatApiResponse =
  /** status 200 Successful Response */ any;
export type DeleteOutputPortQueryStatApiArg = {
  dataProductId: string;
  id: string;
  outputPortQueryStatsDelete: OutputPortQueryStatsDelete;
};
export type GetOutputPortCuratedQueriesApiResponse =
  /** status 200 Successful Response */ OutputPortCuratedQueries;
export type GetOutputPortCuratedQueriesApiArg = {
  dataProductId: string;
  id: string;
};
export type ReplaceOutputPortCuratedQueriesApiResponse =
  /** status 200 Successful Response */ OutputPortCuratedQueries;
export type ReplaceOutputPortCuratedQueriesApiArg = {
  dataProductId: string;
  id: string;
  outputPortCuratedQueriesUpdate: OutputPortCuratedQueriesUpdate;
};
export type GetLatestDataQualitySummaryForOutputPortApiResponse =
  /** status 200 Successful Response */ OutputPortDataQualitySummary;
export type GetLatestDataQualitySummaryForOutputPortApiArg = {
  dataProductId: string;
  id: string;
};
export type AddOutputPortDataQualityRunApiResponse =
  /** status 200 Successful Response */ OutputPortDataQualitySummaryResponse;
export type AddOutputPortDataQualityRunApiArg = {
  dataProductId: string;
  id: string;
  outputPortDataQualitySummaryInput: OutputPortDataQualitySummary2;
};
export type OverwriteOutputPortDataQualitySummaryApiResponse =
  /** status 200 Successful Response */ OutputPortDataQualitySummaryResponse;
export type OverwriteOutputPortDataQualitySummaryApiArg = {
  dataProductId: string;
  id: string;
  summaryId: string;
  outputPortDataQualitySummaryInput: OutputPortDataQualitySummary2;
};
export type GetDataProductOutputPortsApiResponse =
  /** status 200 Successful Response */ GetDataProductOutputPortsResponse;
export type GetDataProductOutputPortsApiArg = string;
export type CreateOutputPortApiResponse =
  /** status 200 Successful Response */ CreateOutputPortResponse;
export type CreateOutputPortApiArg = {
  dataProductId: string;
  createOutputPortRequest: CreateOutputPortRequest;
};
export type GetOutputPortApiResponse =
  /** status 200 Successful Response */ GetOutputPortResponse;
export type GetOutputPortApiArg = {
  dataProductId: string;
  id: string;
};
export type RemoveOutputPortApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveOutputPortApiArg = {
  dataProductId: string;
  id: string;
};
export type UpdateOutputPortApiResponse =
  /** status 200 Successful Response */ UpdateOutputPortResponse;
export type UpdateOutputPortApiArg = {
  dataProductId: string;
  id: string;
  datasetUpdate: DatasetUpdate;
};
export type GetOutputPortsEventHistoryApiResponse =
  /** status 200 Successful Response */ GetEventHistoryResponse;
export type GetOutputPortsEventHistoryApiArg = {
  dataProductId: string;
  id: string;
};
export type UpdateOutputPortAboutApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateOutputPortAboutApiArg = {
  dataProductId: string;
  id: string;
  datasetAboutUpdate: DatasetAboutUpdate;
};
export type UpdateOutputPortStatusApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateOutputPortStatusApiArg = {
  dataProductId: string;
  id: string;
  datasetStatusUpdate: DatasetStatusUpdate;
};
export type GetOutputPortGraphDataApiResponse =
  /** status 200 Successful Response */ Graph;
export type GetOutputPortGraphDataApiArg = {
  dataProductId: string;
  id: string;
  level?: number;
};
export type SetValueForOutputPortApiResponse =
  /** status 200 Successful Response */ any;
export type SetValueForOutputPortApiArg = {
  dataProductId: string;
  id: string;
  settingId: string;
  value: string;
};
export type OutputPortQueryStatsResponse = {
  date: string;
  consumer_data_product_id: string;
  query_count: number;
  consumer_data_product_name?: string | null;
};
export type OutputPortQueryStatsResponses = {
  output_port_query_stats_responses: OutputPortQueryStatsResponse[];
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
export type OutputPortQueryStatsUpdate = {
  date: string;
  consumer_data_product_id: string;
  query_count: number;
};
export type UpdateOutputPortQueryStatus = {
  output_port_query_stats_updates: OutputPortQueryStatsUpdate[];
};
export type OutputPortQueryStatsDelete = {
  date: string;
  consumer_data_product_id: string;
};
export type OutputPortCuratedQuery = {
  output_port_id: string;
  sort_order: number;
  title: string;
  description: string | null;
  query_text: string;
  created_at: string;
  updated_at: string | null;
};
export type OutputPortCuratedQueries = {
  output_port_curated_queries: OutputPortCuratedQuery[];
};
export type OutputPortCuratedQueryInput = {
  title: string;
  description?: string | null;
  query_text: string;
};
export type OutputPortCuratedQueriesUpdate = {
  curated_queries: OutputPortCuratedQueryInput[];
};
export type DataQualityTechnicalAsset = {
  name: string;
  status: DataQualityStatus;
};
export type OutputPortDataQualitySummary = {
  created_at: string;
  overall_status: DataQualityStatus;
  description?: string | null;
  details_url?: string | null;
  technical_assets: DataQualityTechnicalAsset[];
  dimensions?: {
    [key: string]: DataQualityStatus;
  } | null;
};
export type OutputPortDataQualitySummaryResponse = {
  created_at: string;
  overall_status: DataQualityStatus;
  description?: string | null;
  details_url?: string | null;
  technical_assets: DataQualityTechnicalAsset[];
  dimensions?: {
    [key: string]: DataQualityStatus;
  } | null;
  id: string;
  output_port_id: string;
};
export type OutputPortDataQualitySummary2 = {
  created_at: string;
  overall_status: DataQualityStatus;
  description?: string | null;
  details_url?: string | null;
  technical_assets: DataQualityTechnicalAsset[];
  dimensions?: {
    [key: string]: DataQualityStatus;
  } | null;
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
export type GetDataProductOutputPortsResponse = {
  output_ports: OutputPort[];
};
export type CreateOutputPortResponse = {
  id: string;
};
export type CreateOutputPortRequest = {
  name: string;
  namespace: string;
  description: string;
  access_type: OutputPortAccessType;
  about?: string | null;
  lifecycle_id?: string | null;
  tag_ids: string[];
  owners: string[];
};
export type Domain = {
  id: string;
  name: string;
  description: string;
};
export type DataProductLifeCycle = {
  id: string;
  name: string;
  value: number;
  color: string;
  is_default: boolean;
};
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
export type OutputPortSettingValue = {
  id: string;
  data_product_setting_id: string;
  value: string;
  data_product_setting: DataProductSetting;
  output_port_id: string;
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
export type TechnicalAssetLink = {
  id: string;
  output_port_id: string;
  technical_asset_id: string;
  status: DecisionStatus;
  technical_asset: TechnicalAsset;
};
export type GetOutputPortResponse = {
  id: string;
  namespace: string;
  name: string;
  description: string;
  status: OutputPortStatus;
  usage: string | null;
  access_type: OutputPortAccessType;
  data_product_id: string;
  tags: Tag[];
  domain: Domain;
  lifecycle: DataProductLifeCycle | null;
  about: string | null;
  rolled_up_tags: Tag[];
  data_product_settings: OutputPortSettingValue[];
  technical_asset_links: TechnicalAssetLink[];
};
export type UpdateOutputPortResponse = {
  id: string;
};
export type DatasetUpdate = {
  name: string;
  namespace: string;
  description: string;
  access_type: OutputPortAccessType;
  about?: string | null;
  lifecycle_id?: string | null;
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
export type DatasetAboutUpdate = {
  about: string;
};
export type DatasetStatusUpdate = {
  status: OutputPortStatus;
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
export enum QueryStatsGranularity {
  Day = "day",
  Week = "week",
  Month = "month",
}
export enum DataQualityStatus {
  Success = "success",
  Failure = "failure",
  Warning = "warning",
  Error = "error",
  Unknown = "unknown",
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
export enum DataProductSettingType {
  Checkbox = "checkbox",
  Tags = "tags",
  Input = "input",
}
export enum DataProductSettingScope {
  Dataproduct = "dataproduct",
  Dataset = "dataset",
}
export enum DecisionStatus {
  Approved = "approved",
  Pending = "pending",
  Denied = "denied",
}
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
export enum EventEntityType {
  DataProduct = "data_product",
  OutputPort = "output_port",
  TechnicalAsset = "technical_asset",
  User = "user",
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
export enum NodeType {
  DataProductNode = "dataProductNode",
  DataOutputNode = "dataOutputNode",
  DatasetNode = "datasetNode",
  DomainNode = "domainNode",
}
export const {
  useGetOutputPortQueryStatsQuery,
  useLazyGetOutputPortQueryStatsQuery,
  useUpdateOutputPortQueryStatsMutation,
  useDeleteOutputPortQueryStatMutation,
  useGetOutputPortCuratedQueriesQuery,
  useLazyGetOutputPortCuratedQueriesQuery,
  useReplaceOutputPortCuratedQueriesMutation,
  useGetLatestDataQualitySummaryForOutputPortQuery,
  useLazyGetLatestDataQualitySummaryForOutputPortQuery,
  useAddOutputPortDataQualityRunMutation,
  useOverwriteOutputPortDataQualitySummaryMutation,
  useGetDataProductOutputPortsQuery,
  useLazyGetDataProductOutputPortsQuery,
  useCreateOutputPortMutation,
  useGetOutputPortQuery,
  useLazyGetOutputPortQuery,
  useRemoveOutputPortMutation,
  useUpdateOutputPortMutation,
  useGetOutputPortsEventHistoryQuery,
  useLazyGetOutputPortsEventHistoryQuery,
  useUpdateOutputPortAboutMutation,
  useUpdateOutputPortStatusMutation,
  useGetOutputPortGraphDataQuery,
  useLazyGetOutputPortGraphDataQuery,
  useSetValueForOutputPortMutation,
} = injectedRtkApi;
