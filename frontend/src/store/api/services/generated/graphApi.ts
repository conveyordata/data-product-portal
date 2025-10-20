import { api } from '@/store/api/services/generated/themeSettingsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getGraphDataApiDatasetsIdGraphGet: build.query<
            GetGraphDataApiDatasetsIdGraphGetApiResponse,
            GetGraphDataApiDatasetsIdGraphGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/datasets/${queryArg.id}/graph`,
                params: {
                    level: queryArg.level,
                },
            }),
        }),
        getGraphDataApiDataProductsIdGraphGet: build.query<
            GetGraphDataApiDataProductsIdGraphGetApiResponse,
            GetGraphDataApiDataProductsIdGraphGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_products/${queryArg.id}/graph`,
                params: {
                    level: queryArg.level,
                },
            }),
        }),
        getGraphDataApiDataOutputsIdGraphGet: build.query<
            GetGraphDataApiDataOutputsIdGraphGetApiResponse,
            GetGraphDataApiDataOutputsIdGraphGetApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_outputs/${queryArg.id}/graph`,
                params: {
                    level: queryArg.level,
                },
            }),
        }),
        getGraphDataApiGraphGet: build.query<GetGraphDataApiGraphGetApiResponse, GetGraphDataApiGraphGetApiArg>({
            query: (queryArg) => ({
                url: '/api/graph',
                params: {
                    domain_nodes_enabled: queryArg.domainNodesEnabled,
                    data_product_nodes_enabled: queryArg.dataProductNodesEnabled,
                    dataset_nodes_enabled: queryArg.datasetNodesEnabled,
                    data_output_nodes_enabled: queryArg.dataOutputNodesEnabled,
                },
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetGraphDataApiDatasetsIdGraphGetApiResponse = /** status 200 Successful Response */ Graph;
export type GetGraphDataApiDatasetsIdGraphGetApiArg = {
    id: string;
    level?: number;
};
export type GetGraphDataApiDataProductsIdGraphGetApiResponse = /** status 200 Successful Response */ Graph;
export type GetGraphDataApiDataProductsIdGraphGetApiArg = {
    id: string;
    level?: number;
};
export type GetGraphDataApiDataOutputsIdGraphGetApiResponse = /** status 200 Successful Response */ Graph;
export type GetGraphDataApiDataOutputsIdGraphGetApiArg = {
    id: string;
    level?: number;
};
export type GetGraphDataApiGraphGetApiResponse = /** status 200 Successful Response */ Graph;
export type GetGraphDataApiGraphGetApiArg = {
    domainNodesEnabled?: boolean;
    dataProductNodesEnabled?: boolean;
    datasetNodesEnabled?: boolean;
    dataOutputNodesEnabled?: boolean;
};
export type Edge = {
    id: string;
    source: string;
    target: string;
    animated: boolean;
    sourceHandle?: string;
    targetHandle?: string;
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
export type RoleAssignment = {
    id: string;
    data_product: DataProduct;
    user: User;
    role: Role | null;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: User | null;
    decided_on: string | null;
    decided_by: User | null;
    data_product_id: string;
    user_id: string;
    role_id: string | null;
    requested_by_id: string | null;
    decided_by_id: string | null;
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
export type RoleAssignment2 = {
    id: string;
    dataset: Dataset;
    user: User;
    role: Role | null;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: User | null;
    decided_on: string | null;
    decided_by: User | null;
    dataset_id: string;
    user_id: string;
    role_id: string | null;
    requested_by_id: string | null;
    decided_by_id: string | null;
};
export type NodeData = {
    id: string;
    name: string;
    link_to_id?: string | null;
    icon_key?: string | null;
    domain?: string | null;
    domain_id?: string | null;
    description?: string | null;
    assignments?: (RoleAssignment | RoleAssignment2)[] | null;
};
export type NodeType = 'dataProductNode' | 'dataOutputNode' | 'datasetNode' | 'domainNode';
export type Node = {
    id: string;
    data: NodeData;
    type: NodeType;
    isMain?: boolean;
};
export type Graph = {
    edges: Edge[];
    nodes: Node[];
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export const {
    useGetGraphDataApiDatasetsIdGraphGetQuery,
    useLazyGetGraphDataApiDatasetsIdGraphGetQuery,
    useGetGraphDataApiDataProductsIdGraphGetQuery,
    useLazyGetGraphDataApiDataProductsIdGraphGetQuery,
    useGetGraphDataApiDataOutputsIdGraphGetQuery,
    useLazyGetGraphDataApiDataOutputsIdGraphGetQuery,
    useGetGraphDataApiGraphGetQuery,
    useLazyGetGraphDataApiGraphGetQuery,
} = injectedRtkApi;
