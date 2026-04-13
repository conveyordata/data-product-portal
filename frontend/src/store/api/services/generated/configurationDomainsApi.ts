import { api } from "@/store/api/services/generated/configurationDataProductTypesApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getDomains: build.query<GetDomainsApiResponse, GetDomainsApiArg>({
      query: () => ({ url: `/api/v2/configuration/domains` }),
    }),
    createDomain: build.mutation<CreateDomainApiResponse, CreateDomainApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/configuration/domains`,
        method: "POST",
        body: queryArg,
      }),
    }),
    updateDomain: build.mutation<UpdateDomainApiResponse, UpdateDomainApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/configuration/domains/${queryArg.id}`,
        method: "PUT",
        body: queryArg.domainUpdate,
      }),
    }),
    removeDomain: build.mutation<RemoveDomainApiResponse, RemoveDomainApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/configuration/domains/${queryArg}`,
        method: "DELETE",
      }),
    }),
    getDomain: build.query<GetDomainApiResponse, GetDomainApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/configuration/domains/${queryArg}`,
      }),
    }),
    migrateDomain: build.mutation<
      MigrateDomainApiResponse,
      MigrateDomainApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/domains/migrate/${queryArg.fromId}/${queryArg.toId}`,
        method: "PUT",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDomainsApiResponse =
  /** status 200 Successful Response */ GetDomainsResponse;
export type GetDomainsApiArg = void;
export type CreateDomainApiResponse =
  /** status 200 Domain successfully created */ CreateDomainResponse;
export type CreateDomainApiArg = DomainCreate;
export type UpdateDomainApiResponse =
  /** status 200 Successful Response */ UpdateDomainResponse;
export type UpdateDomainApiArg = {
  id: string;
  domainUpdate: DomainUpdate;
};
export type RemoveDomainApiResponse = /** status 200 Successful Response */ any;
export type RemoveDomainApiArg = string;
export type GetDomainApiResponse =
  /** status 200 Successful Response */ GetDomainResponse;
export type GetDomainApiArg = string;
export type MigrateDomainApiResponse =
  /** status 200 Successful Response */ any;
export type MigrateDomainApiArg = {
  fromId: string;
  toId: string;
};
export type GetDomainsItem = {
  id: string;
  name: string;
  description: string;
  data_product_count: number;
};
export type GetDomainsResponse = {
  domains: GetDomainsItem[];
};
export type CreateDomainResponse = {
  id: string;
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
export type UpdateDomainResponse = {
  id: string;
};
export type DomainUpdate = {
  name: string;
  description: string;
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
export type GetDomainResponse = {
  id: string;
  name: string;
  description: string;
  data_products: DataProduct[];
};
export enum DataProductStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum DataProductIconKey {
  Reporting = "reporting",
  Processing = "processing",
  Exploration = "exploration",
  Ingestion = "ingestion",
  MachineLearning = "machine_learning",
  Analytics = "analytics",
  Default = "default",
}
export const {
  useGetDomainsQuery,
  useLazyGetDomainsQuery,
  useCreateDomainMutation,
  useUpdateDomainMutation,
  useRemoveDomainMutation,
  useGetDomainQuery,
  useLazyGetDomainQuery,
  useMigrateDomainMutation,
} = injectedRtkApi;
