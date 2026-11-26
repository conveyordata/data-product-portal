import { api } from "@/store/api/services/generated/usersNotificationsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getGroups: build.query<GetGroupsApiResponse, GetGroupsApiArg>({
      query: () => ({ url: `/api/v2/groups` }),
    }),
    createGroup: build.mutation<CreateGroupApiResponse, CreateGroupApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/groups`,
        method: "POST",
        body: queryArg,
      }),
    }),
    getGroup: build.query<GetGroupApiResponse, GetGroupApiArg>({
      query: (queryArg) => ({ url: `/api/v2/groups/${queryArg}` }),
    }),
    updateGroup: build.mutation<UpdateGroupApiResponse, UpdateGroupApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/groups/${queryArg.id}`,
        method: "PUT",
        body: queryArg.groupUpdate,
      }),
    }),
    deleteGroup: build.mutation<DeleteGroupApiResponse, DeleteGroupApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/groups/${queryArg}`,
        method: "DELETE",
      }),
    }),
    createGroupsBatch: build.mutation<
      CreateGroupsBatchApiResponse,
      CreateGroupsBatchApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/groups/batch`,
        method: "POST",
        body: queryArg,
      }),
    }),
    deleteGroupsBatch: build.mutation<
      DeleteGroupsBatchApiResponse,
      DeleteGroupsBatchApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/groups/batch`,
        method: "DELETE",
        body: queryArg,
      }),
    }),
    getGroupMembers: build.query<
      GetGroupMembersApiResponse,
      GetGroupMembersApiArg
    >({
      query: (queryArg) => ({ url: `/api/v2/groups/${queryArg}/members` }),
    }),
    addGroupMembers: build.mutation<
      AddGroupMembersApiResponse,
      AddGroupMembersApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/groups/${queryArg.id}/members`,
        method: "POST",
        body: queryArg.groupMembersAdd,
      }),
    }),
    replaceGroupMembers: build.mutation<
      ReplaceGroupMembersApiResponse,
      ReplaceGroupMembersApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/groups/${queryArg.id}/members`,
        method: "PUT",
        body: queryArg.groupMembersReplace,
      }),
    }),
    removeGroupMembers: build.mutation<
      RemoveGroupMembersApiResponse,
      RemoveGroupMembersApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/groups/${queryArg.id}/members`,
        method: "DELETE",
        body: queryArg.groupMembersRemove,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetGroupsApiResponse =
  /** status 200 Successful Response */ GroupsGetResponse;
export type GetGroupsApiArg = void;
export type CreateGroupApiResponse =
  /** status 200 Successful Response */ GroupCreateResponse;
export type CreateGroupApiArg = GroupCreate;
export type GetGroupApiResponse =
  /** status 200 Successful Response */ GroupGet;
export type GetGroupApiArg = string;
export type UpdateGroupApiResponse =
  /** status 200 Successful Response */ GroupUpdateResponse;
export type UpdateGroupApiArg = {
  id: string;
  groupUpdate: GroupUpdate;
};
export type DeleteGroupApiResponse = unknown;
export type DeleteGroupApiArg = string;
export type CreateGroupsBatchApiResponse =
  /** status 200 Successful Response */ IdentityBatchCreateResponse;
export type CreateGroupsBatchApiArg = IdentityBatchCreateRequestGroupCreate;
export type DeleteGroupsBatchApiResponse = unknown;
export type DeleteGroupsBatchApiArg = IdentityBatchDeleteRequest;
export type GetGroupMembersApiResponse =
  /** status 200 Successful Response */ GroupMembershipsGetResponse;
export type GetGroupMembersApiArg = string;
export type AddGroupMembersApiResponse = unknown;
export type AddGroupMembersApiArg = {
  id: string;
  groupMembersAdd: GroupMembersAdd;
};
export type ReplaceGroupMembersApiResponse = unknown;
export type ReplaceGroupMembersApiArg = {
  id: string;
  groupMembersReplace: GroupMembersReplace;
};
export type RemoveGroupMembersApiResponse = unknown;
export type RemoveGroupMembersApiArg = {
  id: string;
  groupMembersRemove: GroupMembersRemove;
};
export type GroupGet = {
  id: string;
  external_id: string;
  display_name: string;
};
export type GroupsGetResponse = {
  groups: GroupGet[];
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
export type GroupCreateResponse = {
  id: string;
};
export type AppSharedSchemaNonEmptyStr3 = string;
export type GroupCreate = {
  external_id: AppSharedSchemaNonEmptyStr3;
  display_name: AppSharedSchemaNonEmptyStr3;
};
export type GroupUpdateResponse = {
  id: string;
};
export type GroupUpdate = {
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
export type IdentityBatchCreateRequestGroupCreate = {
  items: {
    external_id: AppSharedSchemaNonEmptyStr3;
    display_name: AppSharedSchemaNonEmptyStr3;
  }[];
};
export type IdentityBatchDeleteRequest = {
  ids: string[];
};
export type GroupMemberIdentityGet = {
  id: string;
  type: IdentityType;
  external_id: string;
};
export type GroupMembershipGet = {
  group_id: string;
  member_identity_id: string;
  member: GroupMemberIdentityGet;
};
export type GroupMembershipsGetResponse = {
  members: GroupMembershipGet[];
};
export type GroupMembersAdd = {
  member_identity_ids: string[];
};
export type GroupMembersReplace = {
  member_identity_ids: string[];
};
export type GroupMembersRemove = {
  member_identity_ids: string[];
};
export enum IdentityType {
  User = "user",
  Group = "group",
  MachineUser = "machine_user",
}
export const {
  useGetGroupsQuery,
  useLazyGetGroupsQuery,
  useCreateGroupMutation,
  useGetGroupQuery,
  useLazyGetGroupQuery,
  useUpdateGroupMutation,
  useDeleteGroupMutation,
  useCreateGroupsBatchMutation,
  useDeleteGroupsBatchMutation,
  useGetGroupMembersQuery,
  useLazyGetGroupMembersQuery,
  useAddGroupMembersMutation,
  useReplaceGroupMembersMutation,
  useRemoveGroupMembersMutation,
} = injectedRtkApi;
