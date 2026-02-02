// @ts-nocheck
import { api } from "@/store/api/services/generated/pluginsApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: () => ({}),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export const {} = injectedRtkApi;
