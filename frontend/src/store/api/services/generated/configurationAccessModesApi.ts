import { api } from "@/store/api/services/generated/configurationTagsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getAccessModes: build.query<
      GetAccessModesApiResponse,
      GetAccessModesApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/access_modes` }),
    }),
    createAccessMode: build.mutation<
      CreateAccessModeApiResponse,
      CreateAccessModeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/access_modes`,
        method: "POST",
        body: queryArg,
      }),
    }),
    updateAccessMode: build.mutation<
      UpdateAccessModeApiResponse,
      UpdateAccessModeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/access_modes/${queryArg.id}`,
        method: "PUT",
        body: queryArg.accessModeUpdate,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetAccessModesApiResponse =
  /** status 200 Successful Response */ GetAccessModes;
export type GetAccessModesApiArg = void;
export type CreateAccessModeApiResponse =
  /** status 200 Successful Response */ AccessMode;
export type CreateAccessModeApiArg = AccessModeCreate;
export type UpdateAccessModeApiResponse =
  /** status 200 Successful Response */ AccessMode;
export type UpdateAccessModeApiArg = {
  id: string;
  accessModeUpdate: AccessModeUpdate;
};
export type AccessMode = {
  id: string;
  name: string;
  description: string;
};
export type GetAccessModes = {
  access_modes: AccessMode[];
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
export type AccessModeCreate = {
  name: string;
  description: string;
};
export type AccessModeUpdate = {
  description: string;
};
export const {
  useGetAccessModesQuery,
  useLazyGetAccessModesQuery,
  useCreateAccessModeMutation,
  useUpdateAccessModeMutation,
} = injectedRtkApi;
