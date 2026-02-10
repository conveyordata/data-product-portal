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
export type DataProductType = {
  id: string;
  name: string;
  description: string;
  icon_key: DataProductIconKey;
};
export type DataProductInfo = {
  name: string;
  type: DataProductType;
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
  data_product_id: string;
  data_product: DataProductInfo;
  output_port_id: string;
  status: DecisionStatus;
  input_port: OutputPort;
};
export type GetInputPortsForOutputPortResponse = {
  input_ports: InputPort[];
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
export type RemoveOutputPortAsInputPortRequest = {
  consuming_data_product_id: string;
};
export enum DataProductIconKey {
  Reporting = "reporting",
  Processing = "processing",
  Exploration = "exploration",
  Ingestion = "ingestion",
  MachineLearning = "machine_learning",
  Analytics = "analytics",
  Default = "default",
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
}
export const {
  useGetInputPortsForOutputPortQuery,
  useLazyGetInputPortsForOutputPortQuery,
  useApproveOutputPortAsInputPortMutation,
  useDenyOutputPortAsInputPortMutation,
  useRemoveOutputPortAsInputPortMutation,
} = injectedRtkApi;
