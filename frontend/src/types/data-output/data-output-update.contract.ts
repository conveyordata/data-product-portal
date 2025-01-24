import { DataOutputCreate, DataOutputCreateResponse } from './data-output-create.contract';

export type DataOutputUpdateRequest = Pick<DataOutputCreate, 'name' | 'description'>;

export type DataOutputUpdateResponse = DataOutputCreateResponse;

export type DataOutputUpdateFormSchema = DataOutputUpdateRequest & {
    id: string;
};
