import { api } from '@/store/api/services/generated/dataProductsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getDataProductsTypesApiDataProductTypesGet: build.query<
            GetDataProductsTypesApiDataProductTypesGetApiResponse,
            GetDataProductsTypesApiDataProductTypesGetApiArg
        >({
            query: () => ({ url: '/api/data_product_types' }),
        }),
        createDataProductTypeApiDataProductTypesPost: build.mutation<
            CreateDataProductTypeApiDataProductTypesPostApiResponse,
            CreateDataProductTypeApiDataProductTypesPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_product_types',
                method: 'POST',
                body: queryArg.dataProductTypeCreate,
            }),
        }),
        getDataProductTypeApiDataProductTypesIdGet: build.query<
            GetDataProductTypeApiDataProductTypesIdGetApiResponse,
            GetDataProductTypeApiDataProductTypesIdGetApiArg
        >({
            query: (queryArg) => ({ url: `/api/data_product_types/${queryArg.id}` }),
        }),
        updateDataProductTypeApiDataProductTypesIdPut: build.mutation<
            UpdateDataProductTypeApiDataProductTypesIdPutApiResponse,
            UpdateDataProductTypeApiDataProductTypesIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_types/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.dataProductTypeUpdate,
            }),
        }),
        removeDataProductTypeApiDataProductTypesIdDelete: build.mutation<
            RemoveDataProductTypeApiDataProductTypesIdDeleteApiResponse,
            RemoveDataProductTypeApiDataProductTypesIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_types/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
        migrateDataProductTypeApiDataProductTypesMigrateFromIdToIdPut: build.mutation<
            MigrateDataProductTypeApiDataProductTypesMigrateFromIdToIdPutApiResponse,
            MigrateDataProductTypeApiDataProductTypesMigrateFromIdToIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_types/migrate/${queryArg.fromId}/${queryArg.toId}`,
                method: 'PUT',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductsTypesApiDataProductTypesGetApiResponse =
    /** status 200 Successful Response */ DataProductTypesGet[];
export type GetDataProductsTypesApiDataProductTypesGetApiArg = void;
export type CreateDataProductTypeApiDataProductTypesPostApiResponse =
    /** status 200 Data Product successfully created */ {
        [key: string]: string;
    };
export type CreateDataProductTypeApiDataProductTypesPostApiArg = {
    dataProductTypeCreate: DataProductTypeCreate;
};
export type GetDataProductTypeApiDataProductTypesIdGetApiResponse =
    /** status 200 Successful Response */ DataProductTypeGet;
export type GetDataProductTypeApiDataProductTypesIdGetApiArg = {
    id: string;
};
export type UpdateDataProductTypeApiDataProductTypesIdPutApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type UpdateDataProductTypeApiDataProductTypesIdPutApiArg = {
    id: string;
    dataProductTypeUpdate: DataProductTypeUpdate;
};
export type RemoveDataProductTypeApiDataProductTypesIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveDataProductTypeApiDataProductTypesIdDeleteApiArg = {
    id: string;
};
export type MigrateDataProductTypeApiDataProductTypesMigrateFromIdToIdPutApiResponse =
    /** status 200 Successful Response */ any;
export type MigrateDataProductTypeApiDataProductTypesMigrateFromIdToIdPutApiArg = {
    fromId: string;
    toId: string;
};
export type DataProductIconKey =
    | 'reporting'
    | 'processing'
    | 'exploration'
    | 'ingestion'
    | 'machine_learning'
    | 'analytics'
    | 'default';
export type DataProductTypesGet = {
    id: string;
    name: string;
    description: string;
    icon_key: DataProductIconKey;
    data_product_count: number;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type DataProductTypeCreate = {
    name: string;
    description: string;
    icon_key: DataProductIconKey;
};
export type DataProductStatus = 'pending' | 'active' | 'archived';
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
export type DataProductTypeGet = {
    id: string;
    name: string;
    description: string;
    icon_key: DataProductIconKey;
    data_products: DataProduct[];
};
export type DataProductTypeUpdate = {
    name: string;
    description: string;
    icon_key: DataProductIconKey;
};
export const {
    useGetDataProductsTypesApiDataProductTypesGetQuery,
    useLazyGetDataProductsTypesApiDataProductTypesGetQuery,
    useCreateDataProductTypeApiDataProductTypesPostMutation,
    useGetDataProductTypeApiDataProductTypesIdGetQuery,
    useLazyGetDataProductTypeApiDataProductTypesIdGetQuery,
    useUpdateDataProductTypeApiDataProductTypesIdPutMutation,
    useRemoveDataProductTypeApiDataProductTypesIdDeleteMutation,
    useMigrateDataProductTypeApiDataProductTypesMigrateFromIdToIdPutMutation,
} = injectedRtkApi;
