import { api } from "@/store/api/services/generated/configurationDomainsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getEnvironment: build.query<
      GetEnvironmentApiResponse,
      GetEnvironmentApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/environments/${queryArg}`,
      }),
    }),
    updateEnvironmentIsGlobal: build.mutation<
      UpdateEnvironmentIsGlobalApiResponse,
      UpdateEnvironmentIsGlobalApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/environments/${queryArg.id}`,
        method: "PATCH",
        body: queryArg.environmentUpdateGlobal,
      }),
    }),
    getEnvironments: build.query<
      GetEnvironmentsApiResponse,
      GetEnvironmentsApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/environments` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetEnvironmentApiResponse =
  /** status 200 Successful Response */ Environment;
export type GetEnvironmentApiArg = string;
export type UpdateEnvironmentIsGlobalApiResponse =
  /** status 200 Successful Response */ Environment;
export type UpdateEnvironmentIsGlobalApiArg = {
  id: string;
  environmentUpdateGlobal: EnvironmentUpdateGlobal;
};
export type GetEnvironmentsApiResponse =
  /** status 200 Successful Response */ EnvironmentsGet;
export type GetEnvironmentsApiArg = void;
export type Environment = {
  id: string;
  name: string;
  acronym: string;
  context: string;
  is_default?: boolean;
  is_global?: boolean;
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
export type EnvironmentUpdateGlobal = {
  is_global: boolean;
};
export type EnvironmentGetItem = {
  id: string;
  name: string;
  acronym: string;
  context: string;
  is_default?: boolean;
  is_global?: boolean;
};
export type EnvironmentsGet = {
  environments: EnvironmentGetItem[];
};
export const {
  useGetEnvironmentQuery,
  useLazyGetEnvironmentQuery,
  useUpdateEnvironmentIsGlobalMutation,
  useGetEnvironmentsQuery,
  useLazyGetEnvironmentsQuery,
} = injectedRtkApi;
