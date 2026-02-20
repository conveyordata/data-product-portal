import { api } from "@/store/api/services/generated/resourceNamesApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    searchOutputPorts: build.query<
      SearchOutputPortsApiResponse,
      SearchOutputPortsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/search/output_ports`,
        params: {
          query: queryArg.query,
          limit: queryArg.limit,
          current_user_assigned: queryArg.currentUserAssigned,
        },
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type SearchOutputPortsApiResponse =
  /** status 200 Successful Response */ SearchOutputPortsResponse;
export type SearchOutputPortsApiArg = {
  query?: string | null;
  limit?: number;
  currentUserAssigned?: boolean;
};
export type Tag = {
  id: string;
  value: string;
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
export type SearchOutputPortsResponseItem = {
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
  data_product_count: number;
  technical_assets_count: number;
  data_product_name: string;
  quality_status: DataQualityStatus | null;
};
export type SearchOutputPortsResponse = {
  output_ports: SearchOutputPortsResponseItem[];
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
export enum DataQualityStatus {
  Success = "success",
  Failure = "failure",
  Warning = "warning",
  Error = "error",
  Unknown = "unknown",
}
export const { useSearchOutputPortsQuery, useLazySearchOutputPortsQuery } =
  injectedRtkApi;
