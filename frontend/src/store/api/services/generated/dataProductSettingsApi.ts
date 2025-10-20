import { api } from '@/store/api/services/generated/dataProductLifecyclesApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getDataProductsSettingsApiDataProductSettingsGet: build.query<
            GetDataProductsSettingsApiDataProductSettingsGetApiResponse,
            GetDataProductsSettingsApiDataProductSettingsGetApiArg
        >({
            query: () => ({ url: '/api/data_product_settings' }),
        }),
        createDataProductSettingApiDataProductSettingsPost: build.mutation<
            CreateDataProductSettingApiDataProductSettingsPostApiResponse,
            CreateDataProductSettingApiDataProductSettingsPostApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_product_settings',
                method: 'POST',
                body: queryArg.dataProductSettingCreate,
            }),
        }),
        getDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGet: build.query<
            GetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetApiResponse,
            GetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_product_settings/namespace_suggestion',
                params: {
                    name: queryArg.name,
                },
            }),
        }),
        validateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGet: build.query<
            ValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetApiResponse,
            ValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetApiArg
        >({
            query: (queryArg) => ({
                url: '/api/data_product_settings/validate_namespace',
                params: {
                    namespace: queryArg['namespace'],
                    scope: queryArg.scope,
                },
            }),
        }),
        getDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGet: build.query<
            GetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetApiResponse,
            GetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetApiArg
        >({
            query: () => ({
                url: '/api/data_product_settings/namespace_length_limits',
            }),
        }),
        updateDataProductSettingApiDataProductSettingsIdPut: build.mutation<
            UpdateDataProductSettingApiDataProductSettingsIdPutApiResponse,
            UpdateDataProductSettingApiDataProductSettingsIdPutApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_settings/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.dataProductSettingUpdate,
            }),
        }),
        deleteDataProductSettingApiDataProductSettingsIdDelete: build.mutation<
            DeleteDataProductSettingApiDataProductSettingsIdDeleteApiResponse,
            DeleteDataProductSettingApiDataProductSettingsIdDeleteApiArg
        >({
            query: (queryArg) => ({
                url: `/api/data_product_settings/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetDataProductsSettingsApiDataProductSettingsGetApiResponse =
    /** status 200 Successful Response */ DataProductSettingsGet[];
export type GetDataProductsSettingsApiDataProductSettingsGetApiArg = void;
export type CreateDataProductSettingApiDataProductSettingsPostApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type CreateDataProductSettingApiDataProductSettingsPostApiArg = {
    dataProductSettingCreate: DataProductSettingCreate;
};
export type GetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetApiResponse =
    /** status 200 Successful Response */ NamespaceSuggestion;
export type GetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetApiArg = {
    name: string;
};
export type ValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetApiResponse =
    /** status 200 Successful Response */ NamespaceValidation;
export type ValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetApiArg = {
    namespace: string;
    scope: DataProductSettingScope;
};
export type GetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetApiResponse =
    /** status 200 Successful Response */ NamespaceLengthLimits;
export type GetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetApiArg = void;
export type UpdateDataProductSettingApiDataProductSettingsIdPutApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type UpdateDataProductSettingApiDataProductSettingsIdPutApiArg = {
    id: string;
    dataProductSettingUpdate: DataProductSettingUpdate;
};
export type DeleteDataProductSettingApiDataProductSettingsIdDeleteApiResponse =
    /** status 200 Successful Response */ any;
export type DeleteDataProductSettingApiDataProductSettingsIdDeleteApiArg = {
    id: string;
};
export type DataProductSettingType = 'checkbox' | 'tags' | 'input';
export type DataProductSettingScope = 'dataproduct' | 'dataset';
export type DataProductSettingsGet = {
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
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
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
export type NamespaceValidityType = 'VALID' | 'INVALID_LENGTH' | 'INVALID_CHARACTERS' | 'DUPLICATE_NAMESPACE';
export type NamespaceValidation = {
    validity: NamespaceValidityType;
};
export type NamespaceLengthLimits = {
    max_length: number;
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
export const {
    useGetDataProductsSettingsApiDataProductSettingsGetQuery,
    useLazyGetDataProductsSettingsApiDataProductSettingsGetQuery,
    useCreateDataProductSettingApiDataProductSettingsPostMutation,
    useGetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetQuery,
    useLazyGetDataProductSettingsNamespaceSuggestionApiDataProductSettingsNamespaceSuggestionGetQuery,
    useValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetQuery,
    useLazyValidateDataProductSettingsNamespaceApiDataProductSettingsValidateNamespaceGetQuery,
    useGetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetQuery,
    useLazyGetDataProductSettingsNamespaceLengthLimitsApiDataProductSettingsNamespaceLengthLimitsGetQuery,
    useUpdateDataProductSettingApiDataProductSettingsIdPutMutation,
    useDeleteDataProductSettingApiDataProductSettingsIdDeleteMutation,
} = injectedRtkApi;
