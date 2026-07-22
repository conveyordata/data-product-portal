import { api } from "@/store/api/services/generated/dataProductsOutputPortsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getInputPortsForOutputPort: build.query<
      GetInputPortsForOutputPortApiResponse,
      GetInputPortsForOutputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/input_ports/`,
      }),
    }),
    approveOutputPortAsInputPort: build.mutation<
      ApproveOutputPortAsInputPortApiResponse,
      ApproveOutputPortAsInputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/input_ports/approve`,
        method: "POST",
        body: queryArg.approveOutputPortAsInputPortRequest,
      }),
    }),
    denyOutputPortAsInputPort: build.mutation<
      DenyOutputPortAsInputPortApiResponse,
      DenyOutputPortAsInputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/input_ports/deny`,
        method: "POST",
        body: queryArg.denyOutputPortAsInputPortRequest,
      }),
    }),
    removeOutputPortAsInputPort: build.mutation<
      RemoveOutputPortAsInputPortApiResponse,
      RemoveOutputPortAsInputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/input_ports/remove`,
        method: "POST",
        body: queryArg.removeOutputPortAsInputPortRequest,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetInputPortsForOutputPortApiResponse =
  /** status 200 Successful Response */ GetInputPortsForOutputPortResponse;
export type GetInputPortsForOutputPortApiArg = {
  dataProductId: string;
  outputPortId: string;
};
export type ApproveOutputPortAsInputPortApiResponse =
  /** status 200 Successful Response */ any;
export type ApproveOutputPortAsInputPortApiArg = {
  dataProductId: string;
  outputPortId: string;
  approveOutputPortAsInputPortRequest: ApproveOutputPortAsInputPortRequest;
};
export type DenyOutputPortAsInputPortApiResponse =
  /** status 200 Successful Response */ any;
export type DenyOutputPortAsInputPortApiArg = {
  dataProductId: string;
  outputPortId: string;
  denyOutputPortAsInputPortRequest: DenyOutputPortAsInputPortRequest;
};
export type RemoveOutputPortAsInputPortApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveOutputPortAsInputPortApiArg = {
  dataProductId: string;
  outputPortId: string;
  removeOutputPortAsInputPortRequest: RemoveOutputPortAsInputPortRequest;
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
export type InputPortRequestBase = {
  id: string;
  justification: string;
  decision_note?: string | null;
  valid_until: string | null;
  requested_by: User;
  decided_by?: User | null;
  decision: DecisionStatus;
  created_on: string;
  requested_on: string;
};
export type AbstractDataProductInfo = {
  name: string;
  namespace: string;
  abstract_data_product_type: AbstractDataProductType;
};
export type OutputPortInputPort = {
  id: string;
  status: InputPortStatus;
  current_request: InputPortRequestBase;
  renewal_status?: RenewalStatus | null;
  consuming_abstract_data_product_id: string;
  consuming_abstract_data_product: AbstractDataProductInfo;
};
export type GetInputPortsForOutputPortResponse = {
  input_ports: OutputPortInputPort[];
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
export type ApproveOutputPortAsInputPortRequest = {
  consuming_data_product_id: string;
  decision_note?: string | null;
};
export type DenyOutputPortAsInputPortRequest = {
  consuming_data_product_id: string;
  decision_note: string;
};
export type RemoveOutputPortAsInputPortRequest = {
  consuming_data_product_id: string;
};
export enum InputPortStatus {
  Pending = "pending",
  Approved = "approved",
  Denied = "denied",
  Expired = "expired",
}
export enum DecisionStatus {
  Approved = "approved",
  Pending = "pending",
  Denied = "denied",
}
export enum RenewalStatus {
  Pending = "pending",
  Denied = "denied",
}
export enum AbstractDataProductType {
  Unknown = "unknown",
  DataProducts = "data_products",
  Explorations = "explorations",
}
export const {
  useGetInputPortsForOutputPortQuery,
  useLazyGetInputPortsForOutputPortQuery,
  useApproveOutputPortAsInputPortMutation,
  useDenyOutputPortAsInputPortMutation,
  useRemoveOutputPortAsInputPortMutation,
} = injectedRtkApi;
