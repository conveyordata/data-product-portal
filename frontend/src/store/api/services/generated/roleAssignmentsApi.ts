import { api } from '@/store/api/services/generated/rolesApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        listAssignmentsApiRoleAssignmentsGlobalGet: build.query<
            ListAssignmentsApiRoleAssignmentsGlobalGetApiResponse,
            ListAssignmentsApiRoleAssignmentsGlobalGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/role_assignments/global',
                params: {
                    user_id: queryArg.userId,
                    role_id: queryArg.roleId,
                },
            }),
        }),
        createAssignmentApiRoleAssignmentsGlobalPost: build.mutation<
            CreateAssignmentApiRoleAssignmentsGlobalPostApiResponse,
            CreateAssignmentApiRoleAssignmentsGlobalPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/role_assignments/global',
                method: 'POST',
                body: queryArg.appRoleAssignmentsGlobalSchemaCreateRoleAssignment,
            }),
        }),
        deleteAssignmentApiRoleAssignmentsGlobalIdDelete: build.mutation<
            DeleteAssignmentApiRoleAssignmentsGlobalIdDeleteApiResponse,
            DeleteAssignmentApiRoleAssignmentsGlobalIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/global/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
        decideAssignmentApiRoleAssignmentsGlobalIdDecidePatch: build.mutation<
            DecideAssignmentApiRoleAssignmentsGlobalIdDecidePatchApiResponse,
            DecideAssignmentApiRoleAssignmentsGlobalIdDecidePatchApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/global/${queryArg.id}/decide`,
                method: 'PATCH',
                body: queryArg.decideRoleAssignment,
            }),
        }),
        modifyAssignedRoleApiRoleAssignmentsGlobalIdRolePatch: build.mutation<
            ModifyAssignedRoleApiRoleAssignmentsGlobalIdRolePatchApiResponse,
            ModifyAssignedRoleApiRoleAssignmentsGlobalIdRolePatchApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/global/${queryArg.id}/role`,
                method: 'PATCH',
                body: queryArg.appRoleAssignmentsGlobalSchemaModifyRoleAssignment,
            }),
        }),
        listAssignmentsApiRoleAssignmentsDataProductGet: build.query<
            ListAssignmentsApiRoleAssignmentsDataProductGetApiResponse,
            ListAssignmentsApiRoleAssignmentsDataProductGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/role_assignments/data_product',
                params: {
                    data_product_id: queryArg.dataProductId,
                    user_id: queryArg.userId,
                    role_id: queryArg.roleId,
                    decision: queryArg.decision,
                },
            }),
        }),
        createAssignmentApiRoleAssignmentsDataProductIdPost: build.mutation<
            CreateAssignmentApiRoleAssignmentsDataProductIdPostApiResponse,
            CreateAssignmentApiRoleAssignmentsDataProductIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/data_product/${queryArg.id}`,
                method: 'POST',
                body: queryArg.appRoleAssignmentsDataProductSchemaCreateRoleAssignment,
            }),
        }),
        deleteAssignmentApiRoleAssignmentsDataProductIdDelete: build.mutation<
            DeleteAssignmentApiRoleAssignmentsDataProductIdDeleteApiResponse,
            DeleteAssignmentApiRoleAssignmentsDataProductIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/data_product/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
        modifyAssignedRoleApiRoleAssignmentsDataProductIdPatch: build.mutation<
            ModifyAssignedRoleApiRoleAssignmentsDataProductIdPatchApiResponse,
            ModifyAssignedRoleApiRoleAssignmentsDataProductIdPatchApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/data_product/${queryArg.id}`,
                method: 'PATCH',
                body: queryArg.appRoleAssignmentsDataProductSchemaModifyRoleAssignment,
            }),
        }),
        requestAssignmentApiRoleAssignmentsDataProductRequestIdPost: build.mutation<
            RequestAssignmentApiRoleAssignmentsDataProductRequestIdPostApiResponse,
            RequestAssignmentApiRoleAssignmentsDataProductRequestIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/data_product/request/${queryArg.id}`,
                method: 'POST',
                body: queryArg.appRoleAssignmentsDataProductSchemaCreateRoleAssignment,
            }),
        }),
        decideAssignmentApiRoleAssignmentsDataProductIdDecidePatch: build.mutation<
            DecideAssignmentApiRoleAssignmentsDataProductIdDecidePatchApiResponse,
            DecideAssignmentApiRoleAssignmentsDataProductIdDecidePatchApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/data_product/${queryArg.id}/decide`,
                method: 'PATCH',
                body: queryArg.decideRoleAssignment,
            }),
        }),
        listAssignmentsApiRoleAssignmentsDatasetGet: build.query<
            ListAssignmentsApiRoleAssignmentsDatasetGetApiResponse,
            ListAssignmentsApiRoleAssignmentsDatasetGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/role_assignments/dataset',
                params: {
                    dataset_id: queryArg.datasetId,
                    user_id: queryArg.userId,
                    role_id: queryArg.roleId,
                    decision: queryArg.decision,
                },
            }),
        }),
        createAssignmentApiRoleAssignmentsDatasetIdPost: build.mutation<
            CreateAssignmentApiRoleAssignmentsDatasetIdPostApiResponse,
            CreateAssignmentApiRoleAssignmentsDatasetIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/dataset/${queryArg.id}`,
                method: 'POST',
                body: queryArg.appRoleAssignmentsDatasetSchemaCreateRoleAssignment,
            }),
        }),
        deleteAssignmentApiRoleAssignmentsDatasetIdDelete: build.mutation<
            DeleteAssignmentApiRoleAssignmentsDatasetIdDeleteApiResponse,
            DeleteAssignmentApiRoleAssignmentsDatasetIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/dataset/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
        modifyAssignedRoleApiRoleAssignmentsDatasetIdPatch: build.mutation<
            ModifyAssignedRoleApiRoleAssignmentsDatasetIdPatchApiResponse,
            ModifyAssignedRoleApiRoleAssignmentsDatasetIdPatchApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/dataset/${queryArg.id}`,
                method: 'PATCH',
                body: queryArg.appRoleAssignmentsDatasetSchemaModifyRoleAssignment,
            }),
        }),
        requestAssignmentApiRoleAssignmentsDatasetRequestIdPost: build.mutation<
            RequestAssignmentApiRoleAssignmentsDatasetRequestIdPostApiResponse,
            RequestAssignmentApiRoleAssignmentsDatasetRequestIdPostApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/dataset/request/${queryArg.id}`,
                method: 'POST',
                body: queryArg.appRoleAssignmentsDatasetSchemaCreateRoleAssignment,
            }),
        }),
        decideAssignmentApiRoleAssignmentsDatasetIdDecidePatch: build.mutation<
            DecideAssignmentApiRoleAssignmentsDatasetIdDecidePatchApiResponse,
            DecideAssignmentApiRoleAssignmentsDatasetIdDecidePatchApiArg
        >({
            query: (queryArg) => ({
                url: `/api/role_assignments/dataset/${queryArg.id}/decide`,
                method: 'PATCH',
                body: queryArg.decideRoleAssignment,
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type ListAssignmentsApiRoleAssignmentsGlobalGetApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse[];
export type ListAssignmentsApiRoleAssignmentsGlobalGetApiArg = {
    userId?: string | null;
    roleId?: string | null;
};
export type CreateAssignmentApiRoleAssignmentsGlobalPostApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse;
export type CreateAssignmentApiRoleAssignmentsGlobalPostApiArg = {
    appRoleAssignmentsGlobalSchemaCreateRoleAssignment: CreateRoleAssignment;
};
export type DeleteAssignmentApiRoleAssignmentsGlobalIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type DeleteAssignmentApiRoleAssignmentsGlobalIdDeleteApiArg = {
    id: string;
};
export type DecideAssignmentApiRoleAssignmentsGlobalIdDecidePatchApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse;
export type DecideAssignmentApiRoleAssignmentsGlobalIdDecidePatchApiArg = {
    id: string;
    decideRoleAssignment: DecideRoleAssignment;
};
export type ModifyAssignedRoleApiRoleAssignmentsGlobalIdRolePatchApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse;
export type ModifyAssignedRoleApiRoleAssignmentsGlobalIdRolePatchApiArg = {
    id: string;
    appRoleAssignmentsGlobalSchemaModifyRoleAssignment: ModifyRoleAssignment;
};
export type ListAssignmentsApiRoleAssignmentsDataProductGetApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse2[];
export type ListAssignmentsApiRoleAssignmentsDataProductGetApiArg = {
    dataProductId?: string | null;
    userId?: string | null;
    roleId?: string | null;
    decision?: DecisionStatus | null;
};
export type CreateAssignmentApiRoleAssignmentsDataProductIdPostApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse2;
export type CreateAssignmentApiRoleAssignmentsDataProductIdPostApiArg = {
    id: string;
    appRoleAssignmentsDataProductSchemaCreateRoleAssignment: CreateRoleAssignment2;
};
export type DeleteAssignmentApiRoleAssignmentsDataProductIdDeleteApiResponse =
    /** status 200 Successful Response */ any;
export type DeleteAssignmentApiRoleAssignmentsDataProductIdDeleteApiArg = {
    id: string;
};
export type ModifyAssignedRoleApiRoleAssignmentsDataProductIdPatchApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse2;
export type ModifyAssignedRoleApiRoleAssignmentsDataProductIdPatchApiArg = {
    id: string;
    appRoleAssignmentsDataProductSchemaModifyRoleAssignment: ModifyRoleAssignment2;
};
export type RequestAssignmentApiRoleAssignmentsDataProductRequestIdPostApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse2;
export type RequestAssignmentApiRoleAssignmentsDataProductRequestIdPostApiArg = {
    id: string;
    appRoleAssignmentsDataProductSchemaCreateRoleAssignment: CreateRoleAssignment2;
};
export type DecideAssignmentApiRoleAssignmentsDataProductIdDecidePatchApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse2;
export type DecideAssignmentApiRoleAssignmentsDataProductIdDecidePatchApiArg = {
    id: string;
    decideRoleAssignment: DecideRoleAssignment;
};
export type ListAssignmentsApiRoleAssignmentsDatasetGetApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse3[];
export type ListAssignmentsApiRoleAssignmentsDatasetGetApiArg = {
    datasetId?: string | null;
    userId?: string | null;
    roleId?: string | null;
    decision?: DecisionStatus | null;
};
export type CreateAssignmentApiRoleAssignmentsDatasetIdPostApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse3;
export type CreateAssignmentApiRoleAssignmentsDatasetIdPostApiArg = {
    id: string;
    appRoleAssignmentsDatasetSchemaCreateRoleAssignment: CreateRoleAssignment3;
};
export type DeleteAssignmentApiRoleAssignmentsDatasetIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type DeleteAssignmentApiRoleAssignmentsDatasetIdDeleteApiArg = {
    id: string;
};
export type ModifyAssignedRoleApiRoleAssignmentsDatasetIdPatchApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse3;
export type ModifyAssignedRoleApiRoleAssignmentsDatasetIdPatchApiArg = {
    id: string;
    appRoleAssignmentsDatasetSchemaModifyRoleAssignment: ModifyRoleAssignment3;
};
export type RequestAssignmentApiRoleAssignmentsDatasetRequestIdPostApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse3;
export type RequestAssignmentApiRoleAssignmentsDatasetRequestIdPostApiArg = {
    id: string;
    appRoleAssignmentsDatasetSchemaCreateRoleAssignment: CreateRoleAssignment3;
};
export type DecideAssignmentApiRoleAssignmentsDatasetIdDecidePatchApiResponse =
    /** status 200 Successful Response */ RoleAssignmentResponse3;
export type DecideAssignmentApiRoleAssignmentsDatasetIdDecidePatchApiArg = {
    id: string;
    decideRoleAssignment: DecideRoleAssignment;
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
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type CreateRoleAssignment = {
    user_id: string;
    role_id: string | 'admin';
};
export type DecideRoleAssignment = {
    decision: DecisionStatus;
};
export type ModifyRoleAssignment = {
    role_id: string | 'admin';
};
export type DataProductStatus = 'pending' | 'active' | 'archived';
export type DataProductIconKey =
    | 'reporting'
    | 'processing'
    | 'exploration'
    | 'ingestion'
    | 'machine_learning'
    | 'analytics'
    | 'default';
export type DataProductType = {
    id: string;
    name: string;
    description: string;
    icon_key: DataProductIconKey;
};
export type DataProduct = {
    id: string;
    name: string;
    namespace: string;
    description: string;
    status: DataProductStatus;
    type: DataProductType;
};
export type RoleAssignmentResponse2 = {
    id: string;
    data_product: DataProduct;
    user: User;
    role: Role | null;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: User | null;
    decided_on: string | null;
    decided_by: User | null;
};
export type CreateRoleAssignment2 = {
    user_id: string;
    role_id: string;
};
export type ModifyRoleAssignment2 = {
    role_id: string;
};
export type DatasetStatus = 'pending' | 'active' | 'archived';
export type DatasetAccessType = 'public' | 'restricted' | 'private';
export type Dataset = {
    id: string;
    name: string;
    namespace: string;
    description: string;
    status: DatasetStatus;
    access_type: DatasetAccessType;
};
export type RoleAssignmentResponse3 = {
    id: string;
    dataset: Dataset;
    user: User;
    role: Role | null;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: User | null;
    decided_on: string | null;
    decided_by: User | null;
};
export type CreateRoleAssignment3 = {
    user_id: string;
    role_id: string;
};
export type ModifyRoleAssignment3 = {
    role_id: string;
};
export const {
    useListAssignmentsApiRoleAssignmentsGlobalGetQuery,
    useLazyListAssignmentsApiRoleAssignmentsGlobalGetQuery,
    useCreateAssignmentApiRoleAssignmentsGlobalPostMutation,
    useDeleteAssignmentApiRoleAssignmentsGlobalIdDeleteMutation,
    useDecideAssignmentApiRoleAssignmentsGlobalIdDecidePatchMutation,
    useModifyAssignedRoleApiRoleAssignmentsGlobalIdRolePatchMutation,
    useListAssignmentsApiRoleAssignmentsDataProductGetQuery,
    useLazyListAssignmentsApiRoleAssignmentsDataProductGetQuery,
    useCreateAssignmentApiRoleAssignmentsDataProductIdPostMutation,
    useDeleteAssignmentApiRoleAssignmentsDataProductIdDeleteMutation,
    useModifyAssignedRoleApiRoleAssignmentsDataProductIdPatchMutation,
    useRequestAssignmentApiRoleAssignmentsDataProductRequestIdPostMutation,
    useDecideAssignmentApiRoleAssignmentsDataProductIdDecidePatchMutation,
    useListAssignmentsApiRoleAssignmentsDatasetGetQuery,
    useLazyListAssignmentsApiRoleAssignmentsDatasetGetQuery,
    useCreateAssignmentApiRoleAssignmentsDatasetIdPostMutation,
    useDeleteAssignmentApiRoleAssignmentsDatasetIdDeleteMutation,
    useModifyAssignedRoleApiRoleAssignmentsDatasetIdPatchMutation,
    useRequestAssignmentApiRoleAssignmentsDatasetRequestIdPostMutation,
    useDecideAssignmentApiRoleAssignmentsDatasetIdDecidePatchMutation,
} = injectedRtkApi;
