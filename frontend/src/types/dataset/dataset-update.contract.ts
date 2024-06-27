import { DatasetCreateRequest, DatasetCreateResponse } from '@/types/dataset';

export type DatasetUpdateRequest = DatasetCreateRequest;

export type DatasetUpdateResponse = DatasetCreateResponse;

export type DatasetUpdateFormSchema = DatasetUpdateRequest & {
    id: string;
};
