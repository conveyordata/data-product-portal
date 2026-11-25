import { api } from "@/store/api/services/generated/resourceNamesApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    searchDataProducts: build.query<
      SearchDataProductsApiResponse,
      SearchDataProductsApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/search/data_products`,
        params: {
          query: queryArg.query,
          limit: queryArg.limit,
        },
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type SearchDataProductsApiResponse =
  /** status 200 Successful Response */ SearchDataProductsResponse;
export type SearchDataProductsApiArg = {
  query?: string;
  limit?: number;
};
export type Tag = {
  id: string;
  value: string;
};
export type Domain = {
  id: string;
  name: string;
  namespace: string;
  description: string;
};
export type DataProductType = {
  id: string;
  name: string;
  description: string;
  icon_key: DataProductIconKey;
};
export type DataProductLifeCycle = {
  id: string;
  name: string;
  value: number;
  color: string;
  is_default: boolean;
};
export type AccessMode = {
  id: string;
  name: string;
  description: string;
};
export type SearchDataProductsOutputPort = {
  id: string;
  name: string;
  description: string;
  access_modes: AccessMode[];
};
export type SearchDataProductsResponseItem = {
  id: string;
  name: string;
  description: string;
  tags: Tag[];
  domain: Domain;
  type: DataProductType;
  lifecycle: DataProductLifeCycle | null;
  output_ports: SearchDataProductsOutputPort[];
  consumer_count: number;
};
export type SearchDataProductsResponse = {
  data_products: SearchDataProductsResponseItem[];
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
export enum DataProductIconKey {
  Reporting = "reporting",
  Processing = "processing",
  Exploration = "exploration",
  Ingestion = "ingestion",
  MachineLearning = "machine_learning",
  Analytics = "analytics",
  Default = "default",
}
export const { useSearchDataProductsQuery, useLazySearchDataProductsQuery } =
  injectedRtkApi;
