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
        body: queryArg.outputPortDataQualitySummary,
      }),
    }),
    overwriteOutputPortDataQualitySummary: build.mutation<
      OverwriteOutputPortDataQualitySummaryApiResponse,
      OverwriteOutputPortDataQualitySummaryApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/data_quality_summary/${queryArg.summaryId}`,
        method: "PUT",
        body: queryArg.outputPortDataQualitySummary,
      }),
    }),
    pushCostRecord: build.mutation<
      PushCostRecordApiResponse,
      PushCostRecordApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/cost`,
        method: "POST",
        body: queryArg.createCostRecord,
      }),
    }),
    getCostHistory: build.query<
      GetCostHistoryApiResponse,
      GetCostHistoryApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/cost`,
        params: {
          day_range: queryArg.dayRange,
        },
      }),
    }),
    getFreshnessSlo: build.query<
      GetFreshnessSloApiResponse,
      GetFreshnessSloApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/freshness_slo`,
      }),
    }),
    upsertFreshnessSlo: build.mutation<
      UpsertFreshnessSloApiResponse,
      UpsertFreshnessSloApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/freshness_slo`,
        method: "PUT",
        body: queryArg.freshnessSloRequest,
      }),
    }),
    deleteFreshnessSlo: build.mutation<
      DeleteFreshnessSloApiResponse,
      DeleteFreshnessSloApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/freshness_slo`,
        method: "DELETE",
      }),
    }),
    addFreshnessObservation: build.mutation<
      AddFreshnessObservationApiResponse,
      AddFreshnessObservationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/freshness_observations`,
        method: "POST",
        body: queryArg.freshnessObservationRequest,
      }),
    }),
    getOutputPortTableSchemas: build.query<
      GetOutputPortTableSchemasApiResponse,
      GetOutputPortTableSchemasApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/table-schemas`,
      }),
    }),
    createOutputPortTableSchema: build.mutation<
      CreateOutputPortTableSchemaApiResponse,
      CreateOutputPortTableSchemaApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/table-schemas`,
        method: "POST",
        body: queryArg.tableSchemaRequest,
      }),
    }),
    replaceOutputPortTableSchema: build.mutation<
      ReplaceOutputPortTableSchemaApiResponse,
      ReplaceOutputPortTableSchemaApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/table-schemas/${queryArg.schemaId}`,
        method: "PUT",
        body: queryArg.tableSchemaRequest,
      }),
    }),
    deleteOutputPortTableSchema: build.mutation<
      DeleteOutputPortTableSchemaApiResponse,
      DeleteOutputPortTableSchemaApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/table-schemas/${queryArg.schemaId}`,
        method: "DELETE",
      }),
    }),
    getOutputPortSemanticModels: build.query<
      GetOutputPortSemanticModelsApiResponse,
      GetOutputPortSemanticModelsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/semantic-models`,
      }),
    }),
    createOutputPortSemanticModel: build.mutation<
      CreateOutputPortSemanticModelApiResponse,
      CreateOutputPortSemanticModelApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/semantic-models`,
        method: "POST",
        body: queryArg.semanticModelRequest,
      }),
    }),
    replaceOutputPortSemanticModel: build.mutation<
      ReplaceOutputPortSemanticModelApiResponse,
      ReplaceOutputPortSemanticModelApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/semantic-models/${queryArg.modelId}`,
        method: "PUT",
        body: queryArg.semanticModelRequest,
      }),
    }),
    deleteOutputPortSemanticModel: build.mutation<
      DeleteOutputPortSemanticModelApiResponse,
      DeleteOutputPortSemanticModelApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.id}/semantic-models/${queryArg.modelId}`,
        method: "DELETE",
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
  /** status 200 Successful Response */ OutputPortDataQualitySummaryResponse;
export type GetLatestDataQualitySummaryForOutputPortApiArg = {
  dataProductId: string;
  id: string;
};
export type AddOutputPortDataQualityRunApiResponse =
  /** status 200 Successful Response */ OutputPortDataQualitySummaryResponse;
export type AddOutputPortDataQualityRunApiArg = {
  dataProductId: string;
  id: string;
  outputPortDataQualitySummary: OutputPortDataQualitySummary;
};
export type OverwriteOutputPortDataQualitySummaryApiResponse =
  /** status 200 Successful Response */ OutputPortDataQualitySummaryResponse;
export type OverwriteOutputPortDataQualitySummaryApiArg = {
  dataProductId: string;
  id: string;
  summaryId: string;
  outputPortDataQualitySummary: OutputPortDataQualitySummary;
};
export type PushCostRecordApiResponse =
  /** status 201 Successful Response */ CostRecordResponseRead;
export type PushCostRecordApiArg = {
  dataProductId: string;
  id: string;
  createCostRecord: CreateCostRecord;
};
export type GetCostHistoryApiResponse =
  /** status 200 Successful Response */ CostHistoryResponseRead;
export type GetCostHistoryApiArg = {
  dataProductId: string;
  id: string;
  dayRange?: number;
};
export type GetFreshnessSloApiResponse =
  /** status 200 Successful Response */ FreshnessSloResponse;
export type GetFreshnessSloApiArg = {
  dataProductId: string;
  id: string;
};
export type UpsertFreshnessSloApiResponse =
  /** status 200 Successful Response */ FreshnessSloResponse;
export type UpsertFreshnessSloApiArg = {
  dataProductId: string;
  id: string;
  freshnessSloRequest: FreshnessSloRequest;
};
export type DeleteFreshnessSloApiResponse = unknown;
export type DeleteFreshnessSloApiArg = {
  dataProductId: string;
  id: string;
};
export type AddFreshnessObservationApiResponse =
  /** status 200 Successful Response */ FreshnessObservationResponse;
export type AddFreshnessObservationApiArg = {
  dataProductId: string;
  id: string;
  freshnessObservationRequest: FreshnessObservationRequest;
};
export type GetOutputPortTableSchemasApiResponse =
  /** status 200 Successful Response */ TableSchemaResponse[];
export type GetOutputPortTableSchemasApiArg = {
  dataProductId: string;
  id: string;
};
export type CreateOutputPortTableSchemaApiResponse =
  /** status 200 Successful Response */ TableSchemaResponse;
export type CreateOutputPortTableSchemaApiArg = {
  dataProductId: string;
  id: string;
  tableSchemaRequest: TableSchemaRequest;
};
export type ReplaceOutputPortTableSchemaApiResponse =
  /** status 200 Successful Response */ TableSchemaResponse;
export type ReplaceOutputPortTableSchemaApiArg = {
  dataProductId: string;
  id: string;
  schemaId: string;
  tableSchemaRequest: TableSchemaRequest;
};
export type DeleteOutputPortTableSchemaApiResponse = unknown;
export type DeleteOutputPortTableSchemaApiArg = {
  dataProductId: string;
  id: string;
  schemaId: string;
};
export type GetOutputPortSemanticModelsApiResponse =
  /** status 200 Successful Response */ SemanticModelResponse[];
export type GetOutputPortSemanticModelsApiArg = {
  dataProductId: string;
  id: string;
};
export type CreateOutputPortSemanticModelApiResponse =
  /** status 200 Successful Response */ SemanticModelResponse;
export type CreateOutputPortSemanticModelApiArg = {
  dataProductId: string;
  id: string;
  semanticModelRequest: SemanticModelRequest;
};
export type ReplaceOutputPortSemanticModelApiResponse =
  /** status 200 Successful Response */ SemanticModelResponse;
export type ReplaceOutputPortSemanticModelApiArg = {
  dataProductId: string;
  id: string;
  modelId: string;
  semanticModelRequest: SemanticModelRequest;
};
export type DeleteOutputPortSemanticModelApiResponse = unknown;
export type DeleteOutputPortSemanticModelApiArg = {
  dataProductId: string;
  id: string;
  modelId: string;
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
export type CostRecordResponse = {
  id: string;
  output_port_id: string;
  recorded_at: string;
  compute_cost: string;
  storage_cost: string;
  platform_overhead_cost: string;
};
export type CostRecordResponseRead = {
  id: string;
  output_port_id: string;
  recorded_at: string;
  compute_cost: string;
  storage_cost: string;
  platform_overhead_cost: string;
  total_cost: string;
};
export type CreateCostRecord = {
  recorded_at?: string | null;
  compute_cost: number | string;
  storage_cost: number | string;
  platform_overhead_cost: number | string;
};
export type CostHistoryResponse = {
  output_port_id: string;
  records: CostRecordResponse[];
};
export type CostHistoryResponseRead = {
  output_port_id: string;
  records: CostRecordResponseRead[];
};
export type FreshnessSloResponse = {
  id: string;
  output_port_id: string;
  deadline_time: string;
  status: FreshnessStatus;
  last_refreshed_at?: string | null;
  last_observed_at?: string | null;
};
export type FreshnessSloRequest = {
  deadline_time: string;
};
export type FreshnessObservationResponse = {
  id: string;
  output_port_id: string;
  last_refreshed_at: string;
  created_at: string;
  status: FreshnessStatus;
};
export type FreshnessObservationRequest = {
  last_refreshed_at: string;
};
export type Tag = {
  id: string;
  value: string;
};
export type ColumnResponse = {
  id: string;
  name: string;
  description?: string | null;
  data_type?: string | null;
  tags: Tag[];
};
export type TableSchemaResponse = {
  id: string;
  output_port_id: string;
  name: string;
  description?: string | null;
  tags: Tag[];
  columns: ColumnResponse[];
};
export type ColumnRequest = {
  name: string;
  description?: string | null;
  data_type?: string | null;
  tag_ids?: string[];
};
export type TableSchemaRequest = {
  name: string;
  description?: string | null;
  tag_ids?: string[];
  columns?: ColumnRequest[];
};
export type SemanticModelResponse = {
  id: string;
  output_port_id: string;
  name: string;
  format: SemanticModelFormat;
  content: {
    [key: string]: any;
  };
};
export type SemanticModelRequest = {
  name: string;
  format: SemanticModelFormat;
  content: {
    [key: string]: any;
  };
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
  freshness_status?: FreshnessStatus | null;
  freshness_deadline_time?: string | null;
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
export type AzureBlobTechnicalAssetConfiguration = {
  configuration_type: "AzureBlobTechnicalAssetConfiguration";
  domain?: string;
  path?: string;
  container_name: string;
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
export type OsiSemanticModelTechnicalAssetConfiguration = {
  configuration_type: "OSISemanticModelTechnicalAssetConfiguration";
  model_name?: string;
  location?: string;
};
export type PostgreSqlTechnicalAssetConfiguration = {
  configuration_type: "PostgreSQLTechnicalAssetConfiguration";
  database: string;
  schema?: string;
  table?: string;
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
        configuration_type: "AzureBlobTechnicalAssetConfiguration";
      } & AzureBlobTechnicalAssetConfiguration)
    | ({
        configuration_type: "DatabricksTechnicalAssetConfiguration";
      } & DatabricksTechnicalAssetConfiguration)
    | ({
        configuration_type: "GlueTechnicalAssetConfiguration";
      } & GlueTechnicalAssetConfiguration)
    | ({
        configuration_type: "OSISemanticModelTechnicalAssetConfiguration";
      } & OsiSemanticModelTechnicalAssetConfiguration)
    | ({
        configuration_type: "PostgreSQLTechnicalAssetConfiguration";
      } & PostgreSqlTechnicalAssetConfiguration)
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
export enum FreshnessStatus {
  Fresh = "fresh",
  Stale = "stale",
  Unknown = "unknown",
}
export enum SemanticModelFormat {
  MetricsFlow = "MetricsFlow",
  OpenSemanticInterchange = "OpenSemanticInterchange",
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
  Unrestricted = "unrestricted",
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
  usePushCostRecordMutation,
  useGetCostHistoryQuery,
  useLazyGetCostHistoryQuery,
  useGetFreshnessSloQuery,
  useLazyGetFreshnessSloQuery,
  useUpsertFreshnessSloMutation,
  useDeleteFreshnessSloMutation,
  useAddFreshnessObservationMutation,
  useGetOutputPortTableSchemasQuery,
  useLazyGetOutputPortTableSchemasQuery,
  useCreateOutputPortTableSchemaMutation,
  useReplaceOutputPortTableSchemaMutation,
  useDeleteOutputPortTableSchemaMutation,
  useGetOutputPortSemanticModelsQuery,
  useLazyGetOutputPortSemanticModelsQuery,
  useCreateOutputPortSemanticModelMutation,
  useReplaceOutputPortSemanticModelMutation,
  useDeleteOutputPortSemanticModelMutation,
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
