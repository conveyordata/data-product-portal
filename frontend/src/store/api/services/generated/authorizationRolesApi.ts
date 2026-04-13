import { api } from "@/store/api/services/generated/authorizationRoleAssignmentsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    createRole: build.mutation<CreateRoleApiResponse, CreateRoleApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/authz/roles`,
        method: "POST",
        body: queryArg,
      }),
    }),
    removeRole: build.mutation<RemoveRoleApiResponse, RemoveRoleApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/authz/roles/${queryArg}`,
        method: "DELETE",
      }),
    }),
    updateRole: build.mutation<UpdateRoleApiResponse, UpdateRoleApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/authz/roles/${queryArg.id}`,
        method: "PUT",
        body: queryArg.updateRole,
      }),
    }),
    getRoles: build.query<GetRolesApiResponse, GetRolesApiArg>({
      query: (queryArg) => ({ url: `/api/v2/authz/roles/${queryArg}` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type CreateRoleApiResponse =
  /** status 200 Role successfully created */ Role;
export type CreateRoleApiArg = CreateRole;
export type RemoveRoleApiResponse = /** status 200 Successful Response */ any;
export type RemoveRoleApiArg = string;
export type UpdateRoleApiResponse =
  /** status 200 Role successfully updated */ Role;
export type UpdateRoleApiArg = {
  id: string;
  updateRole: UpdateRole;
};
export type GetRolesApiResponse =
  /** status 200 Successful Response */ GetRolesResponse;
export type GetRolesApiArg = Scope;
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
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type CreateRole = {
  name: string;
  scope: Scope;
  description: string;
  permissions: AuthorizationAction[];
};
export type UpdateRole = {
  name?: string | null;
  description?: string | null;
  permissions?: AuthorizationAction[] | null;
};
export type GetRolesResponse = {
  roles: Role[];
};
export const {
  useCreateRoleMutation,
  useRemoveRoleMutation,
  useUpdateRoleMutation,
  useGetRolesQuery,
  useLazyGetRolesQuery,
} = injectedRtkApi;
