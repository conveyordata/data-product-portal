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
    removeExploration: build.mutation<
      RemoveExplorationApiResponse,
      RemoveExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg}`,
        method: "DELETE",
      }),
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
    renewInputPortForExploration: build.mutation<
      RenewInputPortForExplorationApiResponse,
      RenewInputPortForExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg.id}/input_ports/${queryArg.outputPortId}/renew`,
        method: "POST",
      }),
    }),
    revokeInputPortForExploration: build.mutation<
      RevokeInputPortForExplorationApiResponse,
      RevokeInputPortForExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg.id}/input_ports/${queryArg.outputPortId}/revoke`,
        method: "POST",
      }),
    }),
    cancelInputPortForExploration: build.mutation<
      CancelInputPortForExplorationApiResponse,
      CancelInputPortForExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg.id}/input_ports/${queryArg.outputPortId}/cancel`,
        method: "POST",
      }),
    }),
    removeInputPortForExploration: build.mutation<
      RemoveInputPortForExplorationApiResponse,
      RemoveInputPortForExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg.id}/input_ports/${queryArg.outputPortId}`,
        method: "DELETE",
      }),
    }),
    addExplorationFinalizer: build.mutation<
      AddExplorationFinalizerApiResponse,
      AddExplorationFinalizerApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg.id}/finalizers`,
        method: "POST",
        body: queryArg.finalizerRequest,
      }),
    }),
    removeExplorationFinalizer: build.mutation<
      RemoveExplorationFinalizerApiResponse,
      RemoveExplorationFinalizerApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations/${queryArg.id}/finalizers/${queryArg.finalizer}`,
        method: "DELETE",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetExplorationsApiResponse =
  /** status 200 Successful Response */ GetExplorationsResponse;
export type GetExplorationsApiArg = string | undefined;
export type CreateExplorationApiResponse =
  /** status 200 Successful Response */ CreateExplorationResponse;
export type CreateExplorationApiArg = CreateExplorationRequestWithInputPorts;
export type GetExplorationApiResponse =
  /** status 200 Successful Response */ GetExplorationResponse;
export type GetExplorationApiArg = string;
export type RemoveExplorationApiResponse =
  /** status 200 Exploration deleted */ any;
export type RemoveExplorationApiArg = string;
export type GetExplorationInputPortsApiResponse =
  /** status 200 Successful Response */ GetExplorationInputPortsResponse;
export type GetExplorationInputPortsApiArg = string;
export type RequestInputPortsForExplorationApiResponse =
  /** status 200 Successful Response */ RequestInputPortsForExplorationResponse;
export type RequestInputPortsForExplorationApiArg = {
  id: string;
  requestInputPortsForExplorationRequest: RequestInputPortsForExplorationRequest;
};
export type RenewInputPortForExplorationApiResponse =
  /** status 200 Successful Response */ RenewInputPortForExplorationResponse;
export type RenewInputPortForExplorationApiArg = {
  id: string;
  outputPortId: string;
};
export type RevokeInputPortForExplorationApiResponse =
  /** status 200 Successful Response */ RevokeInputPortForExplorationResponse;
export type RevokeInputPortForExplorationApiArg = {
  id: string;
  outputPortId: string;
};
export type CancelInputPortForExplorationApiResponse =
  /** status 200 Successful Response */ CancelInputPortForExplorationResponse;
export type CancelInputPortForExplorationApiArg = {
  id: string;
  outputPortId: string;
};
export type RemoveInputPortForExplorationApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveInputPortForExplorationApiArg = {
  id: string;
  outputPortId: string;
};
export type AddExplorationFinalizerApiResponse =
  /** status 200 Successful Response */ any;
export type AddExplorationFinalizerApiArg = {
  id: string;
  finalizerRequest: FinalizerRequest;
};
export type RemoveExplorationFinalizerApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveExplorationFinalizerApiArg = {
  id: string;
  finalizer: string;
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
  status: AbstractDataProductStatus;
  finalizers: string[];
};
export type GetExplorationsResponse = {
  explorations: Exploration[];
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
export type CreateExplorationResponse = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  domain: Domain;
  status: AbstractDataProductStatus;
  finalizers: string[];
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
  status: AbstractDataProductStatus;
  finalizers: string[];
  owner: User;
};
export type InputPortRequestBase = {
  id: string;
  justification: string;
  decision_note?: string | null;
  valid_until: string | null;
  requested_by: User;
  decided_by?: User | null;
  decision: InputPortRequestDecision;
  revoked_at?: string | null;
  revoked_by?: User | null;
  created_on: string;
  requested_on: string;
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
export type AbstractDataProductInputPort = {
  id: string;
  status: InputPortStatus;
  current_request: InputPortRequestBase;
  renewal_status?: RenewalStatus | null;
  output_port_id: string;
  output_port: OutputPort;
};
export type GetExplorationInputPortsResponse = {
  input_ports: AbstractDataProductInputPort[];
};
export type RequestInputPortsForExplorationResponse = {
  input_port_ids: string[];
};
export type RenewInputPortForExplorationResponse = {
  input_port_id: string;
};
export type RevokeInputPortForExplorationResponse = {
  input_port_id: string;
};
export type CancelInputPortForExplorationResponse = {
  input_port_id: string;
};
export type FinalizerRequest = {
  finalizer: string;
};
export enum AbstractDataProductStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
  Deleting = "deleting",
}
export enum InputPortStatus {
  Pending = "pending",
  Approved = "approved",
  Denied = "denied",
  Expired = "expired",
  Revoked = "revoked",
  Cancelled = "cancelled",
}
export enum InputPortRequestDecision {
  Pending = "pending",
  Approved = "approved",
  Denied = "denied",
  Cancelled = "cancelled",
}
export enum RenewalStatus {
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
  useRemoveExplorationMutation,
  useGetExplorationInputPortsQuery,
  useLazyGetExplorationInputPortsQuery,
  useRequestInputPortsForExplorationMutation,
  useRenewInputPortForExplorationMutation,
  useRevokeInputPortForExplorationMutation,
  useCancelInputPortForExplorationMutation,
  useRemoveInputPortForExplorationMutation,
  useAddExplorationFinalizerMutation,
  useRemoveExplorationFinalizerMutation,
} = injectedRtkApi;
