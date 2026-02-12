import { api } from "@/store/api/services/generated/pluginsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
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
export const {
  useApproveOutputPortAsInputPortMutation,
  useDenyOutputPortAsInputPortMutation,
  useRemoveOutputPortAsInputPortMutation,
} = injectedRtkApi;
