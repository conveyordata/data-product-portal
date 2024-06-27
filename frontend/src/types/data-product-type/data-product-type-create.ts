import { DataProductTypeContract } from '@/types/data-product-type';

export type DataProductTypeCreateRequest = Pick<DataProductTypeContract, 'name' | 'description'>;
export type DataProductTypeCreateResponse = DataProductTypeContract;
