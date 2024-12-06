import { DataProductSettingContract } from '@/types/data-product-setting';

export type DataProductSettingCreateRequest = {
    data_product_id: string;
    data_product_settings_id: string;
    value: string;
}
export type DataProductSettingCreateResponse = DataProductSettingContract;
