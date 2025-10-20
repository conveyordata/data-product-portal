import { api } from '@/store/api/services/generated/eventsApi';

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
        getDeviceTokenApiAuthDeviceDeviceTokenPost: build.mutation<
            GetDeviceTokenApiAuthDeviceDeviceTokenPostApiResponse,
            GetDeviceTokenApiAuthDeviceDeviceTokenPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/auth/device/device_token',
                method: 'POST',
                params: {
                    client_id: queryArg.clientId,
                    scope: queryArg.scope,
                },
            }),
        }),
        getJwtTokenApiAuthDeviceJwtTokenPost: build.mutation<
            GetJwtTokenApiAuthDeviceJwtTokenPostApiResponse,
            GetJwtTokenApiAuthDeviceJwtTokenPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/auth/device/jwt_token',
                method: 'POST',
                params: {
                    client_id: queryArg.clientId,
                    device_code: queryArg.deviceCode,
                    grant_type: queryArg.grantType,
                },
            }),
        }),
        authorizeApiAuthUserGet: build.query<AuthorizeApiAuthUserGetApiResponse, AuthorizeApiAuthUserGetApiArg>({
            query: () => ({ url: '/api/auth/user' }),
        }),
        getAwsCredentialsApiAuthAwsCredentialsGet: build.query<
            GetAwsCredentialsApiAuthAwsCredentialsGetApiResponse,
            GetAwsCredentialsApiAuthAwsCredentialsGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/auth/aws_credentials',
                params: {
                    data_product_name: queryArg.dataProductName,
                    environment: queryArg.environment,
                },
            }),
        }),
        oauthMetadataWellKnownOauthAuthorizationServerGet: build.query<
            OauthMetadataWellKnownOauthAuthorizationServerGetApiResponse,
            OauthMetadataWellKnownOauthAuthorizationServerGetApiArg
        >({
            query: () => ({ url: '/.well-known/oauth-authorization-server' }),
        }),
        oauthProtectedResourceWellKnownOauthProtectedResourceGet: build.query<
            OauthProtectedResourceWellKnownOauthProtectedResourceGetApiResponse,
            OauthProtectedResourceWellKnownOauthProtectedResourceGetApiArg
        >({
            query: () => ({ url: '/.well-known/oauth-protected-resource' }),
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
export type GetDeviceTokenApiAuthDeviceDeviceTokenPostApiResponse = /** status 200 Successful Response */ any;
export type GetDeviceTokenApiAuthDeviceDeviceTokenPostApiArg = {
    clientId: string;
    scope?: string;
};
export type GetJwtTokenApiAuthDeviceJwtTokenPostApiResponse = /** status 200 Successful Response */ any;
export type GetJwtTokenApiAuthDeviceJwtTokenPostApiArg = {
    clientId: string;
    deviceCode: string;
    grantType: string;
};
export type AuthorizeApiAuthUserGetApiResponse = /** status 200 Successful Response */ User;
export type AuthorizeApiAuthUserGetApiArg = void;
export type GetAwsCredentialsApiAuthAwsCredentialsGetApiResponse = /** status 200 Successful Response */ AwsCredentials;
export type GetAwsCredentialsApiAuthAwsCredentialsGetApiArg = {
    dataProductName: string;
    environment: string;
};
export type OauthMetadataWellKnownOauthAuthorizationServerGetApiResponse = /** status 200 Successful Response */ any;
export type OauthMetadataWellKnownOauthAuthorizationServerGetApiArg = void;
export type OauthProtectedResourceWellKnownOauthProtectedResourceGetApiResponse =
    /** status 200 Successful Response */ any;
export type OauthProtectedResourceWellKnownOauthProtectedResourceGetApiArg = void;
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
export type User = {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
};
export type AwsCredentials = {
    AccessKeyId: string;
    SecretAccessKey: string;
    SessionToken: string;
    Expiration: string;
};
export const {
    useCheckAccessApiAuthzAccessActionGetQuery,
    useLazyCheckAccessApiAuthzAccessActionGetQuery,
    useIsAdminApiAuthzAdminGetQuery,
    useLazyIsAdminApiAuthzAdminGetQuery,
    useGetDeviceTokenApiAuthDeviceDeviceTokenPostMutation,
    useGetJwtTokenApiAuthDeviceJwtTokenPostMutation,
    useAuthorizeApiAuthUserGetQuery,
    useLazyAuthorizeApiAuthUserGetQuery,
    useGetAwsCredentialsApiAuthAwsCredentialsGetQuery,
    useLazyGetAwsCredentialsApiAuthAwsCredentialsGetQuery,
    useOauthMetadataWellKnownOauthAuthorizationServerGetQuery,
    useLazyOauthMetadataWellKnownOauthAuthorizationServerGetQuery,
    useOauthProtectedResourceWellKnownOauthProtectedResourceGetQuery,
    useLazyOauthProtectedResourceWellKnownOauthProtectedResourceGetQuery,
} = injectedRtkApi;
