import { DataOutputContract } from '@/types/data-output';

export type DataOutputsGetContract = (Omit<DataOutputContract, 'owner' | 'configuration'> & {
    owner_id: string;
    configuration_type: string;
})[];
