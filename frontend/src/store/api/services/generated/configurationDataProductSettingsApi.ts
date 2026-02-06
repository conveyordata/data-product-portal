import { api } from "@/store/api/services/generated/configurationDataProductLifecyclesApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getDataProductsSettings: build.query<
      GetDataProductsSettingsApiResponse,
      GetDataProductsSettingsApiArg
    >({
      query: () => ({ url: `/api/v2/configuration/data_product_settings` }),
    }),
    createDataProductSetting: build.mutation<
      CreateDataProductSettingApiResponse,
      CreateDataProductSettingApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_settings`,
        method: "POST",
        body: queryArg,
      }),
    }),
    getDataProductSettingsNamespaceSuggestion: build.query<
      GetDataProductSettingsNamespaceSuggestionApiResponse,
      GetDataProductSettingsNamespaceSuggestionApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_settings/namespace_suggestion`,
        params: {
          name: queryArg,
        },
      }),
    }),
    validateDataProductSettingsNamespace: build.query<
      ValidateDataProductSettingsNamespaceApiResponse,
      ValidateDataProductSettingsNamespaceApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_settings/validate_namespace`,
        params: {
          namespace: queryArg["namespace"],
          scope: queryArg.scope,
        },
      }),
    }),
    getDataProductSettingsNamespaceLengthLimits: build.query<
      GetDataProductSettingsNamespaceLengthLimitsApiResponse,
      GetDataProductSettingsNamespaceLengthLimitsApiArg
    >({
      query: () => ({
        url: `/api/v2/configuration/data_product_settings/namespace_length_limits`,
      }),
    }),
    updateDataProductSetting: build.mutation<
      UpdateDataProductSettingApiResponse,
      UpdateDataProductSettingApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_settings/${queryArg.id}`,
        method: "PUT",
        body: queryArg.dataProductSettingUpdate,
      }),
    }),
    removeDataProductSetting: build.mutation<
      RemoveDataProductSettingApiResponse,
      RemoveDataProductSettingApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/configuration/data_product_settings/${queryArg}`,
        method: "DELETE",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductsSettingsApiResponse =
  /** status 200 Successful Response */ DataProductSettingsGet;
export type GetDataProductsSettingsApiArg = void;
export type CreateDataProductSettingApiResponse =
  /** status 200 Successful Response */ CreateDataProductSettingResponse;
export type CreateDataProductSettingApiArg = DataProductSettingCreate;
export type GetDataProductSettingsNamespaceSuggestionApiResponse =
  /** status 200 Successful Response */ NamespaceSuggestion;
export type GetDataProductSettingsNamespaceSuggestionApiArg = string;
export type ValidateDataProductSettingsNamespaceApiResponse =
  /** status 200 Successful Response */ NamespaceValidation;
export type ValidateDataProductSettingsNamespaceApiArg = {
  namespace: string;
  scope: DataProductSettingScope;
};
export type GetDataProductSettingsNamespaceLengthLimitsApiResponse =
  /** status 200 Successful Response */ NamespaceLengthLimits;
export type GetDataProductSettingsNamespaceLengthLimitsApiArg = void;
export type UpdateDataProductSettingApiResponse =
  /** status 200 Successful Response */ UpdateDataProductSettingResponse;
export type UpdateDataProductSettingApiArg = {
  id: string;
  dataProductSettingUpdate: DataProductSettingUpdate;
};
export type RemoveDataProductSettingApiResponse =
  /** status 200 Successful Response */ any;
export type RemoveDataProductSettingApiArg = string;
export type DataProductSettingsGetItem = {
  id: string;
  category: string;
  type: DataProductSettingType;
  tooltip: string;
  namespace: string;
  name: string;
  default: string;
  order?: number;
  scope: DataProductSettingScope;
};
export type DataProductSettingsGet = {
  data_product_settings: DataProductSettingsGetItem[];
};
export type CreateDataProductSettingResponse = {
  id: string;
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
export type DataProductSettingCreate = {
  category: string;
  type: DataProductSettingType;
  tooltip: string;
  namespace: string;
  name: string;
  default: string;
  order?: number;
  scope: DataProductSettingScope;
};
export type NamespaceSuggestion = {
  namespace: string;
};
export type NamespaceValidation = {
  validity: ResourceNameValidityType;
};
export type NamespaceLengthLimits = {
  max_length: number;
};
export type UpdateDataProductSettingResponse = {
  id: string;
};
export type DataProductSettingUpdate = {
  category: string;
  type: DataProductSettingType;
  tooltip: string;
  namespace: string;
  name: string;
  default: string;
  order?: number;
  scope: DataProductSettingScope;
};
export enum DataProductSettingType {
  Checkbox = "checkbox",
  Tags = "tags",
  Input = "input",
}
export enum DataProductSettingScope {
  Dataproduct = "dataproduct",
  Dataset = "dataset",
}
export enum ResourceNameValidityType {
  Valid = "VALID",
  InvalidLength = "INVALID_LENGTH",
  InvalidCharacters = "INVALID_CHARACTERS",
  Duplicate = "DUPLICATE",
}
export const {
  useGetDataProductsSettingsQuery,
  useLazyGetDataProductsSettingsQuery,
  useCreateDataProductSettingMutation,
  useGetDataProductSettingsNamespaceSuggestionQuery,
  useLazyGetDataProductSettingsNamespaceSuggestionQuery,
  useValidateDataProductSettingsNamespaceQuery,
  useLazyValidateDataProductSettingsNamespaceQuery,
  useGetDataProductSettingsNamespaceLengthLimitsQuery,
  useLazyGetDataProductSettingsNamespaceLengthLimitsQuery,
  useUpdateDataProductSettingMutation,
  useRemoveDataProductSettingMutation,
} = injectedRtkApi;
