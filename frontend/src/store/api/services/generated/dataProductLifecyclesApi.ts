import { api } from '@/store/api/services/generated/dataProductTypesApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getDataProductsLifecyclesApiDataProductLifecyclesGet: build.query<
            GetDataProductsLifecyclesApiDataProductLifecyclesGetApiResponse,
            GetDataProductsLifecyclesApiDataProductLifecyclesGetApiArg
        >({
            query: () => ({ url: '/api/data_product_lifecycles' }),
        }),
        createDataProductLifecycleApiDataProductLifecyclesPost: build.mutation<
            CreateDataProductLifecycleApiDataProductLifecyclesPostApiResponse,
            CreateDataProductLifecycleApiDataProductLifecyclesPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_product_lifecycles',
                method: 'POST',
                body: queryArg.dataProductLifeCycleCreate,
            }),
        }),
        updateDataProductLifecycleApiDataProductLifecyclesIdPut: build.mutation<
            UpdateDataProductLifecycleApiDataProductLifecyclesIdPutApiResponse,
            UpdateDataProductLifecycleApiDataProductLifecyclesIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_lifecycles/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.dataProductLifeCycleUpdate,
            }),
        }),
        deleteDataProductLifecycleApiDataProductLifecyclesIdDelete: build.mutation<
            DeleteDataProductLifecycleApiDataProductLifecyclesIdDeleteApiResponse,
            DeleteDataProductLifecycleApiDataProductLifecyclesIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_lifecycles/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductsLifecyclesApiDataProductLifecyclesGetApiResponse =
    /** status 200 Successful Response */ DataProductLifeCyclesGet[];
export type GetDataProductsLifecyclesApiDataProductLifecyclesGetApiArg = void;
export type CreateDataProductLifecycleApiDataProductLifecyclesPostApiResponse =
    /** status 200 Data Product successfully created */ {
        [key: string]: string;
    };
export type CreateDataProductLifecycleApiDataProductLifecyclesPostApiArg = {
    dataProductLifeCycleCreate: DataProductLifeCycleCreate;
};
export type UpdateDataProductLifecycleApiDataProductLifecyclesIdPutApiResponse =
    /** status 200 Data Product lifecycle updated */ {
        [key: string]: string;
    };
export type UpdateDataProductLifecycleApiDataProductLifecyclesIdPutApiArg = {
    id: string;
    dataProductLifeCycleUpdate: DataProductLifeCycleUpdate;
};
export type DeleteDataProductLifecycleApiDataProductLifecyclesIdDeleteApiResponse =
    /** status 200 Successful Response */ any;
export type DeleteDataProductLifecycleApiDataProductLifecyclesIdDeleteApiArg = {
    id: string;
};
export type DataProductLifeCyclesGet = {
    id: string;
    value: number;
    name: string;
    color: string;
    is_default: boolean;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type DataProductLifeCycleCreate = {
    value: number;
    name: string;
    color: string;
    is_default?: boolean;
};
export type DataProductLifeCycleUpdate = {
    value: number;
    name: string;
    color: string;
    is_default?: boolean;
};
export const {
    useGetDataProductsLifecyclesApiDataProductLifecyclesGetQuery,
    useLazyGetDataProductsLifecyclesApiDataProductLifecyclesGetQuery,
    useCreateDataProductLifecycleApiDataProductLifecyclesPostMutation,
    useUpdateDataProductLifecycleApiDataProductLifecyclesIdPutMutation,
    useDeleteDataProductLifecycleApiDataProductLifecyclesIdDeleteMutation,
} = injectedRtkApi;
