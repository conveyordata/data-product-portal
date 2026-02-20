import { api } from "@/store/api/services/generated/graphApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getVersion: build.query<GetVersionApiResponse, GetVersionApiArg>({
      query: () => ({ url: `/api/v2/version` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetVersionApiResponse = /** status 200 Successful Response */ any;
export type GetVersionApiArg = void;
export const { useGetVersionQuery, useLazyGetVersionQuery } = injectedRtkApi;
