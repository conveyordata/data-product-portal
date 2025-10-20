import { api } from '@/store/api/services/generated/usersApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getRolesApiRolesScopeGet: build.query<GetRolesApiRolesScopeGetApiResponse, GetRolesApiRolesScopeGetApiArg>({
            query: (queryArg) => ({ url: `/api/roles/${queryArg.scope}` }),
        }),
        createRoleApiRolesPost: build.mutation<CreateRoleApiRolesPostApiResponse, CreateRoleApiRolesPostApiArg>({
            query: (queryArg) => ({
                url: '/api/roles',
                method: 'POST',
                body: queryArg.createRole,
            }),
        }),
        updateRoleApiRolesPatch: build.mutation<UpdateRoleApiRolesPatchApiResponse, UpdateRoleApiRolesPatchApiArg>({
            query: (queryArg) => ({
                url: '/api/roles',
                method: 'PATCH',
                body: queryArg.updateRole,
            }),
        }),
        removeRoleApiRolesIdDelete: build.mutation<
            RemoveRoleApiRolesIdDeleteApiResponse,
            RemoveRoleApiRolesIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/roles/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetRolesApiRolesScopeGetApiResponse = /** status 200 Successful Response */ Role[];
export type GetRolesApiRolesScopeGetApiArg = {
    scope: Scope;
};
export type CreateRoleApiRolesPostApiResponse = /** status 200 Role successfully created */ Role;
export type CreateRoleApiRolesPostApiArg = {
    createRole: CreateRole;
};
export type UpdateRoleApiRolesPatchApiResponse = /** status 200 Role successfully updated */ Role;
export type UpdateRoleApiRolesPatchApiArg = {
    updateRole: UpdateRole;
};
export type RemoveRoleApiRolesIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveRoleApiRolesIdDeleteApiArg = {
    id: string;
};
export type Scope = 'dataset' | 'data_product' | 'domain' | 'global';
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
    id: string;
    name?: string | null;
    description?: string | null;
    permissions?: AuthorizationAction[] | null;
};
export const {
    useGetRolesApiRolesScopeGetQuery,
    useLazyGetRolesApiRolesScopeGetQuery,
    useCreateRoleApiRolesPostMutation,
    useUpdateRoleApiRolesPatchMutation,
    useRemoveRoleApiRolesIdDeleteMutation,
} = injectedRtkApi;
