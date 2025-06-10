import type { DatasetCreateRequest, DatasetCreateResponse } from '@/types/dataset';

export type DatasetUpdateRequest = Omit<DatasetCreateRequest, 'owners'>;

export type DatasetUpdateResponse = DatasetCreateResponse;

export type DatasetUpdateFormSchema = DatasetUpdateRequest & {
    id: string;
};
