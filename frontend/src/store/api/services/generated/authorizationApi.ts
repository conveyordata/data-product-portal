import { api } from "@/store/api/services/baseApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    checkAccess: build.query<CheckAccessApiResponse, CheckAccessApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/authz/access/${queryArg.action}`,
        params: {
          resource: queryArg.resource,
          domain: queryArg.domain,
        },
      }),
    }),
    isAdmin: build.query<IsAdminApiResponse, IsAdminApiArg>({
      query: () => ({ url: `/api/v2/authz/admin` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type CheckAccessApiResponse =
  /** status 200 Access check result */ AccessResponse;
export type CheckAccessApiArg = {
  action: AuthorizationAction;
  resource?: string | null;
  domain?: string | null;
};
export type IsAdminApiResponse =
  /** status 200 Successful Response */ IsAdminResponse;
export type IsAdminApiArg = void;
export type AccessResponse = {
  allowed: boolean;
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
export type IsAdminResponse = {
  is_admin: boolean;
  time?: string | null;
};
export const {
  useCheckAccessQuery,
  useLazyCheckAccessQuery,
  useIsAdminQuery,
  useLazyIsAdminQuery,
} = injectedRtkApi;
