import type { DataProductCreate, DataProductCreateResponse } from '@/types/data-product';

export type DataProductUpdateRequest = Omit<DataProductCreate, 'owners'>;

export type DataProductUpdateResponse = DataProductCreateResponse;

export type DataProductUpdateFormSchema = DataProductUpdateRequest & {
    id: string;
};
