import { api } from "@/store/api/services/generated/configurationDataProductSettingsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getDataProductType: build.query<
      GetDataProductTypeApiResponse,
      GetDataProductTypeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_types/${queryArg}`,
      }),
    }),
    updateDataProductType: build.mutation<
      UpdateDataProductTypeApiResponse,
      UpdateDataProductTypeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_types/${queryArg.id}`,
        method: "PUT",
        body: queryArg.dataProductTypeUpdate,
      }),
    }),
    removeDataProductType: build.mutation<
      RemoveDataProductTypeApiResponse,
      RemoveDataProductTypeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_types/${queryArg}`,
        method: "DELETE",
      }),
    }),
    getDataProductsTypes: build.query<
      GetDataProductsTypesApiResponse,
      GetDataProductsTypesApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/data_product_types` }),
    }),
    createDataProductType: build.mutation<
      CreateDataProductTypeApiResponse,
      CreateDataProductTypeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_types`,
        method: "POST",
        body: queryArg,
      }),
    }),
    migrateDataProductType: build.mutation<
      MigrateDataProductTypeApiResponse,
      MigrateDataProductTypeApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_types/migrate/${queryArg.fromId}/${queryArg.toId}`,
        method: "PUT",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductTypeApiResponse =
  /** status 200 Successful Response */ DataProductTypeGet;
export type GetDataProductTypeApiArg = string;
export type UpdateDataProductTypeApiResponse =
  /** status 200 Successful Response */ UpdateDataProductTypeResponse;
export type UpdateDataProductTypeApiArg = {
  id: string;
  dataProductTypeUpdate: DataProductTypeUpdate;
};
export type RemoveDataProductTypeApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveDataProductTypeApiArg = string;
export type GetDataProductsTypesApiResponse =
  /** status 200 Successful Response */ DataProductTypesGet;
export type GetDataProductsTypesApiArg = void;
export type CreateDataProductTypeApiResponse =
  /** status 200 Data Product successfully created */ CreateDataProductTypeResponse;
export type CreateDataProductTypeApiArg = DataProductTypeCreate;
export type MigrateDataProductTypeApiResponse =
  /** status 200 Successful Response */ any;
export type MigrateDataProductTypeApiArg = {
  fromId: string;
  toId: string;
};
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
export type UpdateDataProductTypeResponse = {
  id: string;
};
export type DataProductTypeUpdate = {
  name: string;
  description: string;
  icon_key: DataProductIconKey;
};
export type DataProductTypesGetItem = {
  id: string;
  name: string;
  description: string;
  icon_key: DataProductIconKey;
  data_product_count: number;
};
export type DataProductTypesGet = {
  data_product_types: DataProductTypesGetItem[];
};
export type CreateDataProductTypeResponse = {
  id: string;
};
export type DataProductTypeCreate = {
  name: string;
  description: string;
  icon_key: DataProductIconKey;
};
export enum DataProductIconKey {
  Reporting = "reporting",
  Processing = "processing",
  Exploration = "exploration",
  Ingestion = "ingestion",
  MachineLearning = "machine_learning",
  Analytics = "analytics",
  Default = "default",
}
export enum DataProductStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export const {
  useGetDataProductTypeQuery,
  useLazyGetDataProductTypeQuery,
  useUpdateDataProductTypeMutation,
  useRemoveDataProductTypeMutation,
  useGetDataProductsTypesQuery,
  useLazyGetDataProductsTypesQuery,
  useCreateDataProductTypeMutation,
  useMigrateDataProductTypeMutation,
} = injectedRtkApi;
