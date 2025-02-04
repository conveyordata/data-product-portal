import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import {
    DataProductSettingContract,
    DataProductSettingCreateRequest,
    DataProductSettingCreateResponse,
} from '@/types/data-product-setting';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import {
    DataProductSettingValueCreateRequest,
    DataProductSettingValueCreateResponse,
} from '@/types/data-product-setting/data-product-setting-create';

export const dataProductSettingTags: string[] = [TagTypes.DataProductSetting];
export const dataProductSettingsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductSettingTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            getAllDataProductSettings: builder.query<DataProductSettingContract[], void>({
                query: () => ({
                    url: ApiUrl.DataProductSetting,
                    method: 'GET',
                }),
                providesTags: (result = []) =>
                    result
                        ? [
                              { type: TagTypes.DataProductSetting as const, id: STATIC_TAG_ID.LIST },
                              ...result.map(({ id }) => ({ type: TagTypes.DataProductSetting as const, id })),
                          ]
                        : [{ type: TagTypes.DataProductSetting, id: STATIC_TAG_ID.LIST }],
            }),
            createDataProductSettingValue: builder.mutation<
                DataProductSettingValueCreateResponse,
                DataProductSettingValueCreateRequest
            >({
                query: (request) => ({
                    url: buildUrl(
                        buildUrl(ApiUrl.DataProductSettingValue, { dataProductId: request.data_product_id }),
                        { dataProductSettingId: request.data_product_settings_id },
                    ),
                    method: 'POST',
                    params: {
                        data_product_id: request.data_product_id,
                        setting_id: request.data_product_settings_id,
                        value: request.value,
                    },
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.DataProduct as const, id: arg.data_product_id },
                    { type: TagTypes.Dataset as const, id: arg.data_product_id },
                    { type: TagTypes.DataProductSetting, id: arg.data_product_settings_id },
                    { type: TagTypes.DataProductSetting, id: STATIC_TAG_ID.LIST },
                ],
            }),
            removeDataProductSetting: builder.mutation<void, string>({
                query: (id) => ({
                    url: buildUrl(ApiUrl.DataProductSettingGet, { settingId: id }),
                    method: 'DELETE',
                }),
                invalidatesTags: [{ type: TagTypes.DataProductSetting as const, id: STATIC_TAG_ID.LIST }],
            }),
            createDataProductSetting: builder.mutation<
                DataProductSettingCreateResponse,
                DataProductSettingCreateRequest
            >({
                query: (dataProductSetting) => ({
                    url: ApiUrl.DataProductSetting,
                    method: 'POST',
                    data: dataProductSetting,
                }),
                invalidatesTags: [{ type: TagTypes.DataProductSetting as const, id: STATIC_TAG_ID.LIST }],
            }),
            updateDataProductSetting: builder.mutation<DataProductSettingCreateResponse, DataProductSettingContract>({
                query: (dataProductSetting) => ({
                    url: buildUrl(ApiUrl.DataProductSettingGet, { settingId: dataProductSetting.id }),
                    method: 'PUT',
                    data: dataProductSetting,
                }),
                invalidatesTags: [{ type: TagTypes.DataProductSetting as const, id: STATIC_TAG_ID.LIST }],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useCreateDataProductSettingValueMutation,
    useRemoveDataProductSettingMutation,
    useUpdateDataProductSettingMutation,
    useCreateDataProductSettingMutation,
    useGetAllDataProductSettingsQuery,
} = dataProductSettingsApiSlice;
