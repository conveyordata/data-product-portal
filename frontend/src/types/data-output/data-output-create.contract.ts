import { DataOutputContract } from './data-output.contract';

export type DataOutputCreate = Pick<DataOutputContract, 'name' | 'configuration' | 'description' | 'external_id'> & {
    owner_id: string;
};

export type DataOutputCreateFormSchema = DataOutputCreate & {
    owner: string;
};

export type DataOutputCreateResponse = {
    id: string;
};
