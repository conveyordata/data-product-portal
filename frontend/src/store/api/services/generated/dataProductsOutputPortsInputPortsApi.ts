import { api } from "@/store/api/services/generated/dataProductsOutputPortsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getInputPortsForOutputPort: build.query<
      GetInputPortsForOutputPortApiResponse,
      GetInputPortsForOutputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/input_ports`,
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
    renewOutputPortAsInputPort: build.mutation<
      RenewOutputPortAsInputPortApiResponse,
      RenewOutputPortAsInputPortApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/data_products/${queryArg.dataProductId}/output_ports/${queryArg.outputPortId}/input_ports/renew`,
        method: "POST",
        body: queryArg.renewOutputPortAsInputPortRequest,
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
export type RenewOutputPortAsInputPortApiResponse =
  /** status 200 Successful Response */ any;
export type RenewOutputPortAsInputPortApiArg = {
  dataProductId: string;
  outputPortId: string;
  renewOutputPortAsInputPortRequest: RenewOutputPortAsInputPortRequest;
};
export type RemoveOutputPortAsInputPortApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveOutputPortAsInputPortApiArg = {
  dataProductId: string;
  outputPortId: string;
  removeOutputPortAsInputPortRequest: RemoveOutputPortAsInputPortRequest;
};
export type AbstractDataProductInfo = {
  name: string;
  namespace: string;
  abstract_data_product_type: AbstractDataProductType;
};
export type OutputPortInputPort = {
  id: string;
  justification: string;
  status: DecisionStatus;
  expires_on?: string | null;
  consuming_abstract_data_product_id: string;
  consuming_abstract_data_product: AbstractDataProductInfo;
  is_expiring_soon: boolean;
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
};
export type DenyOutputPortAsInputPortRequest = {
  consuming_data_product_id: string;
};
export type RenewOutputPortAsInputPortRequest = {
  consuming_data_product_id: string;
};
export type RemoveOutputPortAsInputPortRequest = {
  consuming_data_product_id: string;
};
export enum DecisionStatus {
  Approved = "approved",
  Pending = "pending",
  Denied = "denied",
  Expired = "expired",
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
  useRenewOutputPortAsInputPortMutation,
  useRemoveOutputPortAsInputPortMutation,
} = injectedRtkApi;
