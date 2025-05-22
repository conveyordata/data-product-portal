import { DataProductContract } from '../data-product';

export type DataProductSettingType = 'checkbox' | 'tags' | 'input';
export type DataProductSettingScope = 'dataproduct' | 'dataset';

export interface DataProductSettingContract {
    order: number;
    id: string;
    namespace: string;
    name: string;
    tooltip: string;
    default: string;
    type: DataProductSettingType;
    category: string;
    scope: DataProductSettingScope;
}

export interface DataProductSettingModel extends DataProductSettingContract {}

export interface DataProductSettingValueContract {
    id: string;
    data_product: DataProductContract;
    data_product_id: string;
    data_product_setting: DataProductSettingContract;
    data_product_setting_id: string;
    value: string;
}

export interface DataProductSettingValueForm {
    [id: string]: string;
}

export interface CustomSettingValueContract {
    id: string;
    namespace: string;
    order: number;
    name: string;
    tooltip: string;
    default: string;
    type: DataProductSettingType;
    category: string;
    scope: DataProductSettingScope;
    value: string;
    is_default: boolean;
}
