import { DataProductCreate, DataProductCreateResponse } from '@/types/data-product';

export type DataProductUpdateRequest = DataProductCreate;

export type DataProductUpdateResponse = DataProductCreateResponse;

export type DataProductUpdateFormSchema = DataProductUpdateRequest & {
    id: string;
};
