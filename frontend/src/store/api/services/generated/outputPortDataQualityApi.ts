import { api } from "@/store/api/services/generated/configurationTagsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
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
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
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
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
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
export enum DataQualityStatus {
  Success = "success",
  Failure = "failure",
  Warning = "warning",
  Error = "error",
  Unknown = "unknown",
}
export const {
  useGetLatestDataQualitySummaryForOutputPortQuery,
  useLazyGetLatestDataQualitySummaryForOutputPortQuery,
  useAddOutputPortDataQualityRunMutation,
  useOverwriteOutputPortDataQualitySummaryMutation,
} = injectedRtkApi;
