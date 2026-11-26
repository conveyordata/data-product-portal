import { api } from "@/store/api/services/generated/groupsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getMachineUsers: build.query<
      GetMachineUsersApiResponse,
      GetMachineUsersApiArg
    >({
      query: () => ({ url: `/api/v2/machine-users` }),
    }),
    createMachineUser: build.mutation<
      CreateMachineUserApiResponse,
      CreateMachineUserApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/machine-users`,
        method: "POST",
        body: queryArg,
      }),
    }),
    getMachineUser: build.query<
      GetMachineUserApiResponse,
      GetMachineUserApiArg
    >({
      query: (queryArg) => ({ url: `/api/v2/machine-users/${queryArg}` }),
    }),
    updateMachineUser: build.mutation<
      UpdateMachineUserApiResponse,
      UpdateMachineUserApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/machine-users/${queryArg.id}`,
        method: "PUT",
        body: queryArg.machineUserUpdate,
      }),
    }),
    deleteMachineUser: build.mutation<
      DeleteMachineUserApiResponse,
      DeleteMachineUserApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/machine-users/${queryArg}`,
        method: "DELETE",
      }),
    }),
    createMachineUsersBatch: build.mutation<
      CreateMachineUsersBatchApiResponse,
      CreateMachineUsersBatchApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/machine-users/batch`,
        method: "POST",
        body: queryArg,
      }),
    }),
    deleteMachineUsersBatch: build.mutation<
      DeleteMachineUsersBatchApiResponse,
      DeleteMachineUsersBatchApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/machine-users/batch`,
        method: "DELETE",
        body: queryArg,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetMachineUsersApiResponse =
  /** status 200 Successful Response */ MachineUsersGetResponse;
export type GetMachineUsersApiArg = void;
export type CreateMachineUserApiResponse =
  /** status 200 Successful Response */ MachineUserCreateResponse;
export type CreateMachineUserApiArg = MachineUserCreate;
export type GetMachineUserApiResponse =
  /** status 200 Successful Response */ MachineUserGet;
export type GetMachineUserApiArg = string;
export type UpdateMachineUserApiResponse =
  /** status 200 Successful Response */ MachineUserUpdateResponse;
export type UpdateMachineUserApiArg = {
  id: string;
  machineUserUpdate: MachineUserUpdate;
};
export type DeleteMachineUserApiResponse = unknown;
export type DeleteMachineUserApiArg = string;
export type CreateMachineUsersBatchApiResponse =
  /** status 200 Successful Response */ IdentityBatchCreateResponse;
export type CreateMachineUsersBatchApiArg =
  IdentityBatchCreateRequestMachineUserCreate;
export type DeleteMachineUsersBatchApiResponse = unknown;
export type DeleteMachineUsersBatchApiArg = IdentityBatchDeleteRequest;
export type MachineUserGet = {
  id: string;
  external_id: string;
  display_name: string;
};
export type MachineUsersGetResponse = {
  machine_users: MachineUserGet[];
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
export type MachineUserCreateResponse = {
  id: string;
};
export type AppSharedSchemaNonEmptyStr3 = string;
export type MachineUserCreate = {
  external_id: AppSharedSchemaNonEmptyStr3;
  display_name: AppSharedSchemaNonEmptyStr3;
};
export type MachineUserUpdateResponse = {
  id: string;
};
export type MachineUserUpdate = {
  display_name: AppSharedSchemaNonEmptyStr3;
};
export type IdentityBatchCreateError = {
  item: any;
  errors: string[];
};
export type IdentityBatchCreateResponse = {
  ids: string[];
  errors: IdentityBatchCreateError[];
};
export type IdentityBatchCreateRequestMachineUserCreate = {
  items: {
    external_id: AppSharedSchemaNonEmptyStr3;
    display_name: AppSharedSchemaNonEmptyStr3;
  }[];
};
export type IdentityBatchDeleteRequest = {
  ids: string[];
};
export const {
  useGetMachineUsersQuery,
  useLazyGetMachineUsersQuery,
  useCreateMachineUserMutation,
  useGetMachineUserQuery,
  useLazyGetMachineUserQuery,
  useUpdateMachineUserMutation,
  useDeleteMachineUserMutation,
  useCreateMachineUsersBatchMutation,
  useDeleteMachineUsersBatchMutation,
} = injectedRtkApi;
