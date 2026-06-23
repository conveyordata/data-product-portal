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
    removeInputPortFromExploration: build.mutation<
      RemoveInputPortFromExplorationApiResponse,
      RemoveInputPortFromExplorationApiArg
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
export type RemoveInputPortFromExplorationApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveInputPortFromExplorationApiArg = {
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
  reasoning?: string | null;
  output_port_id: string;
  output_port: OutputPort;
};
export type GetExplorationInputPortsResponse = {
  input_ports: InputPort[];
};
export type RequestInputPortsForExplorationResponse = {
  input_port_ids: string[];
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
  useRemoveExplorationMutation,
  useGetExplorationInputPortsQuery,
  useLazyGetExplorationInputPortsQuery,
  useRequestInputPortsForExplorationMutation,
  useRemoveInputPortFromExplorationMutation,
  useAddExplorationFinalizerMutation,
  useRemoveExplorationFinalizerMutation,
} = injectedRtkApi;
