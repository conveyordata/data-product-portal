import { DataOutputContract } from '@/types/data-output';

export type DataOutputsGetContract = (DataOutputContract & {
    owner_id: string;
    //configuration_type: string;
})[];
