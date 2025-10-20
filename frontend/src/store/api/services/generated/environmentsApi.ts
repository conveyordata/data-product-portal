import { api } from '@/store/api/services/generated/domainsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getEnvironmentsApiEnvsGet: build.query<GetEnvironmentsApiEnvsGetApiResponse, GetEnvironmentsApiEnvsGetApiArg>({
            query: () => ({ url: '/api/envs' }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetEnvironmentsApiEnvsGetApiResponse = /** status 200 Successful Response */ Environment[];
export type GetEnvironmentsApiEnvsGetApiArg = void;
export type Environment = {
    id: string;
    name: string;
    acronym: string;
    context: string;
    is_default?: boolean;
};
export const { useGetEnvironmentsApiEnvsGetQuery, useLazyGetEnvironmentsApiEnvsGetQuery } = injectedRtkApi;
