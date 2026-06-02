import { api } from "@/store/api/services/generated/dataProductsOutputPortsDataQualityApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getExplorations: build.query<
      GetExplorationsApiResponse,
      GetExplorationsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations`,
        params: {
          filter_to_user_with_assigment: queryArg,
        },
      }),
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
    requestInputPortsForExploration: build.mutation<
      RequestInputPortsForExplorationApiResponse,
      RequestInputPortsForExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg.id}/input_ports`,
        method: "POST",
        body: queryArg.requestInputPortsForExplorationRequest,
      }),
    }),
    removeInputPortFromExploration: build.mutation<
      RemoveInputPortFromExplorationApiResponse,
      RemoveInputPortFromExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg.id}/input_ports/${queryArg.outputPortId}`,
        method: "DELETE",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetExplorationsApiResponse =
  /** status 200 Successful Response */ GetExplorationsResponse;
export type GetExplorationsApiArg = (string | null) | undefined;
export type CreateExplorationApiResponse =
  /** status 200 Successful Response */ CreateExplorationResponse;
export type CreateExplorationApiArg = CreateExplorationRequestWithInputPorts;
export type GetExplorationApiResponse =
  /** status 200 Successful Response */ GetExplorationResponse;
export type GetExplorationApiArg = string;
export type GetExplorationInputPortsApiResponse =
  /** status 200 Successful Response */ GetExplorationInputPortsResponse;
export type GetExplorationInputPortsApiArg = string;
export type RequestInputPortsForExplorationApiResponse =
  /** status 200 Successful Response */ RequestInputPortsForExplorationResponse;
export type RequestInputPortsForExplorationApiArg = {
  id: string;
  requestInputPortsForExplorationRequest: RequestInputPortsForExplorationRequest;
};
export type RemoveInputPortFromExplorationApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveInputPortFromExplorationApiArg = {
  id: string;
  outputPortId: string;
};
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
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type CreateExplorationResponse = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  domain: Domain;
};
export type RequestInputPortsForExplorationRequest = {
  output_ports: string[];
  justification: string;
};
export type CreateExplorationRequestWithInputPorts = {
  name: string;
  namespace: string;
  description: string;
  domain_id: string;
  input_ports?: RequestInputPortsForExplorationRequest | null;
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
export type GetExplorationResponse = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  domain: Domain;
  owner: User;
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
export type RequestInputPortsForExplorationResponse = {
  input_port_ids: string[];
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
export const {
  useGetExplorationsQuery,
  useLazyGetExplorationsQuery,
  useCreateExplorationMutation,
  useGetExplorationQuery,
  useLazyGetExplorationQuery,
  useGetExplorationInputPortsQuery,
  useLazyGetExplorationInputPortsQuery,
  useRequestInputPortsForExplorationMutation,
  useRemoveInputPortFromExplorationMutation,
} = injectedRtkApi;
