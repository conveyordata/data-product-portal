import { api } from '@/store/api/services/generated/tagsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getUsersApiUsersGet: build.query<GetUsersApiUsersGetApiResponse, GetUsersApiUsersGetApiArg>({
            query: () => ({ url: '/api/users' }),
        }),
        createUserApiUsersPost: build.mutation<CreateUserApiUsersPostApiResponse, CreateUserApiUsersPostApiArg>({
            query: (queryArg) => ({
                url: '/api/users',
                method: 'POST',
                body: queryArg.userCreate,
            }),
        }),
        removeUserApiUsersIdDelete: build.mutation<
            RemoveUserApiUsersIdDeleteApiResponse,
            RemoveUserApiUsersIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/users/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetUsersApiUsersGetApiResponse = /** status 200 Successful Response */ UsersGet[];
export type GetUsersApiUsersGetApiArg = void;
export type CreateUserApiUsersPostApiResponse = /** status 200 User successfully created */ {
    [key: string]: string;
};
export type CreateUserApiUsersPostApiArg = {
    userCreate: UserCreate;
};
export type RemoveUserApiUsersIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveUserApiUsersIdDeleteApiArg = {
    id: string;
};
export type User = {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
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
export type DecisionStatus = 'approved' | 'pending' | 'denied';
export type RoleAssignmentResponse = {
    id: string;
    user: User;
    role: Role;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: User | null;
    decided_on: string | null;
    decided_by: User | null;
};
export type UsersGet = {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
    global_role: RoleAssignmentResponse | null;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type UserCreate = {
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
};
export const {
    useGetUsersApiUsersGetQuery,
    useLazyGetUsersApiUsersGetQuery,
    useCreateUserApiUsersPostMutation,
    useRemoveUserApiUsersIdDeleteMutation,
} = injectedRtkApi;
