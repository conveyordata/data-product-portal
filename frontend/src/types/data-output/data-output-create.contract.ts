import { DataOutputContract } from "./data-output.contract";

export type DataOutputCreate = Pick<DataOutputContract, 'name' | 'configuration'> & {
    external_id: string;
    owner_id: string;
};

export type DataOutputCreateFormSchema = DataOutputCreate & {
    owner: string;
};

export type DataOutputCreateResponse = {
    id: string;
};
