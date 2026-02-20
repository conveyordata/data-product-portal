import type { DataProductCreate } from '@/types/data-product';

export type DataProductUpdateRequest = Omit<DataProductCreate, 'owners'>;

export type DataProductUpdateFormSchema = DataProductUpdateRequest & {
    id: string;
};
