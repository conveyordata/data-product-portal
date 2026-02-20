import { api } from "@/store/api/services/generated/usersNotificationsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getDataProductsLifecycles: build.query<
      GetDataProductsLifecyclesApiResponse,
      GetDataProductsLifecyclesApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/data_product_lifecycles` }),
    }),
    createDataProductLifecycle: build.mutation<
      CreateDataProductLifecycleApiResponse,
      CreateDataProductLifecycleApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_lifecycles`,
        method: "POST",
        body: queryArg,
      }),
    }),
    updateDataProductLifecycle: build.mutation<
      UpdateDataProductLifecycleApiResponse,
      UpdateDataProductLifecycleApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_lifecycles/${queryArg.id}`,
        method: "PUT",
        body: queryArg.dataProductLifeCycleUpdate,
      }),
    }),
    removeDataProductLifecycle: build.mutation<
      RemoveDataProductLifecycleApiResponse,
      RemoveDataProductLifecycleApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_lifecycles/${queryArg}`,
        method: "DELETE",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductsLifecyclesApiResponse =
  /** status 200 Successful Response */ DataProductLifeCyclesGet;
export type GetDataProductsLifecyclesApiArg = void;
export type CreateDataProductLifecycleApiResponse =
  /** status 200 Data Product successfully created */ CreateDataProductLifeCycleResponse;
export type CreateDataProductLifecycleApiArg = DataProductLifeCycleCreate;
export type UpdateDataProductLifecycleApiResponse =
  /** status 200 Data Product lifecycle updated */ UpdateDataProductLifeCycleResponse;
export type UpdateDataProductLifecycleApiArg = {
  id: string;
  dataProductLifeCycleUpdate: DataProductLifeCycleUpdate;
};
export type RemoveDataProductLifecycleApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveDataProductLifecycleApiArg = string;
export type DataProductLifeCyclesGetItem = {
  id: string;
  value: number;
  name: string;
  color: string;
  is_default: boolean;
};
export type DataProductLifeCyclesGet = {
  data_product_life_cycles: DataProductLifeCyclesGetItem[];
};
export type CreateDataProductLifeCycleResponse = {
  id: string;
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
export type DataProductLifeCycleCreate = {
  value: number;
  name: string;
  color: string;
  is_default?: boolean;
};
export type UpdateDataProductLifeCycleResponse = {
  id: string;
};
export type DataProductLifeCycleUpdate = {
  value: number;
  name: string;
  color: string;
  is_default?: boolean;
};
export const {
  useGetDataProductsLifecyclesQuery,
  useLazyGetDataProductsLifecyclesQuery,
  useCreateDataProductLifecycleMutation,
  useUpdateDataProductLifecycleMutation,
  useRemoveDataProductLifecycleMutation,
} = injectedRtkApi;
