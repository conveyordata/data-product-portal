import { api } from "@/store/api/services/baseApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    isTimeBoundAccessEnabled: build.query<
      IsTimeBoundAccessEnabledApiResponse,
      IsTimeBoundAccessEnabledApiArg
    >({
      query: () => ({ url: `/api/v2/access_durations/enabled` }),
    }),
    getExpiringSoonThreshold: build.query<
      GetExpiringSoonThresholdApiResponse,
      GetExpiringSoonThresholdApiArg
    >({
      query: () => ({
        url: `/api/v2/access_durations/expiring_soon_threshold`,
      }),
    }),
    getDefaultAccessDuration: build.query<
      GetDefaultAccessDurationApiResponse,
      GetDefaultAccessDurationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/access_durations/${queryArg}/default`,
      }),
    }),
    getAllAccessDurations: build.query<
      GetAllAccessDurationsApiResponse,
      GetAllAccessDurationsApiArg
    >({
      query: () => ({ url: `/api/v2/access_durations` }),
    }),
    updateAccessDuration: build.mutation<
      UpdateAccessDurationApiResponse,
      UpdateAccessDurationApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/access_durations/${queryArg.abstractDataProductType}`,
        method: "PUT",
        body: queryArg.accessDurationUpdate,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type IsTimeBoundAccessEnabledApiResponse =
  /** status 200 Successful Response */ TimeBoundAccessEnabledResponse;
export type IsTimeBoundAccessEnabledApiArg = void;
export type GetExpiringSoonThresholdApiResponse =
  /** status 200 Successful Response */ ExpiringSoonThresholdResponse;
export type GetExpiringSoonThresholdApiArg = void;
export type GetDefaultAccessDurationApiResponse =
  /** status 200 Successful Response */ AccessDuration;
export type GetDefaultAccessDurationApiArg = AbstractDataProductType;
export type GetAllAccessDurationsApiResponse =
  /** status 200 Successful Response */ AccessDuration[];
export type GetAllAccessDurationsApiArg = void;
export type UpdateAccessDurationApiResponse =
  /** status 200 Successful Response */ AccessDuration[];
export type UpdateAccessDurationApiArg = {
  abstractDataProductType: AbstractDataProductType;
  accessDurationUpdate: AccessDurationUpdate;
};
export type TimeBoundAccessEnabledResponse = {
  enabled: boolean;
};
export type ExpiringSoonThresholdResponse = {
  days: number;
};
export type AccessDuration = {
  id: string;
  abstract_data_product_type: AbstractDataProductType;
  access_duration_type: AccessDurationType;
  days: number | null;
  is_default: boolean;
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
export type AccessDurationUpdate = {
  access_duration_type: AccessDurationType;
  days?: number | null;
  alternative_allowed: boolean;
  alternative_days?: number | null;
};
export enum AbstractDataProductType {
  Unknown = "unknown",
  DataProducts = "data_products",
  Explorations = "explorations",
}
export enum AccessDurationType {
  Permanent = "permanent",
  TimeBound = "time_bound",
}
export const {
  useIsTimeBoundAccessEnabledQuery,
  useLazyIsTimeBoundAccessEnabledQuery,
  useGetExpiringSoonThresholdQuery,
  useLazyGetExpiringSoonThresholdQuery,
  useGetDefaultAccessDurationQuery,
  useLazyGetDefaultAccessDurationQuery,
  useGetAllAccessDurationsQuery,
  useLazyGetAllAccessDurationsQuery,
  useUpdateAccessDurationMutation,
} = injectedRtkApi;
