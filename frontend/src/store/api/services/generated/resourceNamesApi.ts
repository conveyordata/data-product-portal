import { api } from "@/store/api/services/generated/dataProductsOutputPortsDataQualityApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    sanitizeResourceName: build.query<
      SanitizeResourceNameApiResponse,
      SanitizeResourceNameApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/resource_names/sanitize`,
        params: {
          name: queryArg,
        },
      }),
    }),
    validateResourceName: build.query<
      ValidateResourceNameApiResponse,
      ValidateResourceNameApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v2/resource_names/validate`,
        params: {
          resource_name: queryArg.resourceName,
          model: queryArg.model,
          data_product_id: queryArg.dataProductId,
        },
      }),
    }),
    resourceNameConstraints: build.query<
      ResourceNameConstraintsApiResponse,
      ResourceNameConstraintsApiArg
    >({
      query: () => ({ url: `/api/v2/resource_names/constraints` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type SanitizeResourceNameApiResponse =
  /** status 200 Successful Response */ ResourceNameSuggestion;
export type SanitizeResourceNameApiArg = string;
export type ValidateResourceNameApiResponse =
  /** status 200 Successful Response */ ResourceNameValidation;
export type ValidateResourceNameApiArg = {
  resourceName: string;
  model: ResourceNameModel;
  dataProductId?: string | null;
};
export type ResourceNameConstraintsApiResponse =
  /** status 200 Successful Response */ ResourceNameLengthLimits;
export type ResourceNameConstraintsApiArg = void;
export type ResourceNameSuggestion = {
  resource_name: string;
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
export type ResourceNameValidation = {
  validity: ResourceNameValidityType;
};
export type ResourceNameLengthLimits = {
  max_length: number;
};
export enum ResourceNameValidityType {
  Valid = "VALID",
  InvalidLength = "INVALID_LENGTH",
  InvalidCharacters = "INVALID_CHARACTERS",
  Duplicate = "DUPLICATE",
}
export enum ResourceNameModel {
  DataProduct = "data_product",
  TechnicalAsset = "technical_asset",
  OutputPort = "output_port",
  DataProductSetting = "data_product_setting",
  OutputPortSetting = "output_port_setting",
}
export const {
  useSanitizeResourceNameQuery,
  useLazySanitizeResourceNameQuery,
  useValidateResourceNameQuery,
  useLazyValidateResourceNameQuery,
  useResourceNameConstraintsQuery,
  useLazyResourceNameConstraintsQuery,
} = injectedRtkApi;
