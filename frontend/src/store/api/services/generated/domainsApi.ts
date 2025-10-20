import { api } from '@/store/api/services/generated/dataOutputsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getDomainsApiDomainsGet: build.query<GetDomainsApiDomainsGetApiResponse, GetDomainsApiDomainsGetApiArg>({
            query: () => ({ url: '/api/domains' }),
        }),
        createDomainApiDomainsPost: build.mutation<
            CreateDomainApiDomainsPostApiResponse,
            CreateDomainApiDomainsPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/domains',
                method: 'POST',
                body: queryArg.domainCreate,
            }),
        }),
        getDomainApiDomainsIdGet: build.query<GetDomainApiDomainsIdGetApiResponse, GetDomainApiDomainsIdGetApiArg>({
            query: (queryArg) => ({ url: `/api/domains/${queryArg.id}` }),
        }),
        updateDomainApiDomainsIdPut: build.mutation<
            UpdateDomainApiDomainsIdPutApiResponse,
            UpdateDomainApiDomainsIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/domains/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.domainUpdate,
            }),
        }),
        removeDomainApiDomainsIdDelete: build.mutation<
            RemoveDomainApiDomainsIdDeleteApiResponse,
            RemoveDomainApiDomainsIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/domains/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
        migrateDomainApiDomainsMigrateFromIdToIdPut: build.mutation<
            MigrateDomainApiDomainsMigrateFromIdToIdPutApiResponse,
            MigrateDomainApiDomainsMigrateFromIdToIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/domains/migrate/${queryArg.fromId}/${queryArg.toId}`,
                method: 'PUT',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDomainsApiDomainsGetApiResponse = /** status 200 Successful Response */ DomainsGet[];
export type GetDomainsApiDomainsGetApiArg = void;
export type CreateDomainApiDomainsPostApiResponse = /** status 200 Domain successfully created */ {
    [key: string]: string;
};
export type CreateDomainApiDomainsPostApiArg = {
    domainCreate: DomainCreate;
};
export type GetDomainApiDomainsIdGetApiResponse = /** status 200 Successful Response */ DomainGet;
export type GetDomainApiDomainsIdGetApiArg = {
    id: string;
};
export type UpdateDomainApiDomainsIdPutApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type UpdateDomainApiDomainsIdPutApiArg = {
    id: string;
    domainUpdate: DomainUpdate;
};
export type RemoveDomainApiDomainsIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveDomainApiDomainsIdDeleteApiArg = {
    id: string;
};
export type MigrateDomainApiDomainsMigrateFromIdToIdPutApiResponse = /** status 200 Successful Response */ any;
export type MigrateDomainApiDomainsMigrateFromIdToIdPutApiArg = {
    fromId: string;
    toId: string;
};
export type DomainsGet = {
    id: string;
    name: string;
    description: string;
    data_product_count: number;
    dataset_count: number;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type DomainCreate = {
    name: string;
    description: string;
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
export type DomainGet = {
    id: string;
    name: string;
    description: string;
    data_products: DataProduct[];
    datasets: Dataset[];
};
export type DomainUpdate = {
    name: string;
    description: string;
};
export const {
    useGetDomainsApiDomainsGetQuery,
    useLazyGetDomainsApiDomainsGetQuery,
    useCreateDomainApiDomainsPostMutation,
    useGetDomainApiDomainsIdGetQuery,
    useLazyGetDomainApiDomainsIdGetQuery,
    useUpdateDomainApiDomainsIdPutMutation,
    useRemoveDomainApiDomainsIdDeleteMutation,
    useMigrateDomainApiDomainsMigrateFromIdToIdPutMutation,
} = injectedRtkApi;
