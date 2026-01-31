import { ApiUrl, buildUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types.ts';
import type {
    DataProductSettingValueCreateRequest,
    DataProductSettingValueCreateResponse,
} from '@/types/data-product-setting/data-product-setting-create';

export const dataProductSettingTags: string[] = [TagTypes.DataProductSetting];
export const dataProductSettingsApiSlice = baseApiSlice
    .enhanceEndpoints({ addTagTypes: dataProductSettingTags })
    .injectEndpoints({
        endpoints: (builder) => ({
            createDataProductSettingValue: builder.mutation<
                DataProductSettingValueCreateResponse,
                DataProductSettingValueCreateRequest
            >({
                query: (request) => ({
                    url: buildUrl(
                        buildUrl(ApiUrl.DataProductSettingValue, { dataProductId: request.data_product_id }),
                        { settingId: request.data_product_settings_id },
                    ),
                    method: 'POST',
                    params: {
                        value: request.value,
                    },
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.DataProduct as const, id: arg.data_product_id },
                    { type: TagTypes.DataProductSetting, id: arg.data_product_settings_id },
                    { type: TagTypes.DataProductSetting, id: STATIC_TAG_ID.LIST },
                ],
            }),
            createDatasetSettingValue: builder.mutation<
                DataProductSettingValueCreateResponse,
                DataProductSettingValueCreateRequest
            >({
                query: (request) => ({
                    url: buildUrl(buildUrl(ApiUrl.DatasetSettingValue, { datasetId: request.data_product_id }), {
                        settingId: request.data_product_settings_id,
                    }),
                    method: 'POST',
                    params: {
                        value: request.value,
                    },
                }),
                invalidatesTags: (_, _error, arg) => [
                    { type: TagTypes.Dataset as const, id: arg.data_product_id },
                    { type: TagTypes.DataProductSetting, id: arg.data_product_settings_id },
                    { type: TagTypes.DataProductSetting, id: STATIC_TAG_ID.LIST },
                ],
            }),
        }),
        overrideExisting: false,
    });

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useCreateDataProductSettingValueMutation, useCreateDatasetSettingValueMutation } =
    dataProductSettingsApiSlice;
