import { api } from "@/store/api/services/generated/dataProductsOutputPortsDataQualityApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getExplorations: build.query<
      GetExplorationsApiResponse,
      GetExplorationsApiArg
    >({
      query: () => ({ url: `/api/v2/explorations` }),
    }),
    createExploration: build.mutation<
      CreateExplorationApiResponse,
      CreateExplorationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/explorations`,
        method: "POST",
        body: queryArg,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetExplorationsApiResponse =
  /** status 200 Successful Response */ GetExplorationsResponse;
export type GetExplorationsApiArg = void;
export type CreateExplorationApiResponse =
  /** status 200 Successful Response */ CreateExplorationResponse;
export type CreateExplorationApiArg = CreateExplorationRequest;
export type Domain = {
  id: string;
  name: string;
  description: string;
};
export type Exploration = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  domain: Domain;
};
export type GetExplorationsResponse = {
  explorations: Exploration[];
};
export type CreateExplorationResponse = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  domain: Domain;
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
export type CreateExplorationRequest = {
  name: string;
  namespace: string;
  description: string;
  domain_id: string;
};
export const {
  useGetExplorationsQuery,
  useLazyGetExplorationsQuery,
  useCreateExplorationMutation,
} = injectedRtkApi;
