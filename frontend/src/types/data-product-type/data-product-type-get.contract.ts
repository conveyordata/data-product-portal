import { DataProductTypeContract } from '@/types/data-product-type';

import { DataProductContract } from '../data-product';

export type DataProductTypesGetContract = DataProductTypeContract & {
    data_product_count: number;
};
export type DataProductTypeGetContract = DataProductTypeContract & {
    data_products: DataProductContract[];
};
