import { api } from '@/store/api/services/generated/mcpApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({}),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export const {} = injectedRtkApi;
