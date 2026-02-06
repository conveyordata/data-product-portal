import { api } from "@/store/api/services/generated/authorizationRolesApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    removeUser: build.mutation<RemoveUserApiResponse, RemoveUserApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/users/${queryArg}`,
        method: "DELETE",
      }),
    }),
    getUsers: build.query<GetUsersApiResponse, GetUsersApiArg>({
      query: () => ({ url: `/api/v2/users` }),
    }),
    createUser: build.mutation<CreateUserApiResponse, CreateUserApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/users`,
        method: "POST",
        body: queryArg,
      }),
    }),
    setCanBecomeAdmin: build.mutation<
      SetCanBecomeAdminApiResponse,
      SetCanBecomeAdminApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/users/set_can_become_admin`,
        method: "PUT",
        body: queryArg,
      }),
    }),
    markTourAsSeen: build.mutation<
      MarkTourAsSeenApiResponse,
      MarkTourAsSeenApiArg
    >({
      query: () => ({ url: `/api/v2/users/current/seen_tour`, method: "POST" }),
    }),
    getUserPendingActions: build.query<
      GetUserPendingActionsApiResponse,
      GetUserPendingActionsApiArg
    >({
      query: () => ({ url: `/api/v2/users/current/pending_actions` }),
    }),
    getCurrentUser: build.query<
      GetCurrentUserApiResponse,
      GetCurrentUserApiArg
    >({
      query: () => ({ url: `/api/v2/users/current` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type RemoveUserApiResponse = /** status 200 Successful Response */ any;
export type RemoveUserApiArg = string;
export type GetUsersApiResponse =
  /** status 200 Successful Response */ GetUsersResponse;
export type GetUsersApiArg = void;
export type CreateUserApiResponse =
  /** status 200 User successfully created */ UserCreateResponse;
export type CreateUserApiArg = UserCreate;
export type SetCanBecomeAdminApiResponse =
  /** status 200 Successful Response */ any;
export type SetCanBecomeAdminApiArg = CanBecomeAdminUpdate;
export type MarkTourAsSeenApiResponse =
  /** status 200 Successful Response */ any;
export type MarkTourAsSeenApiArg = void;
export type GetUserPendingActionsApiResponse =
  /** status 200 Successful Response */ PendingActionResponse;
export type GetUserPendingActionsApiArg = void;
export type GetCurrentUserApiResponse =
  /** status 200 Successful Response */ User;
export type GetCurrentUserApiArg = void;
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
export type UsersGet = {
  id: string;
  email: string;
  external_id: string;
  first_name: string;
  last_name: string;
  has_seen_tour: boolean;
  can_become_admin: boolean;
  admin_expiry?: string | null;
  global_role: GlobalRoleAssignmentResponse | null;
};
export type GetUsersResponse = {
  users: UsersGet[];
};
export type UserCreateResponse = {
  id: string;
};
export type UserCreate = {
  email: string;
  external_id: string;
  first_name: string;
  last_name: string;
};
export type CanBecomeAdminUpdate = {
  user_id: string;
  can_become_admin: boolean;
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
export type DataProductOutputPortPendingAction = {
  id: string;
  justification: string;
  data_product_id: string;
  output_port_id: string;
  status: DecisionStatus;
  requested_on: string;
  output_port: OutputPort;
  data_product: DataProduct;
  requested_by: User;
  denied_by: User | null;
  approved_by: User | null;
  pending_action_type?: "DataProductOutputPort";
};
export type TechnicalAssetOutputPortPendingAction = {
  id: string;
  output_port_id: string;
  technical_asset_id: string;
  status: DecisionStatus;
  requested_on: string;
  denied_on: string | null;
  approved_on: string | null;
  requested_by: User;
  denied_by: User | null;
  approved_by: User | null;
  pending_action_type?: "TechnicalAssetOutputPort";
};
export type DataProductRoleAssignmentPendingAction = {
  id: string;
  data_product: DataProduct;
  user: User;
  role: Role | null;
  decision: DecisionStatus;
  requested_on: string | null;
  requested_by: User | null;
  decided_on: string | null;
  decided_by: User | null;
  pending_action_type?: "DataProductRoleAssignment";
};
export type PendingActionResponse = {
  pending_actions: (
    | DataProductOutputPortPendingAction
    | TechnicalAssetOutputPortPendingAction
    | DataProductRoleAssignmentPendingAction
  )[];
};
export const {
  useRemoveUserMutation,
  useGetUsersQuery,
  useLazyGetUsersQuery,
  useCreateUserMutation,
  useSetCanBecomeAdminMutation,
  useMarkTourAsSeenMutation,
  useGetUserPendingActionsQuery,
  useLazyGetUserPendingActionsQuery,
  useGetCurrentUserQuery,
  useLazyGetCurrentUserQuery,
} = injectedRtkApi;
