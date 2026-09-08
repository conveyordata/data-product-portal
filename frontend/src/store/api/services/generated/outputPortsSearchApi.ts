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
          assignment_filter: queryArg.assignmentFilter,
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
  query?: string;
  limit?: number;
  assignmentFilter?: AssignmentFilter;
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
export type AccessMode = {
  id: string;
  name: string;
  description: string;
};
export type SearchOutputPortsResponseItem = {
  id: string;
  namespace: string;
  name: string;
  description: string;
  status: OutputPortStatus;
  usage: string | null;
  access_type: OutputPortAccessType;
  data_product_access_duration_type: AccessDurationType;
  exploration_access_duration_type: AccessDurationType;
  data_product_id: string;
  tags: Tag[];
  domain: Domain;
  lifecycle: DataProductLifeCycle | null;
  access_modes: AccessMode[];
  abstract_data_product_count: number;
  technical_assets_count: number;
  data_product_name: string;
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
  Restricted = "restricted",
  Private = "private",
  Unrestricted = "unrestricted",
}
export enum AccessDurationType {
  Permanent = "permanent",
  TimeBound = "time_bound",
}
export enum AssignmentFilter {
  All = "all",
  OnlyAssigned = "only_assigned",
}
export const { useSearchOutputPortsQuery, useLazySearchOutputPortsQuery } =
  injectedRtkApi;
