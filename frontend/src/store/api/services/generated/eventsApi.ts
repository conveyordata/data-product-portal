import { api } from '@/store/api/services/generated/pendingActionsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getLatestEventTimestampApiEventsLatestGet: build.query<
            GetLatestEventTimestampApiEventsLatestGetApiResponse,
            GetLatestEventTimestampApiEventsLatestGetApiArg
        >({
            query: () => ({ url: '/api/events/latest' }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetLatestEventTimestampApiEventsLatestGetApiResponse = /** status 200 Successful Response */ string | null;
export type GetLatestEventTimestampApiEventsLatestGetApiArg = void;
export const {
    useGetLatestEventTimestampApiEventsLatestGetQuery,
    useLazyGetLatestEventTimestampApiEventsLatestGetQuery,
} = injectedRtkApi;
