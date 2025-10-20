import { api } from '@/store/api/services/baseApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        checkAccessApiAuthzAccessActionGet: build.query<
            CheckAccessApiAuthzAccessActionGetApiResponse,
            CheckAccessApiAuthzAccessActionGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/authz/access/${queryArg.action}`,
                params: {
                    resource: queryArg.resource,
                    domain: queryArg.domain,
                },
            }),
        }),
        isAdminApiAuthzAdminGet: build.query<IsAdminApiAuthzAdminGetApiResponse, IsAdminApiAuthzAdminGetApiArg>({
            query: () => ({ url: '/api/authz/admin' }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type CheckAccessApiAuthzAccessActionGetApiResponse = /** status 200 Access check result */ AccessResponse;
export type CheckAccessApiAuthzAccessActionGetApiArg = {
    action: AuthorizationAction;
    resource?: string | null;
    domain?: string | null;
};
export type IsAdminApiAuthzAdminGetApiResponse = /** status 200 Admin role assignment */ boolean;
export type IsAdminApiAuthzAdminGetApiArg = void;
export type AccessResponse = {
    allowed: boolean;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
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
    | 413;
export const {
    useCheckAccessApiAuthzAccessActionGetQuery,
    useLazyCheckAccessApiAuthzAccessActionGetQuery,
    useIsAdminApiAuthzAdminGetQuery,
    useLazyIsAdminApiAuthzAdminGetQuery,
} = injectedRtkApi;
