import { DataProductContract } from "../data-product";

export type DataProductSettingType =
    | 'checkbox'

export interface DataProductSettingContract {
    id: string;
    name: string;
    tooltip: string;
    default: string;
    type: DataProductSettingType;
    divider: string;
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
