import type { DataProductSettingContract } from '@/types/data-product-setting';

export type DataProductSettingValueCreateRequest = {
    data_product_id: string;
    data_product_settings_id: string;
    value: string;
};
export type DataProductSettingValueCreateResponse = DataProductSettingContract;

export type DataProductSettingCreateRequest = Omit<DataProductSettingContract, 'id'>;
export type DataProductSettingCreateResponse = DataProductSettingContract;
