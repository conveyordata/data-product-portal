import { api } from "@/store/api/services/baseApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
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
  useGetDefaultAccessDurationQuery,
  useLazyGetDefaultAccessDurationQuery,
  useGetAllAccessDurationsQuery,
  useLazyGetAllAccessDurationsQuery,
  useUpdateAccessDurationMutation,
} = injectedRtkApi;
