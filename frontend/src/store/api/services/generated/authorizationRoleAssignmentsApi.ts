import { api } from "@/store/api/services/baseApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    becomeAdmin: build.mutation<BecomeAdminApiResponse, BecomeAdminApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/global/become_admin`,
        method: "POST",
        body: queryArg,
      }),
    }),
    revokeAdmin: build.mutation<RevokeAdminApiResponse, RevokeAdminApiArg>({
      query: () => ({
        url: `/api/v2/authz/role_assignments/global/revoke_admin`,
        method: "POST",
      }),
    }),
    createGlobalRoleAssignment: build.mutation<
      CreateGlobalRoleAssignmentApiResponse,
      CreateGlobalRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/global`,
        method: "POST",
        body: queryArg,
      }),
    }),
    listGlobalRoleAssignments: build.query<
      ListGlobalRoleAssignmentsApiResponse,
      ListGlobalRoleAssignmentsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/global`,
        params: {
          user_id: queryArg.userId,
          role_id: queryArg.roleId,
        },
      }),
    }),
    deleteGlobalRoleAssignment: build.mutation<
      DeleteGlobalRoleAssignmentApiResponse,
      DeleteGlobalRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/global/${queryArg}`,
        method: "DELETE",
      }),
    }),
    decideGlobalRoleAssignment: build.mutation<
      DecideGlobalRoleAssignmentApiResponse,
      DecideGlobalRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/global/${queryArg.id}/decide`,
        method: "POST",
        body: queryArg.decideGlobalRoleAssignment,
      }),
    }),
    modifyGlobalRoleAssignment: build.mutation<
      ModifyGlobalRoleAssignmentApiResponse,
      ModifyGlobalRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/global/${queryArg.id}/role`,
        method: "PUT",
        body: queryArg.modifyGlobalRoleAssignment,
      }),
    }),
    deleteDataProductRoleAssignment: build.mutation<
      DeleteDataProductRoleAssignmentApiResponse,
      DeleteDataProductRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/data_product/${queryArg}`,
        method: "DELETE",
      }),
    }),
    modifyDataProductRoleAssignment: build.mutation<
      ModifyDataProductRoleAssignmentApiResponse,
      ModifyDataProductRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/data_product/${queryArg.id}`,
        method: "PUT",
        body: queryArg.modifyDataProductRoleAssignment,
      }),
    }),
    listDataProductRoleAssignments: build.query<
      ListDataProductRoleAssignmentsApiResponse,
      ListDataProductRoleAssignmentsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/data_product`,
        params: {
          data_product_id: queryArg.dataProductId,
          user_id: queryArg.userId,
          role_id: queryArg.roleId,
          decision: queryArg.decision,
        },
      }),
    }),
    createDataProductRoleAssignment: build.mutation<
      CreateDataProductRoleAssignmentApiResponse,
      CreateDataProductRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/data_product`,
        method: "POST",
        body: queryArg,
      }),
    }),
    requestDataProductRoleAssignment: build.mutation<
      RequestDataProductRoleAssignmentApiResponse,
      RequestDataProductRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/data_product/request`,
        method: "POST",
        body: queryArg,
      }),
    }),
    decideDataProductRoleAssignment: build.mutation<
      DecideDataProductRoleAssignmentApiResponse,
      DecideDataProductRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/data_product/${queryArg.id}/decide`,
        method: "POST",
        body: queryArg.decideDataProductRoleAssignment,
      }),
    }),
    deleteOutputPortRoleAssignment: build.mutation<
      DeleteOutputPortRoleAssignmentApiResponse,
      DeleteOutputPortRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/output_port/${queryArg}`,
        method: "DELETE",
      }),
    }),
    modifyOutputPortRoleAssignment: build.mutation<
      ModifyOutputPortRoleAssignmentApiResponse,
      ModifyOutputPortRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/output_port/${queryArg.id}`,
        method: "PUT",
        body: queryArg.modifyOutputPortRoleAssignment,
      }),
    }),
    listOutputPortRoleAssignments: build.query<
      ListOutputPortRoleAssignmentsApiResponse,
      ListOutputPortRoleAssignmentsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/output_port`,
        params: {
          output_port_id: queryArg.outputPortId,
          user_id: queryArg.userId,
          role_id: queryArg.roleId,
          decision: queryArg.decision,
        },
      }),
    }),
    createOutputPortRoleAssignment: build.mutation<
      CreateOutputPortRoleAssignmentApiResponse,
      CreateOutputPortRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/output_port`,
        method: "POST",
        body: queryArg,
      }),
    }),
    requestOutputPortRoleAssignment: build.mutation<
      RequestOutputPortRoleAssignmentApiResponse,
      RequestOutputPortRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/output_port/request`,
        method: "POST",
        body: queryArg,
      }),
    }),
    decideOutputPortRoleAssignment: build.mutation<
      DecideOutputPortRoleAssignmentApiResponse,
      DecideOutputPortRoleAssignmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/authz/role_assignments/output_port/${queryArg.id}/decide`,
        method: "POST",
        body: queryArg.decideOutputPortRoleAssignment,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type BecomeAdminApiResponse = /** status 200 Successful Response */ any;
export type BecomeAdminApiArg = BecomeAdmin;
export type RevokeAdminApiResponse = /** status 200 Successful Response */ any;
export type RevokeAdminApiArg = void;
export type CreateGlobalRoleAssignmentApiResponse =
  /** status 200 Successful Response */ GlobalRoleAssignmentResponse;
export type CreateGlobalRoleAssignmentApiArg = CreateGlobalRoleAssignment;
export type ListGlobalRoleAssignmentsApiResponse =
  /** status 200 Successful Response */ ListGlobalRoleAssignmentsResponse;
export type ListGlobalRoleAssignmentsApiArg = {
  userId?: string | null;
  roleId?: string | null;
};
export type DeleteGlobalRoleAssignmentApiResponse =
  /** status 200 Successful Response */ DeleteGlobalRoleAssignmentResponse;
export type DeleteGlobalRoleAssignmentApiArg = string;
export type DecideGlobalRoleAssignmentApiResponse =
  /** status 200 Successful Response */ GlobalRoleAssignmentResponse;
export type DecideGlobalRoleAssignmentApiArg = {
  id: string;
  decideGlobalRoleAssignment: DecideGlobalRoleAssignment;
};
export type ModifyGlobalRoleAssignmentApiResponse =
  /** status 200 Successful Response */ GlobalRoleAssignmentResponse;
export type ModifyGlobalRoleAssignmentApiArg = {
  id: string;
  modifyGlobalRoleAssignment: ModifyGlobalRoleAssignment;
};
export type DeleteDataProductRoleAssignmentApiResponse =
  /** status 200 Successful Response */ DeleteDataProductRoleAssignmentResponse;
export type DeleteDataProductRoleAssignmentApiArg = string;
export type ModifyDataProductRoleAssignmentApiResponse =
  /** status 200 Successful Response */ DataProductRoleAssignmentResponse;
export type ModifyDataProductRoleAssignmentApiArg = {
  id: string;
  modifyDataProductRoleAssignment: ModifyDataProductRoleAssignment;
};
export type ListDataProductRoleAssignmentsApiResponse =
  /** status 200 Successful Response */ ListDataProductRoleAssignmentsResponse;
export type ListDataProductRoleAssignmentsApiArg = {
  dataProductId?: string | null;
  userId?: string | null;
  roleId?: string | null;
  decision?: DecisionStatus | null;
};
export type CreateDataProductRoleAssignmentApiResponse =
  /** status 200 Successful Response */ DataProductRoleAssignmentResponse;
export type CreateDataProductRoleAssignmentApiArg =
  CreateDataProductRoleAssignment;
export type RequestDataProductRoleAssignmentApiResponse =
  /** status 200 Successful Response */ DataProductRoleAssignmentResponse;
export type RequestDataProductRoleAssignmentApiArg =
  RequestDataProductRoleAssignment;
export type DecideDataProductRoleAssignmentApiResponse =
  /** status 200 Successful Response */ DataProductRoleAssignmentResponse;
export type DecideDataProductRoleAssignmentApiArg = {
  id: string;
  decideDataProductRoleAssignment: DecideDataProductRoleAssignment;
};
export type DeleteOutputPortRoleAssignmentApiResponse =
  /** status 200 Successful Response */ DeleteOutputPortRoleAssignmentResponse;
export type DeleteOutputPortRoleAssignmentApiArg = string;
export type ModifyOutputPortRoleAssignmentApiResponse =
  /** status 200 Successful Response */ OutputPortRoleAssignmentResponse;
export type ModifyOutputPortRoleAssignmentApiArg = {
  id: string;
  modifyOutputPortRoleAssignment: ModifyOutputPortRoleAssignment;
};
export type ListOutputPortRoleAssignmentsApiResponse =
  /** status 200 Successful Response */ ListOutputPortRoleAssignmentsResponse;
export type ListOutputPortRoleAssignmentsApiArg = {
  outputPortId?: string | null;
  userId?: string | null;
  roleId?: string | null;
  decision?: DecisionStatus | null;
};
export type CreateOutputPortRoleAssignmentApiResponse =
  /** status 200 Successful Response */ OutputPortRoleAssignmentResponse;
export type CreateOutputPortRoleAssignmentApiArg =
  CreateOutputPortRoleAssignment;
export type RequestOutputPortRoleAssignmentApiResponse =
  /** status 200 Successful Response */ OutputPortRoleAssignmentResponse;
export type RequestOutputPortRoleAssignmentApiArg =
  RequestOutputPortRoleAssignment;
export type DecideOutputPortRoleAssignmentApiResponse =
  /** status 200 Successful Response */ OutputPortRoleAssignmentResponse;
export type DecideOutputPortRoleAssignmentApiArg = {
  id: string;
  decideOutputPortRoleAssignment: DecideOutputPortRoleAssignment;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type BecomeAdmin = {
  expiry: string;
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
export type Scope = "dataset" | "data_product" | "domain" | "global";
export type AuthorizationAction =
  | 101
  | 102
  | 103
  | 104
  | 105
  | 106
  | 107
  | 301
  | 302
  | 303
  | 304
  | 305
  | 306
  | 307
  | 308
  | 309
  | 310
  | 311
  | 312
  | 313
  | 314
  | 315
  | 401
  | 402
  | 403
  | 404
  | 405
  | 406
  | 407
  | 408
  | 409
  | 410
  | 411
  | 412
  | 413
  | 414;
export type Prototype = 0 | 1 | 2 | 3;
export type Role = {
  name: string;
  scope: Scope;
  description: string;
  permissions: AuthorizationAction[];
  id: string;
  prototype: Prototype;
};
export type DecisionStatus = "approved" | "pending" | "denied";
export type GlobalRoleAssignmentResponse = {
  id: string;
  user: User;
  role: Role;
  decision: DecisionStatus;
  requested_on: string | null;
  requested_by: User | null;
  decided_on: string | null;
  decided_by: User | null;
};
export type CreateGlobalRoleAssignment = {
  user_id: string;
  role_id: string | "admin";
};
export type ListGlobalRoleAssignmentsResponse = {
  role_assignments: GlobalRoleAssignmentResponse[];
};
export type DeleteGlobalRoleAssignmentResponse = {
  id: string;
};
export type DecideGlobalRoleAssignment = {
  decision: DecisionStatus;
};
export type ModifyGlobalRoleAssignment = {
  role_id: string | "admin";
};
export type DeleteDataProductRoleAssignmentResponse = {
  id: string;
  data_product_id: string;
};
export type DataProductStatus = "pending" | "active" | "archived";
export type DataProductIconKey =
  | "reporting"
  | "processing"
  | "exploration"
  | "ingestion"
  | "machine_learning"
  | "analytics"
  | "default";
export type DataProductType = {
  id: string;
  name: string;
  description: string;
  icon_key: DataProductIconKey;
};
export type DataProduct = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: DataProductStatus;
  type: DataProductType;
};
export type DataProductRoleAssignmentResponse = {
  id: string;
  data_product: DataProduct;
  user: User;
  role: Role | null;
  decision: DecisionStatus;
  requested_on: string | null;
  requested_by: User | null;
  decided_on: string | null;
  decided_by: User | null;
};
export type ModifyDataProductRoleAssignment = {
  role_id: string;
};
export type ListDataProductRoleAssignmentsResponse = {
  role_assignments: DataProductRoleAssignmentResponse[];
};
export type CreateDataProductRoleAssignment = {
  user_id: string;
  role_id: string;
  data_product_id: string;
};
export type RequestDataProductRoleAssignment = {
  user_id: string;
  role_id: string;
  data_product_id: string;
};
export type DecideDataProductRoleAssignment = {
  decision: DecisionStatus;
};
export type DeleteOutputPortRoleAssignmentResponse = {
  id: string;
  output_port_id: string;
};
export type OutputPortStatus = "pending" | "active" | "archived";
export type OutputPortAccessType = "public" | "restricted" | "private";
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
export type OutputPortRoleAssignmentResponse = {
  id: string;
  output_port: OutputPort;
  user: User;
  role: Role | null;
  decision: DecisionStatus;
  requested_on: string | null;
  requested_by: User | null;
  decided_on: string | null;
  decided_by: User | null;
};
export type ModifyOutputPortRoleAssignment = {
  role_id: string;
};
export type ListOutputPortRoleAssignmentsResponse = {
  role_assignments: OutputPortRoleAssignmentResponse[];
};
export type CreateOutputPortRoleAssignment = {
  user_id: string;
  role_id: string;
  output_port_id: string;
};
export type RequestOutputPortRoleAssignment = {
  user_id: string;
  role_id: string;
  output_port_id: string;
};
export type DecideOutputPortRoleAssignment = {
  decision: DecisionStatus;
};
export const {
  useBecomeAdminMutation,
  useRevokeAdminMutation,
  useCreateGlobalRoleAssignmentMutation,
  useListGlobalRoleAssignmentsQuery,
  useLazyListGlobalRoleAssignmentsQuery,
  useDeleteGlobalRoleAssignmentMutation,
  useDecideGlobalRoleAssignmentMutation,
  useModifyGlobalRoleAssignmentMutation,
  useDeleteDataProductRoleAssignmentMutation,
  useModifyDataProductRoleAssignmentMutation,
  useListDataProductRoleAssignmentsQuery,
  useLazyListDataProductRoleAssignmentsQuery,
  useCreateDataProductRoleAssignmentMutation,
  useRequestDataProductRoleAssignmentMutation,
  useDecideDataProductRoleAssignmentMutation,
  useDeleteOutputPortRoleAssignmentMutation,
  useModifyOutputPortRoleAssignmentMutation,
  useListOutputPortRoleAssignmentsQuery,
  useLazyListOutputPortRoleAssignmentsQuery,
  useCreateOutputPortRoleAssignmentMutation,
  useRequestOutputPortRoleAssignmentMutation,
  useDecideOutputPortRoleAssignmentMutation,
} = injectedRtkApi;
