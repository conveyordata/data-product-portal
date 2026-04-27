import { api } from "@/store/api/services/generated/dataProductsOutputPortsDataQualityApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getExplorations: build.query<
      GetExplorationsApiResponse,
      GetExplorationsApiArg
    >({
      query: () => ({ url: `/api/v2/explorations` }),
    }),
    createExploration: build.mutation<
      CreateExplorationApiResponse,
      CreateExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations`,
        method: "POST",
        body: queryArg,
      }),
    }),
    getExploration: build.query<
      GetExplorationApiResponse,
      GetExplorationApiArg
    >({
      query: (queryArg) => ({ url: `/api/v2/explorations/${queryArg}` }),
    }),
    getExplorationInputPorts: build.query<
      GetExplorationInputPortsApiResponse,
      GetExplorationInputPortsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg}/input_ports`,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetExplorationsApiResponse =
  /** status 200 Successful Response */ GetExplorationsResponse;
export type GetExplorationsApiArg = void;
export type CreateExplorationApiResponse =
  /** status 200 Successful Response */ CreateExplorationResponse;
export type CreateExplorationApiArg = CreateExplorationRequestWithInputPorts;
export type GetExplorationApiResponse =
  /** status 200 Successful Response */ GetExplorationResponse;
export type GetExplorationApiArg = string;
export type GetExplorationInputPortsApiResponse =
  /** status 200 Successful Response */ GetExplorationInputPortsResponse;
export type GetExplorationInputPortsApiArg = string;
export type Domain = {
  id: string;
  name: string;
  description: string;
};
export type Exploration = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  domain: Domain;
};
export type GetExplorationsResponse = {
  explorations: Exploration[];
};
export type CreateExplorationResponse = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  domain: Domain;
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
export type CreateInputPortsForExplorationRequest = {
  output_ports: string[];
  justification: string;
};
export type CreateExplorationRequestWithInputPorts = {
  name: string;
  namespace: string;
  description: string;
  domain_id: string;
  input_ports?: CreateInputPortsForExplorationRequest | null;
};
export type GetExplorationResponse = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  domain: Domain;
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
  freshness_status?: FreshnessStatus | null;
  freshness_deadline_time?: string | null;
};
export type InputPort = {
  id: string;
  justification: string;
  status: DecisionStatus;
  output_port_id: string;
  output_port: OutputPort;
};
export type GetExplorationInputPortsResponse = {
  input_ports: InputPort[];
};
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
  Unrestricted = "unrestricted",
}
export enum FreshnessStatus {
  Fresh = "fresh",
  Stale = "stale",
  Unknown = "unknown",
}
export const {
  useGetExplorationsQuery,
  useLazyGetExplorationsQuery,
  useCreateExplorationMutation,
  useGetExplorationQuery,
  useLazyGetExplorationQuery,
  useGetExplorationInputPortsQuery,
  useLazyGetExplorationInputPortsQuery,
} = injectedRtkApi;
