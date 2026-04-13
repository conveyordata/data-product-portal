import { api } from "@/store/api/services/generated/configurationThemeSettingsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getTags: build.query<GetTagsApiResponse, GetTagsApiArg>({
      query: () => ({ url: `/api/v2/configuration/tags` }),
    }),
    createTag: build.mutation<CreateTagApiResponse, CreateTagApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/configuration/tags`,
        method: "POST",
        body: queryArg,
      }),
    }),
    updateTag: build.mutation<UpdateTagApiResponse, UpdateTagApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/configuration/tags/${queryArg.id}`,
        method: "PUT",
        body: queryArg.tagUpdate,
      }),
    }),
    removeTag: build.mutation<RemoveTagApiResponse, RemoveTagApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/configuration/tags/${queryArg}`,
        method: "DELETE",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetTagsApiResponse = /** status 200 Successful Response */ TagsGet;
export type GetTagsApiArg = void;
export type CreateTagApiResponse =
  /** status 200 Successful Response */ CreateTagResponse;
export type CreateTagApiArg = TagCreate;
export type UpdateTagApiResponse =
  /** status 200 Successful Response */ UpdateTagResponse;
export type UpdateTagApiArg = {
  id: string;
  tagUpdate: TagUpdate;
};
export type RemoveTagApiResponse = /** status 200 Successful Response */ any;
export type RemoveTagApiArg = string;
export type TagsGetItem = {
  id: string;
  value: string;
};
export type TagsGet = {
  tags: TagsGetItem[];
};
export type CreateTagResponse = {
  id: string;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type TagCreate = {
  value: string;
};
export type UpdateTagResponse = {
  id: string;
};
export type TagUpdate = {
  value: string;
};
export const {
  useGetTagsQuery,
  useLazyGetTagsQuery,
  useCreateTagMutation,
  useUpdateTagMutation,
  useRemoveTagMutation,
} = injectedRtkApi;
